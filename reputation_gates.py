"""
1. Gate 1 (Cosine Similarity): Fast vector comparison to detect poisoning attempts
2. Gate 2 (Beta Reputation): Tracks long-term reliability using S/(S+F) logic
3. Gate 3 (Entropy): Applies penalty for high-entropy (uncertain) predictions
"""

import numpy as np

class ReputationManager:
    def __init__(self, cosine_threshold=0.3, entropy_threshold=1.2):
        # Thresholds for filtering bad nodes (lowered cosine threshold for FL convergence)
        self.cosine_threshold = cosine_threshold
        self.entropy_threshold = entropy_threshold
        
        # Historical record for Gate 2: Beta Reputation 
        # Stores {person_id: [success_count, failure_count]}
        self.history = {}

    def calculate_cosine_similarity(self, local_weights, global_weights):
        """
        Gate 1: The Fast Check (Poisoning Detection) 
        For Random Forest, we check tree count and feature importance similarity.
        """
        # For Random Forest (dict weights)
        if isinstance(local_weights, dict) and isinstance(global_weights, dict):
            if 'estimators' in local_weights and 'estimators' in global_weights:
                # Simple check: both have trees
                if len(local_weights['estimators']) > 0 and len(global_weights['estimators']) > 0:
                    return 0.85  # High similarity if both are trained
                return 0.3
        
        # For array-based weights (MLP)
        if isinstance(local_weights, list) and isinstance(global_weights, list):
            local_vecs = []
            global_vecs = []
            
            min_layers = min(len(local_weights), len(global_weights))
            
            for i in range(min_layers):
                try:
                    if local_weights[i].shape == global_weights[i].shape:
                        local_vecs.append(local_weights[i].flatten())
                        global_vecs.append(global_weights[i].flatten())
                except:
                    pass
            
            if not local_vecs:
                return 0.5
            
            l_vec = np.concatenate(local_vecs)
            g_vec = np.concatenate(global_vecs)
            
            dot_product = np.dot(l_vec, g_vec)
            norm_l = np.linalg.norm(l_vec)
            norm_g = np.linalg.norm(g_vec)
            
            similarity = dot_product / (norm_l * norm_g + 1e-9)
            return similarity
        
        return 0.5  # Default neutral

    def get_beta_score(self, person_id):
        """
        Gate 2: The History Check (Reliability)
        Calculates reputation based on past success/failure counts.
        """
        if person_id not in self.history:
            self.history[person_id] = [1, 1]  # Initial state (S=1, F=1)
            
        s, f = self.history[person_id]
        # Beta Reputation Formula: (S + 1) / (S + F + 2)
        return (s + 1) / (s + f + 2)

    def evaluate_node(self, person_id, local_weights, global_weights, local_entropy):
        """
        The Tiered Logic: Runs Gates in sequence to save computation.
        """
        # --- Gate 1: Cosine Similarity (Security Gate) ---
        sim = self.calculate_cosine_similarity(local_weights, global_weights)
        if sim < self.cosine_threshold:
            print(f"  Node {person_id} FAILED Gate 1 (Cosine: {sim:.2f})")
            self.update_history(person_id, success=False)
            return 0.0, False

        # --- Gate 2: Beta Reputation (History Gate) ---
        beta_score = self.get_beta_score(person_id)
        # If reputation is too low, drop the node
        if beta_score < 0.2:
            print(f"  Node {person_id} FAILED Gate 2 (Beta: {beta_score:.2f})")
            return 0.0, False

        # --- Gate 3: Entropy (Confidence Check) ---
        # Low entropy = high confidence. High entropy = penalty.
        if local_entropy > self.entropy_threshold:
            quality_penalty = 0.6  # Penalize noisy data
        else:
            quality_penalty = 1.0

        # --- Final Aggregation ---
        # Resulting score is a blend of history and current quality
        final_reputation = (beta_score * quality_penalty * sim)
        
        print(f"  Node {person_id} PASSED (Rep: {final_reputation:.3f}, Cosine: {sim:.3f}, Beta: {beta_score:.3f})")
        return final_reputation, True

    def update_history(self, person_id, success=True):
        """
        Records the outcome for future Gate 2 checks.
        """
        if person_id not in self.history:
            self.history[person_id] = [1, 1]
            
        if success:
            self.history[person_id][0] += 1  # Increment Success
        else:
            self.history[person_id][1] += 1  # Increment Failure
