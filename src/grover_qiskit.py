# Grover's Algorithm - Qiskit Implementation
# Course: MA_HPQC - HES-SO MSE
# Authors: Djelal Avdyli, Ryan Dorasamy

import matplotlib
matplotlib.use('Agg')

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import numpy as np

# PARAMETERS
n_qubits = 2
target = '11'
N = 2 ** n_qubits  # Total number of states = 4

# Optimal number of iterations: π/4 * √N
optimal_iterations = 1  # For N=4: peak is at iteration 1
print(f"Optimal number of iterations: π/4 * √{N} ≈ {optimal_iterations}")

# ORACLE: marks target state by flipping its phase
def oracle(qc, target):
    if target == '11':
        qc.cz(0, 1)
    elif target == '00':
        qc.x(0); qc.x(1)
        qc.cz(0, 1)
        qc.x(0); qc.x(1)
    elif target == '01':
        qc.x(0)
        qc.cz(0, 1)
        qc.x(0)
    elif target == '10':
        qc.x(1)
        qc.cz(0, 1)
        qc.x(1)

# DIFFUSION: amplifies target state → aᵢ = 2*average - aᵢ
def diffusion(qc, n):
    for i in range(n): qc.h(i)
    for i in range(n): qc.x(i)
    qc.cz(0, 1)
    for i in range(n): qc.x(i)
    for i in range(n): qc.h(i)

# SIMULATE PROBABILITY AFTER EACH ITERATION
simulator = AerSimulator()
shots = 10000
all_states = ['00', '01', '10', '11']

# Store probabilities at each step
prob_history = {}
for state in all_states:
    prob_history[state] = []

# Iteration 0: just superposition (no oracle/diffusion yet)
qc0 = QuantumCircuit(n_qubits, n_qubits)
for i in range(n_qubits): qc0.h(i)
qc0.measure(range(n_qubits), range(n_qubits))
compiled = transpile(qc0, simulator)
counts = simulator.run(compiled, shots=shots).result().get_counts()
for state in all_states:
    prob_history[state].append(counts.get(state, 0) / shots)

print(f"\nIteration 0 (superposition only):")
for state in all_states:
    print(f"  |{state}⟩: {prob_history[state][-1]:.1%}")

# Iterations 1 to 3 (to show what happens beyond optimal)
max_iter = 3
for k in range(1, max_iter + 1):
    qc = QuantumCircuit(n_qubits, n_qubits)
    for i in range(n_qubits): qc.h(i)
    for _ in range(k):
        oracle(qc, target)
        diffusion(qc, n_qubits)
    qc.measure(range(n_qubits), range(n_qubits))
    compiled = transpile(qc, simulator)
    counts = simulator.run(compiled, shots=shots).result().get_counts()
    for state in all_states:
        prob_history[state].append(counts.get(state, 0) / shots)
    print(f"\nIteration {k}:")
    for state in all_states:
        print(f"  |{state}⟩: {prob_history[state][-1]:.1%}")

# PLOT: probability evolution per iteration
iterations = list(range(max_iter + 1))
colors = {'11': 'green', '00': 'orange', '01': 'steelblue', '10': 'salmon'}

plt.figure(figsize=(10, 6))
for state in all_states:
    style = '-o' if state == target else '--s'
    lw = 2.5 if state == target else 1.5
    plt.plot(iterations, prob_history[state],
             style, label=f'|{state}⟩', color=colors[state],
             linewidth=lw, markersize=8)

plt.axvline(x=optimal_iterations, color='red', linestyle=':', linewidth=2,
            label=f'Optimal iterations = {optimal_iterations}')
plt.xlabel('Number of Grover iterations', fontsize=13)
plt.ylabel('Probability', fontsize=13)
plt.title("Grover's Algorithm - Probability evolution per iteration\n"
          f"Target state |{target}⟩, n={n_qubits} qubits, N={N} states",
          fontsize=13)
plt.xticks(iterations)
plt.ylim(-0.05, 1.05)
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('results/grover_qiskit_evolution.png', dpi=150)
print("\nEvolution plot saved to results/grover_qiskit_evolution.png")

# FINAL CIRCUIT (optimal iterations)
qc_final = QuantumCircuit(n_qubits, n_qubits)
for i in range(n_qubits): qc_final.h(i)
qc_final.barrier()
for _ in range(optimal_iterations):
    oracle(qc_final, target)
    qc_final.barrier()
    diffusion(qc_final, n_qubits)
    qc_final.barrier()
qc_final.measure(range(n_qubits), range(n_qubits))

print("\nFinal Quantum Circuit:")
print(qc_final.draw(output='text'))

# Save final histogram
compiled_final = transpile(qc_final, simulator)
counts_final = simulator.run(compiled_final, shots=1000).result().get_counts()
fig = plot_histogram(counts_final)
fig.savefig('results/grover_qiskit_histogram.png', dpi=150)
print("Histogram saved to results/grover_qiskit_histogram.png")
