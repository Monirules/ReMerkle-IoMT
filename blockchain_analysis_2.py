"""
ADDITIONAL BLOCKCHAIN VISUALIZATIONS
5 High-Impact Single-Focus Diagrams for Your Research
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrowPatch, Wedge
from matplotlib.patches import ConnectionPatch
import seaborn as sns

plt.style.use('seaborn-v0_8-whitegrid')

print("=" * 70)
print("CREATING 5 ADDITIONAL BLOCKCHAIN VISUALIZATIONS")
print("=" * 70)

# ============================================================================
# DIAGRAM 1: TRANSACTION FLOW COMPARISON
# ============================================================================
print("\n[1/5] Creating Transaction Flow Comparison...")

fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

# Traditional Flow
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 12)
ax1.axis('off')
ax1.set_title('Traditional Approach: Full Model Storage\n(High Complexity)', 
              fontsize=14, fontweight='bold', pad=20)

# Nodes
y_nodes = 10
for i, x in enumerate([1, 2.5, 4, 5.5, 7]):
    circle = Circle((x, y_nodes), 0.4, color='#ff9999', ec='black', linewidth=2)
    ax1.add_patch(circle)
    ax1.text(x, y_nodes, f'N{i+1}', ha='center', va='center', fontweight='bold')
    ax1.text(x, y_nodes-0.8, '15KB', ha='center', fontsize=8)
    
    # Arrows to blockchain
    arrow = FancyArrowPatch((x, y_nodes-0.5), (x, 6),
                           arrowstyle='->', mutation_scale=20, linewidth=2,
                           color='red', linestyle='--')
    ax1.add_patch(arrow)
    ax1.text(x+0.3, 8, f'{i+1}', fontsize=9, color='red', fontweight='bold')

# Blockchain
blockchain = FancyBboxPatch((0.5, 4), 9, 1.5, boxstyle="round,pad=0.1",
                            facecolor='#ffcccc', edgecolor='black', linewidth=3)
ax1.add_patch(blockchain)
ax1.text(5, 4.75, 'BLOCKCHAIN\n75 KB Stored (5 × 15 KB)', 
         ha='center', va='center', fontsize=11, fontweight='bold')

# Gas costs
ax1.text(5, 3, '⚠️ Gas Cost: 9.4M × 5 = 47M gas', 
         ha='center', fontsize=12, fontweight='bold', 
         bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))

# Smart Contract
contract = FancyBboxPatch((3.5, 1.5), 3, 1, boxstyle="round,pad=0.1",
                         facecolor='#ffeeee', edgecolor='black', linewidth=2)
ax1.add_patch(contract)
ax1.text(5, 2, 'Smart Contract\nVerification: 1M gas', 
         ha='center', va='center', fontsize=10)

# Issues
ax1.text(5, 0.5, '❌ Expensive  ❌ Slow  ❌ Doesn\'t Scale', 
         ha='center', fontsize=11, color='red', fontweight='bold')

# Merkle-PoR Flow
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 12)
ax2.axis('off')
ax2.set_title('Merkle-PoR Approach: Hash-Based Proof\n(Low Complexity)', 
              fontsize=14, fontweight='bold', pad=20)

# Nodes
y_nodes = 10
for i, x in enumerate([1, 2.5, 4, 5.5, 7]):
    circle = Circle((x, y_nodes), 0.4, color='#99ccff', ec='black', linewidth=2)
    ax2.add_patch(circle)
    ax2.text(x, y_nodes, f'N{i+1}', ha='center', va='center', fontweight='bold')
    ax2.text(x, y_nodes-0.8, '32B', ha='center', fontsize=8)
    
    # Small arrows (just hashes)
    arrow = FancyArrowPatch((x, y_nodes-0.5), (x, 8),
                           arrowstyle='->', mutation_scale=15, linewidth=1.5,
                           color='green')
    ax2.add_patch(arrow)

# Merkle Tree (off-chain)
tree_box = FancyBboxPatch((2, 7), 6, 1.5, boxstyle="round,pad=0.1",
                         facecolor='#e8f5e9', edgecolor='green', 
                         linewidth=2, linestyle='--')
ax2.add_patch(tree_box)
ax2.text(5, 7.75, 'Merkle Tree (Off-Chain)\nCompute Root: 300 gas', 
         ha='center', va='center', fontsize=10)

# Single arrow to blockchain
arrow_root = FancyArrowPatch((5, 7), (5, 5.5),
                            arrowstyle='->', mutation_scale=30, linewidth=3,
                            color='green')
ax2.add_patch(arrow_root)
ax2.text(5.5, 6.2, 'ROOT\n32B', ha='center', fontsize=9, 
         fontweight='bold', color='green')

# Blockchain
blockchain2 = FancyBboxPatch((0.5, 4), 9, 1.5, boxstyle="round,pad=0.1",
                            facecolor='#ccffcc', edgecolor='black', linewidth=3)
ax2.add_patch(blockchain2)
ax2.text(5, 4.75, 'BLOCKCHAIN\n32 Bytes Stored (Just Root!)', 
         ha='center', va='center', fontsize=11, fontweight='bold')

# Gas costs
ax2.text(5, 3, '✅ Gas Cost: 20K gas', 
         ha='center', fontsize=12, fontweight='bold',
         bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))

# Smart Contract
contract2 = FancyBboxPatch((3.5, 1.5), 3, 1, boxstyle="round,pad=0.1",
                          facecolor='#eeffee', edgecolor='black', linewidth=2)
ax2.add_patch(contract2)
ax2.text(5, 2, 'Smart Contract\nVerification: <1 ms', 
         ha='center', va='center', fontsize=10)

# Benefits
ax2.text(5, 0.5, '✅ Cheap  ✅ Fast  ✅ Scales', 
         ha='center', fontsize=11, color='green', fontweight='bold')

plt.tight_layout()
plt.savefig('blockchain_visual_1_transaction_flow.png', dpi=300, bbox_inches='tight')
print("✓ Saved: blockchain_visual_1_transaction_flow.png")

# ============================================================================
# DIAGRAM 2: COST OVER TIME (MULTIPLE SCENARIOS)
# ============================================================================
print("[2/5] Creating Cost Over Time Analysis...")

fig2, ax = plt.subplots(figsize=(14, 8))

rounds = np.arange(1, 101)  # 100 rounds

# Different gas prices
gas_prices = [10, 30, 50, 100]  # gwei
eth_price = 3000

for gwei in gas_prices:
    # Traditional cost
    trad_cost = [(r * 4_700_000 * gwei * 1e-9 * eth_price) for r in rounds]
    
    # Merkle cost
    merkle_cost = [(r * 20_000 * gwei * 1e-9 * eth_price) for r in rounds]
    
    # Plot
    ax.plot(rounds, trad_cost, linewidth=2, linestyle='--', 
            label=f'Traditional @ {gwei} gwei', alpha=0.7)
    ax.plot(rounds, merkle_cost, linewidth=2.5, 
            label=f'Merkle-PoR @ {gwei} gwei')

ax.set_xlabel('Training Rounds', fontsize=13, fontweight='bold')
ax.set_ylabel('Cumulative Cost (USD)', fontsize=13, fontweight='bold')
ax.set_title('Blockchain Cost Over Time: Impact of Gas Prices\n(5 Nodes, ETH = $3000)', 
             fontsize=14, fontweight='bold')
ax.legend(loc='upper left', fontsize=10, ncol=2)
ax.grid(True, alpha=0.3)
ax.set_yscale('log')

# Highlight zones
ax.axhspan(0, 1000, alpha=0.1, color='green', label='Affordable Zone')
ax.axhspan(1000, 10000, alpha=0.1, color='yellow')
ax.axhspan(10000, 100000, alpha=0.1, color='red')

# Add annotations
ax.annotate('Merkle-PoR stays\naffordable even\nat 100 gwei!', 
            xy=(80, 600), xytext=(50, 5000),
            arrowprops=dict(arrowstyle='->', lw=2, color='green'),
            fontsize=11, fontweight='bold', color='green',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))

ax.annotate('Traditional becomes\nprohibitively expensive', 
            xy=(80, 40000), xytext=(40, 60000),
            arrowprops=dict(arrowstyle='->', lw=2, color='red'),
            fontsize=11, fontweight='bold', color='red',
            bbox=dict(boxstyle='round', facecolor='#ffcccc', alpha=0.8))

plt.tight_layout()
plt.savefig('blockchain_visual_2_cost_over_time.png', dpi=300, bbox_inches='tight')
print("✓ Saved: blockchain_visual_2_cost_over_time.png")

# ============================================================================
# DIAGRAM 3: SECURITY VS EFFICIENCY QUADRANT
# ============================================================================
print("[3/5] Creating Security vs Efficiency Quadrant...")

fig3, ax = plt.subplots(figsize=(12, 10))

# Define approaches
approaches = {
    'Traditional\n(Full Storage)': {'security': 9, 'efficiency': 1, 'color': '#d62728', 'size': 300},
    'Hash-Only\n(No Proof)': {'security': 3, 'efficiency': 9, 'color': '#ff7f0e', 'size': 250},
    'Merkle-PoR\n(Our Approach)': {'security': 9, 'efficiency': 9.5, 'color': '#2ca02c', 'size': 500},
    'Optimistic\nRollup': {'security': 7, 'efficiency': 9.2, 'color': '#9467bd', 'size': 280},
    'ZK-Rollup': {'security': 9.5, 'efficiency': 8.5, 'color': '#8c564b', 'size': 280},
    'No Blockchain\n(Centralized)': {'security': 1, 'efficiency': 10, 'color': '#7f7f7f', 'size': 200},
}

# Plot
for name, props in approaches.items():
    ax.scatter(props['efficiency'], props['security'], 
              s=props['size'], c=props['color'], 
              alpha=0.7, edgecolors='black', linewidth=2,
              label=name, zorder=3)
    
    # Add labels
    offset_x = 0.3 if props['efficiency'] < 5 else -0.3
    offset_y = 0.3 if props['security'] < 5 else -0.3
    ax.text(props['efficiency'] + offset_x, props['security'] + offset_y, 
            name, fontsize=10, fontweight='bold',
            ha='left' if offset_x > 0 else 'right')

# Quadrants
ax.axhline(5, color='gray', linestyle='--', alpha=0.5, linewidth=1)
ax.axvline(5, color='gray', linestyle='--', alpha=0.5, linewidth=1)

# Labels for quadrants
ax.text(2.5, 9, 'High Security\nLow Efficiency', ha='center', fontsize=11, 
        style='italic', color='#666',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
ax.text(7.5, 9, 'IDEAL ZONE\nHigh Security\nHigh Efficiency', ha='center', fontsize=12, 
        fontweight='bold', color='green',
        bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
ax.text(2.5, 2, 'Low Security\nLow Efficiency', ha='center', fontsize=11, 
        style='italic', color='#666',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
ax.text(7.5, 2, 'High Efficiency\nLow Security', ha='center', fontsize=11, 
        style='italic', color='#666',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

# Highlight ideal zone
ideal_box = Rectangle((7, 7), 3, 3, linewidth=3, edgecolor='green', 
                      facecolor='none', linestyle='--')
ax.add_patch(ideal_box)

ax.set_xlabel('Efficiency (Cost, Speed, Scalability)', fontsize=13, fontweight='bold')
ax.set_ylabel('Security (Tamper Resistance, Auditability)', fontsize=13, fontweight='bold')
ax.set_title('Security vs Efficiency Trade-off\nBlockchain-Based Federated Learning', 
             fontsize=14, fontweight='bold')
ax.set_xlim(0, 11)
ax.set_ylim(0, 11)
ax.grid(True, alpha=0.3)

# Add arrow pointing to Merkle-PoR
ax.annotate('Our Approach:\nBest of Both Worlds!', 
            xy=(9.5, 9), xytext=(6, 6),
            arrowprops=dict(arrowstyle='->', lw=3, color='green'),
            fontsize=12, fontweight='bold', color='green',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.9))

plt.tight_layout()
plt.savefig('blockchain_visual_3_security_efficiency.png', dpi=300, bbox_inches='tight')
print("✓ Saved: blockchain_visual_3_security_efficiency.png")

# ============================================================================
# DIAGRAM 4: DATA FLOW ARCHITECTURE
# ============================================================================
print("[4/5] Creating System Architecture Diagram...")

fig4 = plt.figure(figsize=(14, 10))
ax = plt.subplot(111)
ax.set_xlim(0, 14)
ax.set_ylim(0, 12)
ax.axis('off')
ax.set_title('Merkle-PoR System Architecture\nEnd-to-End Data Flow', 
             fontsize=16, fontweight='bold', pad=20)

# Layer 1: WBAN Nodes (Bottom)
y_wban = 1.5
for i, x in enumerate([2, 4, 6, 8, 10]):
    # WBAN sensor
    sensor = Circle((x, y_wban), 0.5, color='#ffcccc', ec='black', linewidth=2)
    ax.add_patch(sensor)
    ax.text(x, y_wban, f'W{i+1}', ha='center', va='center', fontweight='bold', fontsize=10)
    ax.text(x, y_wban-0.9, 'WBAN\nNode', ha='center', fontsize=8)
    
    # Arrow up
    arrow = FancyArrowPatch((x, y_wban+0.6), (x, 3.5),
                           arrowstyle='->', mutation_scale=15, linewidth=1.5,
                           color='blue')
    ax.add_patch(arrow)
    ax.text(x+0.3, 2.5, 'Train', fontsize=7, rotation=90)

# Layer 2: Local Training
training_box = FancyBboxPatch((1, 3.5), 10, 1.2, boxstyle="round,pad=0.1",
                             facecolor='#cce5ff', edgecolor='blue', linewidth=2)
ax.add_patch(training_box)
ax.text(6, 4.1, 'LOCAL TRAINING (Off-Chain)', ha='center', va='center',
        fontsize=11, fontweight='bold')
ax.text(6, 3.7, 'RandomForest Models + Feature Engineering', ha='center', fontsize=9)

# Arrow to Merkle Layer
arrow_to_merkle = FancyArrowPatch((6, 4.7), (6, 5.8),
                                 arrowstyle='->', mutation_scale=20, linewidth=2,
                                 color='green')
ax.add_patch(arrow_to_merkle)
ax.text(6.5, 5.2, 'Hash', fontsize=9, fontweight='bold', color='green')

# Layer 3: Merkle Tree Construction
merkle_box = FancyBboxPatch((1, 5.8), 10, 1.5, boxstyle="round,pad=0.1",
                           facecolor='#e8f5e9', edgecolor='green', linewidth=2)
ax.add_patch(merkle_box)
ax.text(6, 6.9, 'MERKLE TREE CONSTRUCTION (Off-Chain)', ha='center', va='center',
        fontsize=11, fontweight='bold')

# Draw mini tree
tree_x = [3, 4.5, 6, 7.5, 9]
tree_y = 6.2
for i, x in enumerate(tree_x):
    circle = Circle((x, tree_y), 0.15, color='lightgreen', ec='black', linewidth=1)
    ax.add_patch(circle)
    ax.text(x, tree_y, f'{i+1}', ha='center', va='center', fontsize=6)

# Parent nodes
parent_y = 6.7
ax.plot([3.75, 6, 8.25], [parent_y, parent_y, parent_y], 'o', 
        markersize=8, color='green', markeredgecolor='black')

# Root
root_y = 7.1
ax.plot([6], [root_y], 'o', markersize=12, color='#ffcc00', 
        markeredgecolor='black', markeredgewidth=2)
ax.text(6.5, root_y, 'ROOT', fontsize=8, fontweight='bold')

# Arrow to blockchain
arrow_to_bc = FancyArrowPatch((6, 7.3), (6, 8.3),
                             arrowstyle='->', mutation_scale=25, linewidth=3,
                             color='gold')
ax.add_patch(arrow_to_bc)
ax.text(6.7, 7.8, '32 bytes\n20K gas', fontsize=9, fontweight='bold', 
        color='#ff6600',
        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))

# Layer 4: Blockchain
blockchain_box = FancyBboxPatch((1, 8.3), 10, 1.2, boxstyle="round,pad=0.1",
                               facecolor='#fff3cd', edgecolor='#ff6600', linewidth=3)
ax.add_patch(blockchain_box)
ax.text(6, 9.1, 'BLOCKCHAIN (On-Chain)', ha='center', va='center',
        fontsize=12, fontweight='bold', color='#ff6600')
ax.text(6, 8.7, 'Smart Contract: Store Root + Verify Proofs', ha='center', fontsize=9)

# Side: Reputation System
rep_box = FancyBboxPatch((11.5, 5), 2, 3.5, boxstyle="round,pad=0.1",
                        facecolor='#ffe6e6', edgecolor='red', linewidth=2, linestyle='--')
ax.add_patch(rep_box)
ax.text(12.5, 8, 'REPUTATION\nSYSTEM', ha='center', va='center',
        fontsize=10, fontweight='bold')
ax.text(12.5, 7.3, '🛡️ Gate 1\nCosine', ha='center', fontsize=8)
ax.text(12.5, 6.7, '📊 Gate 2\nBeta', ha='center', fontsize=8)
ax.text(12.5, 6.1, '🎲 Gate 3\nEntropy', ha='center', fontsize=8)
ax.text(12.5, 5.5, '🔍 Audit\n(10%)', ha='center', fontsize=8)

# Connections from reputation to layers
arrow_rep1 = FancyArrowPatch((11.5, 6.5), (11, 4.1),
                            arrowstyle='->', mutation_scale=15, linewidth=1.5,
                            color='red', linestyle='--')
ax.add_patch(arrow_rep1)

arrow_rep2 = FancyArrowPatch((11.5, 7.5), (11, 8.9),
                            arrowstyle='->', mutation_scale=15, linewidth=1.5,
                            color='red', linestyle='--')
ax.add_patch(arrow_rep2)

# Top: Global Model
global_box = FancyBboxPatch((3.5, 10), 5, 1, boxstyle="round,pad=0.1",
                           facecolor='#d4edda', edgecolor='darkgreen', linewidth=3)
ax.add_patch(global_box)
ax.text(6, 10.5, 'GLOBAL MODEL UPDATE', ha='center', va='center',
        fontsize=12, fontweight='bold', color='darkgreen')

# Arrow from blockchain to global
arrow_to_global = FancyArrowPatch((6, 9.5), (6, 10),
                                 arrowstyle='->', mutation_scale=20, linewidth=2,
                                 color='darkgreen')
ax.add_patch(arrow_to_global)

# Legend/Notes
notes = """
KEY FEATURES:
✓ Off-chain: Training + Tree Building
✓ On-chain: Only Root (32 bytes)
✓ Scalable: O(log n) verification
✓ Secure: Cryptographic proofs
✓ Cost: 20K gas vs 4.7M gas
"""
ax.text(0.5, 9, notes, fontsize=9, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9),
        family='monospace')

plt.tight_layout()
plt.savefig('blockchain_visual_4_architecture.png', dpi=300, bbox_inches='tight')
print("✓ Saved: blockchain_visual_4_architecture.png")

# ============================================================================
# DIAGRAM 5: PROOF SIZE GROWTH COMPARISON
# ============================================================================
print("[5/5] Creating Proof Size Growth Analysis...")

fig5, ax = plt.subplots(figsize=(12, 8))

nodes = np.array([2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000])

# Traditional: Must send full model
traditional = np.full_like(nodes, 15360, dtype=float)  # 15 KB in bytes

# Merkle: log(n) * 32 bytes
merkle = np.ceil(np.log2(nodes)) * 32

# Hash-only: constant
hash_only = np.full_like(nodes, 32, dtype=float)

# Plot
ax.plot(nodes, traditional, 'o-', linewidth=3, markersize=8, 
        color='#d62728', label='Traditional (Full Model)')
ax.plot(nodes, merkle, '^-', linewidth=3, markersize=8,
        color='#2ca02c', label='Merkle-PoR (Log n)')
ax.plot(nodes, hash_only, 's--', linewidth=2, markersize=7,
        color='#ff7f0e', label='Hash-Only (No Verification)', alpha=0.7)

ax.set_xlabel('Number of Federated Nodes', fontsize=13, fontweight='bold')
ax.set_ylabel('Audit Proof Size (bytes)', fontsize=13, fontweight='bold')
ax.set_title('Proof Size Growth: Scalability Comparison\nHow does proof size grow with network size?', 
             fontsize=14, fontweight='bold')
ax.set_xscale('log')
ax.set_yscale('log')
ax.legend(fontsize=11, loc='upper left')
ax.grid(True, which='both', alpha=0.3)

# Annotations
ax.annotate('O(1) - Constant\n(But no proof!)', 
            xy=(2000, 32), xytext=(500, 100),
            arrowprops=dict(arrowstyle='->', lw=2, color='#ff7f0e'),
            fontsize=11, fontweight='bold', color='#ff7f0e',
            bbox=dict(boxstyle='round', facecolor='#fff3cd', alpha=0.9))

ax.annotate('O(log n) - Logarithmic\nScales excellently!', 
            xy=(2000, merkle[-2]), xytext=(500, 500),
            arrowprops=dict(arrowstyle='->', lw=2, color='#2ca02c'),
            fontsize=11, fontweight='bold', color='#2ca02c',
            bbox=dict(boxstyle='round', facecolor='#d4edda', alpha=0.9))

ax.annotate('O(1) - Constant\n(But expensive!)', 
            xy=(2000, 15360), xytext=(200, 5000),
            arrowprops=dict(arrowstyle='->', lw=2, color='#d62728'),
            fontsize=11, fontweight='bold', color='#d62728',
            bbox=dict(boxstyle='round', facecolor='#f8d7da', alpha=0.9))

# Add specific values
ax.text(1000, merkle[-3], f'{int(merkle[-3])} bytes\n@ 1000 nodes', 
        fontsize=10, ha='center', fontweight='bold', color='green',
        bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))

ax.text(5000, merkle[-1], f'{int(merkle[-1])} bytes\n@ 5000 nodes', 
        fontsize=10, ha='center', fontweight='bold', color='green',
        bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))

# Comparison box
comparison_text = f"""
@ 1000 nodes:
Traditional: 15,360 bytes
Merkle-PoR: {int(merkle[-3])} bytes
Reduction: {((traditional[0] - merkle[-3])/traditional[0]*100):.1f}%

