
"""
Step 3 (Commitment): The create_hash function creates the "Digital Seal" before training begins.

Step 4 (Tree Building): It reduces multiple WBAN node updates into a single Merkle Root, saving expensive blockchain storage.

Step 5 (The Proof): Instead of sending heavy raw data, get_merkle_path provides a "family tree" path that the Smart Contract uses to catch any tampering with just 3 or 4 small strings.

"""



import hashlib
import json

class MerkleUtils:
    @staticmethod
    def create_hash(data):
        """
        Step 3: Hash Commitment (The Digital Seal) [cite: 24]
        Converts any data (weights or sensor data) into a unique SHA-256 string[cite: 26].
        """
        # Convert data (like a list of weights) to a stable string for hashing
        data_string = json.dumps(str(data), sort_keys=True).encode()
        return hashlib.sha256(data_string).hexdigest()

    def build_merkle_tree(self, leaf_hashes):
        """
        Step 4: Merkle-PoR (The Secure Tree) [cite: 28]
        Takes a list of individual commitments and combines them into one Root[cite: 29].
        """
        if not leaf_hashes:
            return None
        
        # If there's an odd number of leaves, duplicate the last one to make it even
        if len(leaf_hashes) % 2 != 0:
            leaf_hashes.append(leaf_hashes[-1])

        tree = [leaf_hashes]
        current_level = leaf_hashes

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                # Combine pairs of hashes into a new hash
                combined = current_level[i] + current_level[i+1]
                next_level.append(self.create_hash(combined))
            
            # Pad if odd at higher levels
            if len(next_level) > 1 and len(next_level) % 2 != 0:
                next_level.append(next_level[-1])
                
            tree.append(next_level)
            current_level = next_level

        # The last level contains only the Merkle Root [cite: 31]
        return tree

    def get_merkle_root(self, tree):
        """
        Returns the single Master Seal to be stored on the Smart Contract[cite: 32].
        """
        return tree[-1][0] if tree else None

    def get_merkle_path(self, tree, leaf_index):
        """
        Step 5: Provide a 'Merkle Path' for the Audit [cite: 42, 43]
        Returns the small list of hashes needed to prove a leaf belongs to the Root[cite: 47].
        """
        path = []
        for level in range(len(tree) - 1):
            # Find the sibling of the current node
            if leaf_index % 2 == 0:
                sibling_index = leaf_index + 1
            else:
                sibling_index = leaf_index - 1
            
            # Add sibling to the path [cite: 46]
            path.append(tree[level][sibling_index])
            leaf_index //= 2
            
        return path

    def verify_proof(self, leaf_hash, path, root):
        """
        The Smart Contract Checks the Math [cite: 48, 49]
        Proves integrity without requiring the full dataset[cite: 43].
        """
        current_hash = leaf_hash
        for sibling_hash in path:
            # The order of hashing must match the tree building logic
            # Here we sort to ensure consistency (standard in simplified Merkle proofs)
            combined = "".join(sorted([current_hash, sibling_hash]))
            current_hash = self.create_hash(combined)
        
        # If the calculated path leads to the stored Root, it's a Success [cite: 50, 54]
        return current_hash == root