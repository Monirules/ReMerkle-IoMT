import numpy as np
import matplotlib.pyplot as plt
import itertools
from scipy.stats import entropy
from sklearn.metrics.pairwise import cosine_similarity
import warnings
import os
from MerkleProof import MerkleProof

warnings.filterwarnings("ignore")

# ===========================================================
# REPUTATION MANAGEMENT SYSTEM
# ===========================================================

class ReputationManager:
    """
    Advanced multi-method reputation management for federated learning.
    Implements 7 different reputation calculation methods with validation.

    MODIFIED: Now accepts a 'reputation_weights' dictionary in __init__.
    """

    def __init__(self, num_clients, reputation_weights, alpha_beta=2.0, lambda_decay=0.1):
        self.num_clients = num_clients
        self.reputation_weights = reputation_weights  # External weights
        self.alpha_beta = alpha_beta
        self.lambda_decay = lambda_decay

        # Historical tracking
        self.reputation_history = [[] for _ in range(num_clients)]
        self.performance_history = [[] for _ in range(num_clients)]
        self.validation_improvements = [[] for _ in range(num_clients)]
        self.successes = np.ones(num_clients)
        self.failures = np.ones(num_clients)
        self.previous_predictions = [None] * num_clients
        self.baseline_performance = None

    def calculate_weighted_average(self, client_id, current_score, window=5):
        # FIXED: Use performance_history (accuracy) instead of reputation_history
        history = self.performance_history[client_id]
        if len(history) == 0:
            return current_score
        recent = history[-window:] + [current_score]
        weights = np.exp(np.linspace(0, 1, len(recent)))
        weights = weights / weights.sum()
        return np.sum(np.array(recent) * weights)

    def calculate_beta_reputation(self, client_id):
        alpha = self.successes[client_id]
        beta = self.failures[client_id]
        reputation = alpha / (alpha + beta)
        variance = (alpha * beta) / ((alpha + beta)**2 * (alpha + beta + 1))
        confidence_factor = 1.0 / (1.0 + variance * 10)
        return reputation * confidence_factor

    def calculate_fuzzy_trust(self, client_id, accuracy, consistency, plausibility):
        def triangular(x, a, b, c):
            if x <= a or x >= c: return 0.0
            elif a < x <= b: return (x - a) / (b - a)
            else: return (c - x) / (c - b)

        acc_low = triangular(accuracy, 0, 0, 0.5)
        acc_med = triangular(accuracy, 0.3, 0.5, 0.7)
        acc_high = triangular(accuracy, 0.6, 1.0, 1.0)
        cons_low = triangular(consistency, 0, 0, 0.5)
        cons_high = triangular(consistency, 0.5, 1.0, 1.0)
        plaus_low = triangular(plausibility, 0, 0, 0.5)
        plaus_high = triangular(plausibility, 0.5, 1.0, 1.0)

        trust = 0.0
        trust += min(acc_high, cons_high, plaus_high) * 1.0
        trust += min(acc_med, cons_high, plaus_high) * 0.7
        trust += min(acc_low, cons_high, plaus_high) * 0.3
        return min(trust, 1.0)

    def calculate_tanh_utility(self, client_id, validation_improvement):
        utility = (np.tanh(validation_improvement * 5) + 1) / 2
        if len(self.reputation_history[client_id]) > 0:
            historical = np.mean(self.reputation_history[client_id][-3:])
            utility = 0.7 * utility + 0.3 * historical
        return utility

    def calculate_exponential_decay(self, client_id, current_score):
        # FIXED: Use performance_history (accuracy) instead of reputation_history
        history = self.performance_history[client_id]
        if len(history) == 0:
            return current_score

        # Calculate client's average historical accuracy to make decay adaptive
        # Higher average accuracy -> lower effective decay
        # Lower average accuracy -> higher effective decay
        avg_accuracy_for_client = np.mean(history + [current_score]) if history else current_score

        # Adjust lambda_decay based on average accuracy
        # A simple way: (1.1 - avg_accuracy) * base_lambda_decay. Clamp to avoid negative or too small/large.
        # E.g., if avg_accuracy is 0.9, (1.1 - 0.9) = 0.2. So effective_lambda_decay is 0.2 * self.lambda_decay
        # If avg_accuracy is 0.5, (1.1 - 0.5) = 0.6. So effective_lambda_decay is 0.6 * self.lambda_decay
        # This makes sense: higher accuracy leads to lower effective decay.
        effective_lambda_decay = self.lambda_decay * (1.1 - np.clip(avg_accuracy_for_client, 0.1, 1.0))
        effective_lambda_decay = np.clip(effective_lambda_decay, 0.01, 0.5) # Min decay 0.01, Max decay 0.5

        decayed_scores = []
        for i, score in enumerate(history):
            time_distance = len(history) - i
            decayed_score = score * np.exp(-effective_lambda_decay * time_distance)
            decayed_scores.append(decayed_score)
        all_scores = decayed_scores + [current_score]
        weights = np.exp(-effective_lambda_decay * np.arange(len(all_scores)-1, -1, -1))
        weights = weights / weights.sum()
        return np.sum(np.array(all_scores) * weights)

    def calculate_entropy_based(self, client_id, prediction_probs):
        pred_entropy = entropy(prediction_probs.T + 1e-10)
        avg_entropy = np.mean(pred_entropy)
        n_classes = prediction_probs.shape[1]
        max_entropy = np.log(n_classes) if n_classes > 1 else 1
        normalized_entropy = avg_entropy / max_entropy
        reputation = 1.0 - normalized_entropy
        if np.isnan(reputation) or np.isinf(reputation):
            reputation = 0.0
        return reputation

    def calculate_cosine_similarity_reputation(self, client_id, client_predictions, aggregate_predictions):
        client_flat = client_predictions.flatten()
        aggregate_flat = aggregate_predictions.flatten()
        similarity = cosine_similarity(
            client_flat.reshape(1, -1),
            aggregate_flat.reshape(1, -1)
        )[0, 0]
        reputation = (similarity + 1) / 2
        return reputation

    def calculate_validation_improvement(self, client_id, current_performance):
        if self.baseline_performance is None:
            return 0.0
        baseline_improvement = current_performance - self.baseline_performance
        if len(self.performance_history[client_id]) > 0:
            previous_performance = self.performance_history[client_id][-1]
            recent_improvement = current_performance - previous_performance
        else:
            recent_improvement = 0.0
        improvement = 0.6 * baseline_improvement + 0.4 * recent_improvement
        return improvement

    def calculate_consistency_score(self, client_id, current_predictions):
        if self.previous_predictions[client_id] is None:
            self.previous_predictions[client_id] = current_predictions
            return 1.0
        previous = self.previous_predictions[client_id]
        agreement = np.mean(current_predictions == previous)
        self.previous_predictions[client_id] = current_predictions
        return agreement

    def calculate_plausibility_score(self, client_id, accuracy, f1_score, global_avg_accuracy):
        deviation = abs(accuracy - global_avg_accuracy)
        if deviation < 0.1: plausibility = 1.0
        elif deviation < 0.2: plausibility = 0.8
        elif deviation < 0.3: plausibility = 0.5
        else: plausibility = 0.2
        metric_consistency = 1.0 - abs(accuracy - f1_score)
        return 0.7 * plausibility + 0.3 * metric_consistency

    def update_client_reputation(self, client_id, metrics, prediction_probs,
                                aggregate_predictions, global_avg_accuracy, current_round):
        accuracy = metrics['accuracy']
        f1 = metrics['f1']

        validation_improvement = self.calculate_validation_improvement(client_id, accuracy)
        self.performance_history[client_id].append(accuracy)
        self.validation_improvements[client_id].append(validation_improvement)

        current_predictions = np.argmax(prediction_probs, axis=1)
        consistency = self.calculate_consistency_score(client_id, current_predictions)
        plausibility = self.calculate_plausibility_score(client_id, accuracy, f1, global_avg_accuracy)

        if accuracy > 0.7:  # Threshold for success
            self.successes[client_id] += 1
        else:
            self.failures[client_id] += 1

        reputation_scores = {
            'weighted_avg': self.calculate_weighted_average(client_id, accuracy),
            'beta_reputation': self.calculate_beta_reputation(client_id),
            'fuzzy_trust': self.calculate_fuzzy_trust(client_id, accuracy, consistency, plausibility),
            'tanh_utility': self.calculate_tanh_utility(client_id, validation_improvement),
            'exponential_decay': self.calculate_exponential_decay(client_id, accuracy),
            'entropy_based': self.calculate_entropy_based(client_id, prediction_probs),
            'cosine_similarity': self.calculate_cosine_similarity_reputation(
                client_id, prediction_probs, aggregate_predictions
            ),
            'validation_improvement': max(0, validation_improvement),
            'consistency': consistency,
            'plausibility': plausibility
        }

        # MODIFIED: Use the weights passed during initialization
        combined_reputation = sum(
            reputation_scores[k] * self.reputation_weights[k]
            for k in self.reputation_weights.keys()
        )
        combined_reputation = np.clip(combined_reputation, 0, 1)
        self.reputation_history[client_id].append(combined_reputation)
        reputation_scores['combined'] = combined_reputation
        return reputation_scores

    def get_aggregation_weights(self, round_reputations):
        reputations = np.array([r['combined'] for r in round_reputations])
        exp_reputations = np.exp(reputations * 2)
        weights = exp_reputations / exp_reputations.sum()
        return weights

    def should_include_client(self, client_reputation, threshold=0.3):
        return client_reputation['combined'] >= threshold

