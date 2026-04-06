// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title WBAN_FL_Audit
 * @dev Automates reputation management and Merkle-PoR audits for Federated Learning.
 */
contract WBAN_FL_Audit {
    
    // Structure to track node reputation history (Gate 2: Beta Reputation) [cite: 16]
    struct NodeReputation {
        uint256 successes;
        uint256 failures;
        bool isBlacklisted;
    }

    // Mapping to store the Merkle Root for each round (Step 4) [cite: 31, 32]
    mapping(uint256 => bytes32) public roundMerkleRoots;
    
    // Mapping of node addresses to their reputation scores
    mapping(address => NodeReputation) public nodeRegistry;

    // Events for logging (useful for generating graphs in your paper)
    event RootSubmitted(uint256 indexed roundId, bytes32 root);
    event AuditPassed(address indexed node, uint256 roundId);
    event AuditFailed(address indexed node, uint256 roundId);

    /**
     * @dev Step 4: Store the Merkle Root as an immutable "Digital Seal"[cite: 24, 32].
     */
    function submitRoundRoot(uint256 _roundId, bytes32 _root) public {
        // In a real system, only the authorized Aggregator should call this
        roundMerkleRoots[_roundId] = _root;
        emit RootSubmitted(_roundId, _root);
    }

    /**
     * @dev Step 5: Verify the Proof (Catching the Liar Phase)[cite: 33, 41].
     * This function mathematically verifies that the node's data matches the stored root.
     */
    function verifyAndAudit(
        uint256 _roundId,
        bytes32 _leafHash,      // The node's specific commitment [cite: 26]
        bytes32[] memory _proof, // The Merkle Path [cite: 43]
        address _nodeAddress
    ) public returns (bool) {
        
        // 1. Initial check: Is the node already blacklisted?
        if (nodeRegistry[_nodeAddress].isBlacklisted) {
            return false;
        }

        bytes32 computedHash = _leafHash;

        // 2. Reconstruct the Merkle Root using the provided path [cite: 49, 50]
        for (uint256 i = 0; i < _proof.length; i++) {
            bytes32 proofElement = _proof[i];

            if (computedHash <= proofElement) {
                // Hash(current, sibling)
                computedHash = keccak256(abi.encodePacked(computedHash, proofElement));
            } else {
                // Hash(sibling, current)
                computedHash = keccak256(abi.encodePacked(proofElement, computedHash));
            }
        }

        // 3. Step 5: Result (Punishment or Reward) [cite: 53]
        bool isHonest = (computedHash == roundMerkleRoots[_roundId]);

        if (isHonest) {
            // Integrity Proven: Update Success count [cite: 54, 55]
            nodeRegistry[_nodeAddress].successes += 1;
            emit AuditPassed(_nodeAddress, _roundId);
        } else {
            // Caught Tampering: Automate Penalties [cite: 56, 57]
            nodeRegistry[_nodeAddress].failures += 1;
            nodeRegistry[_nodeAddress].isBlacklisted = true; // Kicks them out [cite: 59]
            emit AuditFailed(_nodeAddress, _roundId);
        }

        return isHonest;
    }

    /**
     * @dev Helper to fetch reputation for the Tiered Gate 2 check[cite: 16].
     */
    function getReputation(address _nodeAddress) public view returns (uint256 s, uint256 f) {
        NodeReputation memory node = nodeRegistry[_nodeAddress];
        return (node.successes, node.failures);
    }
}