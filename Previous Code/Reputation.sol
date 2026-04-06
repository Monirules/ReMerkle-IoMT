// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title Reputation
 * @dev Manages decentralized reputation scores and Proof of Learning (Merkle Roots) for federated learning clients.
 */
contract Reputation {
    
    struct Client {
        uint256 reputationScore;   // Scaled by 1e18 (1.0 = 1000000000000000000)
        bytes32 latestMerkleRoot;  // Proof of Learning for the latest round
        uint256 lastUpdateRound;   // The round number of the last update
        bool isRegistered;
    }

    mapping(address => Client) public clients;
    address public owner;

    event ClientRegistered(address indexed client);
    event ReputationUpdated(address indexed client, uint256 newScore, uint256 round);
    event MerkleRootSubmitted(address indexed client, bytes32 root, uint256 round);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    /**
     * @dev Registers a new client with default reputation (1.0).
     */
    function registerClient(address _client) external onlyOwner {
        require(!clients[_client].isRegistered, "Client already registered");
        clients[_client].isRegistered = true;
        clients[_client].reputationScore = 1 * 10**18; // Default to 1.0
        emit ClientRegistered(_client);
    }

    /**
     * @dev Updates the reputation score for a client.
     * @param _client The address of the client.
     * @param _newScore The new reputation score (scaled by 1e18).
     */
    function updateReputation(address _client, uint256 _newScore) external onlyOwner {
        require(clients[_client].isRegistered, "Client not registered");
        clients[_client].reputationScore = _newScore;
        emit ReputationUpdated(_client, _newScore, block.number);
    }

    /**
     * @dev Submits the Merkle Root (Proof of Learning) for a training round.
     * @param _client The address of the client.
     * @param _root The Merkle Root of the training metadata.
     * @param _round The training round number.
     */
    function submitMerkleRoot(address _client, bytes32 _root, uint256 _round) external onlyOwner {
        require(clients[_client].isRegistered, "Client not registered");
        clients[_client].latestMerkleRoot = _root;
        clients[_client].lastUpdateRound = _round;
        emit MerkleRootSubmitted(_client, _root, _round);
    }

    /**
     * @dev Returns the full details of a client.
     */
    function getClientDetails(address _client) external view returns (uint256 score, bytes32 root, uint256 round) {
        Client memory c = clients[_client];
        return (c.reputationScore, c.latestMerkleRoot, c.lastUpdateRound);
    }
}