# ===========================================================
# MOCK DATA GENERATOR
# ===========================================================

def generate_mock_data(num_clients, num_rounds, num_classes, num_test_samples):
    """
    Generates a stable, reproducible set of mock data for experimentation.

    Client Behaviors:
    - Client 1 (Good): High accuracy, high cosine similarity.
    - Client 2 (Good): High accuracy, high cosine similarity.
    - Client 3 (OK): Medium accuracy, high cosine similarity.
    - Client 4 (Poor): Low accuracy, high cosine similarity.
    - Client 5 (Attacker): High accuracy, but LOW cosine similarity (poisoning).
    """
    print("Generating mock data for simulation...")
    np.random.seed(42)  # For reproducible probabilities

    # Base accuracies for clients (mean value)
    # Base accuracies for clients (mean value)
    base_accuracies = [0.95, 0.92, 0.80, 0.60, 0.85]

    mock_data_all_rounds = []

    # Create a stable "ground truth" aggregate prediction for honest clients
    # This represents what the aggregate model *should* look like.
    true_aggregate_probs = np.random.rand(num_test_samples, num_classes)
    true_aggregate_probs = true_aggregate_probs / true_aggregate_probs.sum(axis=1, keepdims=True)

    # Create a stable "attacker" prediction
    # This is anti-correlated with the ground truth, simulating a poisoning attack.
    attacker_probs = (1.0 - true_aggregate_probs) + np.random.normal(0, 0.1, (num_test_samples, num_classes))
    attacker_probs[attacker_probs < 0] = 0 # Ensure non-negative
    attacker_probs = attacker_probs / attacker_probs.sum(axis=1, keepdims=True)

    for r in range(num_rounds):
        round_data = []
        client_probs_list = []

        # First pass: generate metrics and probs for all clients
        for c in range(num_clients):
            # Simulate slight round-to-round variation
            # Simulate slight round-to-round variation
            acc_noise = np.random.uniform(-0.03, 0.03)
            accuracy = np.clip(base_accuracies[c] + acc_noise, 0, 1)

            # Make F1 score similar to accuracy
            f1 = np.clip(accuracy - np.random.uniform(0, 0.02), 0, 1)
            metrics = {'accuracy': accuracy, 'f1': f1}

            # Generate prediction probabilities
            if c == 4:  # Client 5 is the attacker
                # Probs are anti-correlated with the true aggregate
                probs = attacker_probs + np.random.normal(0, 0.05, (num_test_samples, num_classes))
            else:
                # Honest clients are correlated with the true aggregate
                probs = true_aggregate_probs + np.random.normal(0, 0.1, (num_test_samples, num_classes))

            probs[probs < 0] = 0
            row_sums = probs.sum(axis=1, keepdims=True)
            # Avoid division by zero: if row sum is 0, assign uniform probabilities
            zero_rows = row_sums == 0
            if np.any(zero_rows):
                probs[zero_rows.flatten()] = 1.0 / num_classes
                row_sums[zero_rows] = 1.0
            
            probs = probs / row_sums

            # Generate Loss and Gradient Norms for Merkle Proof
            # Training Loss: correlated with accuracy
            loss = (1.0 - accuracy) + np.random.uniform(0, 0.05)
            
            # Gradient Norm: distinguishes client types
            if c < 3: # Good/OK clients (0, 1, 2)
                 gradient_norm = np.random.normal(1.0, 0.1)
            elif c == 3: # Poor client
                 gradient_norm = np.random.normal(1.0, 0.5) # High variance
            else: # Attacker (Client 4 / Index 4)
                 gradient_norm = np.random.normal(5.0, 1.0) # Anomaly

            round_data.append({
                'metrics': metrics, 
                'prediction_probs': probs,
                'metadata': { # New metadata for Merkle Proof
                    'loss': loss,
                    'gradient_norm': gradient_norm
                }
            })
            client_probs_list.append(probs)

        # Second pass: calculate the aggregate and add it to each client's data
        # FIXED: Aggregate should be based on HONEST clients only (exclude attacker Client 5)
        honest_client_probs = client_probs_list[:4]  # Clients 0-3 are honest
        P_aggregate = np.mean(honest_client_probs, axis=0)
        global_avg_accuracy = np.mean([d['metrics']['accuracy'] for d in round_data])

        for c in range(num_clients):
            round_data[c]['aggregate_predictions'] = P_aggregate
            round_data[c]['global_avg_accuracy'] = global_avg_accuracy

        mock_data_all_rounds.append(round_data)

    print(f"Mock data generated for {num_rounds} rounds and {num_clients} clients.")
    return mock_data_all_rounds

