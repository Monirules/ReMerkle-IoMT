# ReMerkle: Proof of Reputation-Driven Federated Learning with Compact Merkle Verification for Consumer-centric IoMT

&lt;p align="center"&gt;
  &lt;img src="https://img.shields.io/badge/IEEE%20Transactions-Under%20Review-blue.svg" alt="Publication Status"/&gt;
  &lt;img src="https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white" alt="Python Version"/&gt;
  &lt;img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License"/&gt;
  &lt;img src="https://img.shields.io/badge/Blockchain-Ethereum-3C3C3D?logo=ethereum&logoColor=white" alt="Ethereum"/&gt;
&lt;/p&gt;

&lt;p align="center"&gt;
  &lt;b&gt;🏥 Secure Federated Learning for Medical IoT with 97.99% Reduced Blockchain Overhead&lt;/b&gt;&lt;br&gt;
  &lt;i&gt;WBAN-optimized • Byzantine-Robust • Consumer-Affordable&lt;/i&gt;
&lt;/p&gt;

---

## 📌 Project Overview

**ReMerkle** is a secure, resource-efficient framework designed to protect Internet of Medical Things (IoMT) devices in Wireless Body Area Networks (WBAN). It leverages Federated Learning (FL) to preserve privacy, but adds a critical security layer: **Proof of Reputation-Driven (PoR)** verification.

Traditional blockchain-based FL is too expensive for consumer electronics due to massive gas costs. ReMerkle solves this by using **Compact Merkle Verification**, storing only the Merkle Root on-chain while providing a **97.99% reduction** in blockchain overhead.

### ✨ Key Features

- 🔒 **Zero-Knowledge Privacy**: Raw medical data never leaves the sensor device
- ⚡ **Lightweight Verification**: Merkle proofs reduce verification to O(log n) complexity  
- 🛡️ **Triple-Gate Security**: Cosine + Beta + Entropy sequential filtering
- 💰 **Consumer Viable**: Costs drop from ~$141 to **$0.60** per transaction (at 30 gwei)
- 📊 **Automated Auditing**: Smart Contract-driven "Surprise Quizzes" detect malicious actors

---

## 🚀 The 5-Step Secure Workflow

&lt;p align="center"&gt;
  &lt;img src="docs/figures/ieee_methodology_diagram.png" alt="ReMerkle Architecture" width="800"/&gt;
&lt;/p&gt;

The ReMerkle framework follows a structured pipeline to ensure that only high-quality, trusted updates influence the global health model:

### Step 1: Local Training (Sensor Level)
WBAN nodes train lightweight models locally on 3-axis accelerometer data to ensure raw medical data never leaves the device.

### Step 2: Tiered Reputation Gating
Before aggregation, updates pass through three sequential "Security Gates":

| Gate | Mechanism | Purpose |
|------|-----------|---------|
| **Gate 1** | Cosine Similarity | Filters out immediate model poisoning attacks |
| **Gate 2** | Beta Reputation | Assesses long-term node reliability using historical success/failure rates |
| **Gate 3** | Entropy Quality | Evaluates prediction confidence to discard noisy or "confused" sensor data |

### Step 3: Hash Commitment
Each node generates a **SHA-256 "Digital Seal"** of its model parameters and quality score, creating a tamper-evident fingerprint.

### Step 4: Compact Merkle-Tree Aggregation
Thousands of updates are bundled into a single Merkle Tree. Only the **Merkle Root** is stored on-chain, creating an immutable reference at near-zero cost.

### Step 5: Automated Audit (Surprise Quiz)
A Smart Contract-driven "Surprise Quiz" selects random nodes for verification. Using the **Merkle Path**, the contract:
- ✅ Proves the node is honest (valid proof → reputation boost)
- ❌ Detects tampered updates (invalid proof → immediate slashing)

---

## 📈 Technical Performance

Our simulation on the **WBAN HAR Dataset** (Nodes 1–5, 5 Activity Classes) demonstrates:

### Efficiency Analysis

| Metric | Traditional FL (On-Chain) | ReMerkle (Ours) | Improvement |
|--------|---------------------------|-----------------|-------------|
| **Gas Cost** (per Round) | ~4,700,000 | ~20,000 | **99.57% ↓** |
| **Storage** (per Round) | 75,000 Bytes | 32 Bytes | **99.96% ↓** |
| **Verification Time** | ~500 ms | &lt;1 ms | **99.80% ↓** |
| **Audit Scalability** | Linear O(n) | Logarithmic O(log n) | **Exponential** |

### Key Findings

- **Trust Accumulation**: Honest nodes see a Beta Score increase from 0.5 to 0.85+ over 10 rounds
- **Malicious Mitigation**: Nodes that fail the Step 5 Audit are immediately dropped from the global model, preserving accuracy
- **Consumer Viability**: Transaction costs drop from ~$141 to **$0.60**, making it affordable for consumer-centric health monitoring

---

## 📂 Repository Structure

```text
ReMerkle/
├── 📁 data/                      # WBAN HAR Dataset (3-axis accelerometer)
├── 📁 src/
│   ├── data_loader.py            # Standardizes sensor data & person-based splitting
│   ├── local_model.py            # Lightweight Softmax Regression (WBAN-optimized)
│   ├── reputation_gates.py       # Tiered Gating logic (Cosine, Beta, Entropy)
│   ├── fl_server.py              # Aggregator, Merkle Tree builder, Smart Contract Judge
│   ├── merkle_utils.py           # Cryptographic hashing & Merkle Proof verification
│   └── blockchain_analysis.py    # IEEE-standard research plots & metrics
├── 📁 contracts/
│   └── ReMerkleValidator.sol     # Solidity smart contract for on-chain verification
├── 📁 docs/
│   └── figures/                  # Architecture diagrams & result plots
├── main.ipynb                    # Interactive simulation notebook
└── requirements.txt              # Python dependencies