@ 5000 nodes:
Traditional: 15,360 bytes  
Merkle-PoR: {int(merkle[-1])} bytes
Reduction: {((traditional[0] - merkle[-1])/traditional[0]*100):.1f}%
"""
ax.text(0.02, 0.98, comparison_text, transform=ax.transAxes,
        fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='black', linewidth=2),
        family='monospace')

plt.tight_layout()
plt.savefig('blockchain_visual_5_proof_growth.png', dpi=300, bbox_inches='tight')
print("✓ Saved: blockchain_visual_5_proof_growth.png")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 70)
print("✅ CREATED 5 NEW BLOCKCHAIN VISUALIZATIONS")
print("=" * 70)
print("\n📊 Generated Files:")
print("  1. blockchain_visual_1_transaction_flow.png")
print("     → Side-by-side comparison of data flow")
print("  2. blockchain_visual_2_cost_over_time.png")
print("     → Cost accumulation under different gas prices")
print("  3. blockchain_visual_3_security_efficiency.png")
print("     → Quadrant analysis of security vs efficiency")
print("  4. blockchain_visual_4_architecture.png")
print("     → Complete system architecture with data flow")
print("  5. blockchain_visual_5_proof_growth.png")
print("     → Scalability analysis (proof size vs nodes)")
print("\n🎯 Each diagram focuses on ONE key insight!")
print("=" * 70)