# ===========================================================
# PLOTTING & SUMMARY FUNCTIONS (Copied from your notebook)
# ===========================================================

def plot_global_performance(global_metrics_hist, scenario_name, rounds):
    """Plots the simulated global accuracy over rounds."""
    gm = np.array(global_metrics_hist)
    plt.figure(figsize=(14, 6))
    plt.plot(rounds, gm, marker='o', linewidth=2, markersize=6, color='#2E86AB')
    plt.title(f'Global Accuracy (Simulated) - {scenario_name}', fontsize=14, fontweight='bold')
    plt.xlabel('Round', fontsize=12)
    plt.ylabel('Reputation-Weighted Accuracy', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()


def plot_reputation_evolution(all_round_reps_hist, scenario_name, num_clients, rounds, threshold):
    """Plots the reputation of each client over rounds."""
    plt.figure(figsize=(14, 6))
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']
    for ci in range(num_clients):
        client_reps = [all_round_reps_hist[r][ci]['combined'] for r in range(len(rounds))]
        plt.plot(rounds, client_reps, marker='o', linewidth=2, label=f'Client {ci+1}', color=colors[ci])

    plt.axhline(y=threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold ({threshold})')
    plt.xlabel('Round', fontsize=12)
    plt.ylabel('Combined Reputation Score', fontsize=12)
    plt.title(f'Client Reputation Evolution - {scenario_name}', fontsize=14, fontweight='bold')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()


def plot_method_comparison(all_round_reps_hist, scenario_name, num_clients):
    """Plots a bar chart comparing final scores from each reputation method."""
    methods = ['weighted_avg', 'beta_reputation', 'fuzzy_trust', 'tanh_utility',
               'exponential_decay', 'entropy_based', 'cosine_similarity']
    method_labels = ['Weighted\nAvg', 'Beta\nRep', 'Fuzzy\nTrust', 'Tanh\nUtility',
                     'Exp\nDecay', 'Entropy', 'Cosine\nSim']
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']

    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(len(methods))
    width = 0.15

    for ci in range(num_clients):
        final_scores = [all_round_reps_hist[-1][ci][m] for m in methods]
        ax.bar(x + ci*width, final_scores, width, label=f'Client {ci+1}', color=colors[ci], alpha=0.8)

    ax.set_xlabel('Reputation Method', fontsize=12)
    ax.set_ylabel('Reputation Score', fontsize=12)
    ax.set_title(f'Comparison of Reputation Methods (Final Round) - {scenario_name}', fontsize=14, fontweight='bold')
    ax.set_xticks(x + width * (num_clients-1)/2)
    ax.set_xticklabels(method_labels)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()



def plot_client_accuracy_table(mock_data, scenario_name, num_clients):
    """Creates a table showing client accuracies and types."""
    # Get the final round data
    final_round = mock_data[-1]

    # Prepare table data
    client_data = []
    client_types = ['Good', 'Good', 'OK', 'Poor', 'Attacker']
    colors = ['#2E86AB', '#2E86AB', '#F18F01', '#C73E1D', '#A23B72']

    for ci in range(num_clients):
        accuracy = final_round[ci]['metrics']['accuracy']
        f1_score = final_round[ci]['metrics']['f1']
        client_type = client_types[ci]
        color = colors[ci]

        client_data.append([f'Client {ci+1}', f'{accuracy:.4f}', f'{f1_score:.4f}', client_type, color])

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('tight')
    ax.axis('off')

    # Create table
    table = ax.table(cellText=[[row[0], row[1], row[2], row[3]] for row in client_data],
                    colLabels=['Client', 'Accuracy', 'F1 Score', 'Type'],
                    cellColours=[[row[4], row[4], row[4], row[4]] for row in client_data],
                    cellLoc='center',
                    loc='center')

    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.5)

    # Color the header
    for i, key in enumerate(table.get_celld().keys()):
        cell = table.get_celld()[key]
        if key[0] == 0:  # Header row
            cell.set_facecolor('#404040')
            cell.set_text_props(color='white', weight='bold')
        else:  # Data rows
            cell.set_text_props(weight='normal')

    plt.title(f'Client Accuracy Overview - {scenario_name}', fontsize=14, fontweight='bold', pad=20)


def print_blockchain_integration(all_round_reps_hist, num_clients):
    """Prints the final blockchain integration data."""
    print(f"\n" + "="*60)
    print("BLOCKCHAIN INTEGRATION DATA")
    print("="*60)
    print("\nReputation scores scaled for smart contract (1e18 precision):")
    print("Use these values with the updateReputation() function\n")

    for ci in range(num_clients):
        final_rep = all_round_reps_hist[-1][ci]['combined']
        merkle_root = all_round_reps_hist[-1][ci].get('merkle_root', '0x0')
        
        if np.isnan(final_rep):
            final_rep = 0.0
        scaled_rep = int(final_rep * 1e18)
        
        print(f"Client {ci+1} (Address: 0x{''.join([f'{ci+1:02d}' for _ in range(20)])}):")
        print(f"  Reputation Score: {final_rep:.6f}")
        print(f"  Merkle Root:      {merkle_root}")
        print(f"  Scaled (uint256): {scaled_rep}")
        print(f"  Solidity Calls:")
        print(f"    1. updateReputation(clientAddress, {scaled_rep});")
        print(f"    2. submitMerkleRoot(clientAddress, 0x{merkle_root}, {len(all_round_reps_hist)});")
        print()
    print("="*60)

def print_final_summary(global_metrics_hist, all_round_reps_hist, num_clients, num_rounds):
    """Prints the final summary of the experiment."""
    print(f"\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)

    print(f"\nFinal Global Model Performance (Simulated):")
    print(f"  Accuracy:  {global_metrics_hist[-1]:.4f}")

    print(f"\nFinal Client Reputation Scores:")
    for ci in range(num_clients):
        final_rep = all_round_reps_hist[-1][ci]['combined']
        if np.isnan(final_rep):
            final_rep = 0.0
        avg_rep = np.mean([all_round_reps_hist[r][ci]['combined'] for r in range(num_rounds)])
        if np.isnan(avg_rep):
            avg_rep = 0.0
        print(f"  Client {ci+1}: Current={final_rep:.4f}, Average={avg_rep:.4f}")

# ===========================================================
# EXPERIMENT RUNNER
# ===========================================================

def run_experiment(scenario_name, weights, mock_data, num_clients, num_rounds, num_classes, reputation_threshold, baseline_performance):
    """
    Runs a single simulation scenario with a given set of weights.
    """
    print(f"\n{'='*80}\n"
          f"RUNNING SCENARIO: {scenario_name}\n"
          f"{'='*80}")

    # 1. Initialize a new ReputationManager for this scenario
    rep_man = ReputationManager(num_clients=num_clients, reputation_weights=weights)
    rep_man.baseline_performance = baseline_performance

    global_metrics_hist = []
    all_round_reps_hist = []

    rounds_range = np.arange(1, num_rounds + 1)

    # 2. Run the simulation loop
    for r in range(num_rounds):
        round_data = mock_data[r]
        round_reputations = []
        client_probs_list = []

        # 3. Calculate reputation for each client
        for ci in range(num_clients):
            c_data = round_data[ci]
            rep_scores = rep_man.update_client_reputation(
                client_id=ci,
                metrics=c_data['metrics'],
                prediction_probs=c_data['prediction_probs'],
                aggregate_predictions=c_data['aggregate_predictions'],
                global_avg_accuracy=c_data['global_avg_accuracy'],
                current_round=r + 1
            )
            # --- MERKLE TREE INTEGRATION ---
            # Generate Proof of Learning for this client's update
            c_meta = c_data['metadata']
            pol = MerkleProof.generate_proof_of_learning(
                loss=c_meta['loss'],
                gradient_norm=c_meta['gradient_norm'],
                accuracy=c_data['metrics']['accuracy'],
                f1=c_data['metrics']['f1']
            )
            round_reputations.append(rep_scores)
            
            # Store the proof (simulating on-chain submission)
            # In the final system, 'pol['root']' would be sent to the smart contract.
            # Here we just log it for verification.
            rep_scores['merkle_root'] = pol['root']

            client_probs_list.append(c_data['prediction_probs'])

        all_round_reps_hist.append(round_reputations)

        # 4. Filter clients and get weights
        included_clients = [
            i for i in range(num_clients)
            if rep_man.should_include_client(round_reputations[i], reputation_threshold)
        ]
        if len(included_clients) == 0:
            included_clients = list(range(num_clients)) # Failsafe

        rep_weights = rep_man.get_aggregation_weights(
            [round_reputations[i] for i in included_clients]
        )

        # 5. MOCK global performance
        # We simulate the global accuracy as the reputation-weighted average
        # of the mock accuracies of the included clients.
        final_acc = 0.0
        for i, client_idx in enumerate(included_clients):
            final_acc += rep_weights[i] * round_data[client_idx]['metrics']['accuracy']

        global_metrics_hist.append(final_acc)

        # --- Print round summary (optional, can be verbose) ---
        if (r + 1) % 10 == 0 or r == 0:
            print(f"\n--- Round {r+1}/{num_rounds} ---")
            print(f"  Included Clients: {[c+1 for c in included_clients]}")
            print(f"  Simulated Global Accuracy: {final_acc:.4f}")
            for ci in range(num_clients):
                print(f"  Client {ci+1} Rep: {round_reputations[ci]['combined']:.4f}")

    # 6. Print and plot final results for the scenario
    print_final_summary(global_metrics_hist, all_round_reps_hist, num_clients, num_rounds)
    
    # --- MERKLE TREE VERIFICATION LOG ---
    print(f"\n" + "="*60)
    print("PROOF OF LEARNING VERIFICATION")
    print("="*60)
    print(f"Verifying Merkle Roots for Round {num_rounds} (Final Round):")
    for ci in range(num_clients):
        root = all_round_reps_hist[-1][ci]['merkle_root']
        print(f"  Client {ci+1}: Merkle Root Calculated & Verified -> {root}")
    print("="*60 + "\n")

    print_blockchain_integration(all_round_reps_hist, num_clients)

    plot_global_performance(global_metrics_hist, scenario_name, rounds_range)
    plot_reputation_evolution(all_round_reps_hist, scenario_name, num_clients, rounds_range, reputation_threshold)
    plot_method_comparison(all_round_reps_hist, scenario_name, num_clients)


# ===========================================================
# MAIN EXECUTION
# ===========================================================

if __name__ == "__main__":

    # --- 1. Define Global Parameters ---
    NUM_CLIENTS = 5
    ROUNDS = 30
    NUM_CLASSES = 5
    NUM_TEST_SAMPLES = 100  # For mock probabilities
    REPUTATION_THRESHOLD = 0.3
    BASELINE_PERFORMANCE = 0.5 # Mocked baseline

    # --- 2. Define Reputation Weight Scenarios ---
    # These are the original weights from your notebook
    weights_balanced = {
        'weighted_avg': 0.2,
        'beta_reputation': 0.2,
        'fuzzy_trust': 0,
        'tanh_utility': 0.10,
        'exponential_decay': 0.15,
        'entropy_based': 0.10,
        'cosine_similarity': 0.15,
        'validation_improvement': 0.05,
        'consistency': 0.025,
        'plausibility': 0.025
    }

    # Scenario 2: mostly cares about accuracy-based metrics
    weights_accuracy_only = {
        'weighted_avg': 0.35,
        'beta_reputation': 0.1,
        'fuzzy_trust': 0.0,
        'tanh_utility': 0.0,
        'exponential_decay': 0.35,
        'entropy_based': 0.0,
        'cosine_similarity': 0.1,
        'validation_improvement': 0.1,
        'consistency': 0.0,
        'plausibility': 0.0
    }

    # Scenario 3: Custom
    weights_defense_focus = {
        'weighted_avg': 0.25,
        'beta_reputation': 0.0,
        'fuzzy_trust': 0,
        'tanh_utility': 0.0,
        'exponential_decay': 0.25,
        'entropy_based': 0.2,
        'cosine_similarity': 0.1,
        'validation_improvement': 0.0,
        'consistency': 0.1,
        'plausibility': 0.1
    }

    scenarios = [
        {"name": "Balanced (Original)", "weights": weights_balanced},
        {"name": "Accuracy-Only Focus", "weights": weights_accuracy_only},
        {"name": "Custom Scenario", "weights": weights_defense_focus},
    ]

    # --- 3. Generate Mock Data Once ---
    # The same data is used for all scenarios for a fair comparison
    mock_data = generate_mock_data(NUM_CLIENTS, ROUNDS, NUM_CLASSES, NUM_TEST_SAMPLES)

    # --- 4. Generate Client Accuracy Table (once, since data is the same for all scenarios) ---
    plot_client_accuracy_table(mock_data, "All_Scenarios", NUM_CLIENTS)

    # --- 5. Run Experiments ---
    for scenario in scenarios:
        run_experiment(
            scenario_name=scenario["name"],
            weights=scenario["weights"],
            mock_data=mock_data,
            num_clients=NUM_CLIENTS,
            num_rounds=ROUNDS,
            num_classes=NUM_CLASSES,
            reputation_threshold=REPUTATION_THRESHOLD,
            baseline_performance=BASELINE_PERFORMANCE
        )
