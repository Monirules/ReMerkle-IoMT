import hashlib
from typing import List

class MerkleProof:
    """
    A simple implementation of a Merkle Tree for Proof of Learning.
    """

    @staticmethod
    def hash_data(data: str) -> str:
        """Helper to create a SHA256 hash of a string."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @staticmethod
    def build_merkle_tree(leaves: List[str]) -> List[str]:
        """
        Builds a Merkle Tree from a list of data items (leaves).
        Returns the list representing the tree levels, where the last item is the root.
        """
        if not leaves:
            return []

        # Hash all initial leaves
        current_level = [MerkleProof.hash_data(str(leaf)) for leaf in leaves]
        
        # If there's only one leaf, just return its hash as the root (and level)
        if len(current_level) == 1:
            return [current_level[0]]

        while len(current_level) > 1:
            next_level = []
            # Process pairs of nodes
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                if i + 1 < len(current_level):
                    right = current_level[i+1]
                else:
                    # If odd number of nodes, duplicate the last one
                    right = left
                
                # Combine and hash
                combined = left + right
                next_level.append(MerkleProof.hash_data(combined))
            
            # This implementation simplifies by not storing the full tree structure for proofs,
            # just calculating the root. For a full implementation, we'd store layers.
            # But for this simulation, we just need the root.
            current_level = next_level

        return current_level[0] # The Root

    @staticmethod
    def generate_proof_of_learning(loss: float, gradient_norm: float, accuracy: float, f1: float) -> dict:
        """
        Generates a Merkle Root for a specific training round's metadata.
        """
        # Data Layout: Loss, Gradient, Accuracy, F1
        data_points = [
            f"loss:{loss:.6f}",
            f"grad:{gradient_norm:.6f}",
            f"acc:{accuracy:.6f}",
            f"f1:{f1:.6f}"
        ]
        
        root = MerkleProof.build_merkle_tree(data_points)
        
        return {
            "root": root,
            "data": data_points
        }
