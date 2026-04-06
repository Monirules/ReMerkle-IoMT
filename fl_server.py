import numpy as np
import random
from reputation_gates import ReputationManager
from merkle_utils import MerkleUtils

class FederatedServer:
    def __init__(self, global_model_weights, num_classes, contract_address=None):
        """
        Initializes the Federated Server as the central aggregator and digital judge.
        """
        self.global_weights = global_model_weights
        self.num_classes = num_classes
        self.reputation_mgr = ReputationManager()
        self.merkle_utils = MerkleUtils()
        
        # --- Simulated Blockchain for WBAN ---
        self.contract_address = contract_address if contract_address else "0x" + "0"*40
        self.contract = None  # Simulated contract

    def aggregate_weights(self, client_updates):
        """
        Performs Federated Averaging for Random Forest by combining trees from all clients.
        """
        if not client_updates:
            return self.global_weights

        # For Random Forest, we combine all trees from all nodes
        all_estimators = []
        classes = None
        n_classes = None
        n_features_in = None
        
        for update in client_updates:
            if isinstance(update['weights'], dict) and 'estimators' in update['weights']:
                # Add trees from this client (weighted by reputation)
                # For simplicity, we take the trees proportional to reputation
                num_trees = max(1, int(len(update['weights']['estimators']) * update['reputation']))
                all_estimators.extend(update['weights']['estimators'][:num_trees])
                
                if classes is None:
                    classes = update['weights']['classes']
                    n_classes = update['weights']['n_classes']
                    n_features_in = update['weights']['n_features_in']
        
        # Limit total trees to avoid memory issues
        if len(all_estimators) > 200:
            # Sample trees to keep best diversity
            indices = np.random.choice(len(all_estimators), 200, replace=False)
            all_estimators = [all_estimators[i] for i in sorted(indices)]
        
        self.global_weights = {
            'estimators': all_estimators,
            'classes': classes,
            'n_classes': n_classes,
            'n_features_in': n_features_in
        }
        
        return self.global_weights

    def track_gas_costs(self, round_id, num_participants):
        """
        Tracks blockchain gas costs for Merkle-PoR vs traditional storage.
        """
        GAS_PER_STORAGE_SLOT = 20000 
        GAS_PER_HASH_OP = 60 
        
        # Merkle-PoR Cost: Storing 1 Root (32 bytes) + Verifying 1 Logarithmic Path
        merkle_storage_gas = GAS_PER_STORAGE_SLOT 
        audit_gas = np.log2(max(num_participants, 2)) * GAS_PER_HASH_OP
        total_merkle_gas = merkle_storage_gas + audit_gas

        # Traditional Cost: Storing all raw model coefficients on-chain
        traditional_gas = num_participants * (GAS_PER_STORAGE_SLOT * 10)

        return {
            'round': round_id,
            'merkle_gas': total_merkle_gas,
            'traditional_gas': traditional_gas,
            'savings_percentage': ((traditional_gas - total_merkle_gas) / traditional_gas) * 100
        }

    def run_round(self, round_id, participants):
        """
        Executes a full Federated Learning round with Tiered Gating and Blockchain Audits.
        """
        accepted_updates = []
        leaf_hashes = []

        print(f"\n--- Round {round_id} ---")

        # 1. Collect Commitments (Step 3: Hash Commitment)
        for p in participants:
            # Hash of local weights and quality entropy creates a digital seal
            commitment = self.merkle_utils.create_hash([str(p['weights']), p['entropy']])
            p['commitment'] = commitment
            leaf_hashes.append(commitment)

        # 2. Build Merkle Tree & Store Root on Smart Contract
        tree = self.merkle_utils.build_merkle_tree(leaf_hashes)
        root = self.merkle_utils.get_merkle_root(tree)
        
        # Step 4: Automate immutable storage of the Merkle Root
        print(f"[Blockchain] Merkle Root: {root[:10]}...")

        # 3. Process Tiered Gates (Gate 1: Cosine -> Gate 2: Beta -> Gate 3: Entropy)
        passed_count = 0
        for i, p in enumerate(participants):
            rep_score, passed = self.reputation_mgr.evaluate_node(
                p['id'], p['weights'], self.global_weights, p['entropy']
            )
            
            if passed:
                passed_count += 1
                # Reward the node for passing Gate 1 & 2
                self.reputation_mgr.update_history(p['id'], success=True) 
                
                # Step 5: Random Audit (20% chance)
                if random.random() < 0.2:
                    path = self.merkle_utils.get_merkle_path(tree, i) 
                    is_honest = self.merkle_utils.verify_proof(p['commitment'], path, root) 
                    
                    if is_honest:
                        # Bonus reputation for passing audit
                        self.reputation_mgr.update_history(p['id'], success=True)
                        print(f"  Node {p['id']}: ✓ Passed audit")
                    else:
                        # CRITICAL: Punishment for tampering
                        self.reputation_mgr.update_history(p['id'], success=False)
                        print(f"  Node {p['id']}: ✗ Failed audit - DROPPED")
                        continue

                accepted_updates.append({'weights': p['weights'], 'reputation': rep_score})
            else:
                # Gate Failure: Penalty applied to Beta Reputation
                self.reputation_mgr.update_history(p['id'], success=False)

        print(f"Accepted: {passed_count}/{len(participants)} nodes")

        # 5. Global Aggregation: Update central model with trusted data
        if accepted_updates:
            self.global_weights = self.aggregate_weights(accepted_updates)
        
        return self.global_weights
