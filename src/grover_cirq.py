# =============================================================
# Grover's Algorithm - Cirq Implementation
# Course: MA_HPQC - HES-SO MSE
# Authors: Djelal Avdyli, Ryan Dorasamy
# =============================================================

import matplotlib
matplotlib.use('Agg')

import cirq
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

# =============================================================
# PARAMETERS
# =============================================================
n_qubits = 2
target = '11'
N = 2 ** n_qubits
optimal_iterations = 1  # For N=4: peak is at iteration 1
shots = 10000

print(f"Grover's Algorithm - Cirq")
print(f"Target state |{target}⟩, n={n_qubits} qubits, N={N} states")
print(f"Optimal iterations: {optimal_iterations}")

# =============================================================
# CREATE QUBITS
# In Cirq, qubits are explicit objects (unlike Qiskit)
# =============================================================
qubits = cirq.LineQubit.range(n_qubits)
q0, q1 = qubits

# =============================================================
# STEP 1: UNIFORM SUPERPOSITION
# Apply Hadamard to all qubits
# =============================================================
def create_superposition(qubits):
    return [cirq.H(q) for q in qubits]

# =============================================================
# STEP 2: ORACLE (Marking phase)
# Marks target state by flipping its phase
# For |11⟩: CZ gate directly
# =============================================================
def oracle(qubits, target):
    q0, q1 = qubits
    gates = []
    if target == '11':
        gates.append(cirq.CZ(q0, q1))
    elif target == '00':
        gates += [cirq.X(q0), cirq.X(q1)]
        gates.append(cirq.CZ(q0, q1))
        gates += [cirq.X(q0), cirq.X(q1)]
    elif target == '01':
        gates.append(cirq.X(q0))
        gates.append(cirq.CZ(q0, q1))
        gates.append(cirq.X(q0))
    elif target == '10':
        gates.append(cirq.X(q1))
        gates.append(cirq.CZ(q0, q1))
        gates.append(cirq.X(q1))
    return gates

# =============================================================
# STEP 3: DIFFUSION OPERATOR (Amplifying phase)
# Implements aᵢ = 2*average - aᵢ
# H → X → CZ → X → H
# =============================================================
def diffusion(qubits):
    q0, q1 = qubits
    return [
        cirq.H(q0), cirq.H(q1),
        cirq.X(q0), cirq.X(q1),
        cirq.CZ(q0, q1),
        cirq.X(q0), cirq.X(q1),
        cirq.H(q0), cirq.H(q1),
    ]

# =============================================================
# SIMULATE PROBABILITY AFTER EACH ITERATION
# =============================================================
simulator = cirq.Simulator()
all_states = ['00', '01', '10', '11']
prob_history = {state: [] for state in all_states}

# Iteration 0: superposition only
circuit0 = cirq.Circuit()
circuit0.append(create_superposition(qubits))
circuit0.append(cirq.measure(*qubits, key='result'))
result0 = simulator.run(circuit0, repetitions=shots)
counts0 = Counter([''.join(str(b) for b in result0.measurements['result'][i])
                   for i in range(shots)])
for state in all_states:
    prob_history[state].append(counts0.get(state, 0) / shots)

print(f"\nIteration 0 (superposition only):")
for state in all_states:
    print(f"  |{state}⟩: {prob_history[state][-1]:.1%}")

# Iterations 1 to 3
max_iter = 3
for k in range(1, max_iter + 1):
    circuit = cirq.Circuit()
    circuit.append(create_superposition(qubits))
    for _ in range(k):
        circuit.append(oracle(qubits, target))
        circuit.append(diffusion(qubits))
    circuit.append(cirq.measure(*qubits, key='result'))
    result = simulator.run(circuit, repetitions=shots)
    counts = Counter([''.join(str(b) for b in result.measurements['result'][i])
                      for i in range(shots)])
    for state in all_states:
        prob_history[state].append(counts.get(state, 0) / shots)
    print(f"\nIteration {k}:")
    for state in all_states:
        print(f"  |{state}⟩: {prob_history[state][-1]:.1%}")

# =============================================================
# PLOT: probability evolution
# =============================================================
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
plt.title("Grover's Algorithm - Probability evolution per iteration (Cirq)\n"
          f"Target state |{target}⟩, n={n_qubits} qubits, N={N} states",
          fontsize=13)
plt.xticks(iterations)
plt.ylim(-0.05, 1.05)
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('results/grover_cirq_evolution.png', dpi=150)
print("\nEvolution plot saved to results/grover_cirq_evolution.png")

# =============================================================
# PRINT FINAL CIRCUIT
# =============================================================
circuit_final = cirq.Circuit()
circuit_final.append(create_superposition(qubits))
circuit_final.append(oracle(qubits, target))
circuit_final.append(diffusion(qubits))
circuit_final.append(cirq.measure(*qubits, key='result'))

print("\nFinal Quantum Circuit (Cirq):")
print(circuit_final)
