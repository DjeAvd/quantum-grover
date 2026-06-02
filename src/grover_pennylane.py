# Grover's Algorithm - PennyLane Implementation
# Course: MA_HPQC - HES-SO MSE
# Authors: Djelal Avdil, Ryan Dorasamy

import matplotlib
matplotlib.use('Agg')

import pennylane as qml
import numpy as np
import matplotlib.pyplot as plt

# PARAMETERS
n_qubits = 2
target = '11'
N = 2 ** n_qubits
optimal_iterations = 1
shots = 10000

print(f"Grover's Algorithm - PennyLane")
print(f"Target state |{target}⟩, n={n_qubits} qubits, N={N} states")
print(f"Optimal iterations: {optimal_iterations}")

# DEVICE: PennyLane uses a "device" to run circuits
# default.qubit = local simulator
dev = qml.device('default.qubit', wires=n_qubits, shots=shots)

# STEP 1: UNIFORM SUPERPOSITION
def superposition():
    for i in range(n_qubits):
        qml.Hadamard(wires=i)

# STEP 2: ORACLE (Marking phase)
# Marks target state ω by flipping its phase
def oracle(target):
    if target == '11':
        qml.CZ(wires=[0, 1])
    elif target == '00':
        qml.PauliX(wires=0); qml.PauliX(wires=1)
        qml.CZ(wires=[0, 1])
        qml.PauliX(wires=0); qml.PauliX(wires=1)
    elif target == '01':
        qml.PauliX(wires=0)
        qml.CZ(wires=[0, 1])
        qml.PauliX(wires=0)
    elif target == '10':
        qml.PauliX(wires=1)
        qml.CZ(wires=[0, 1])
        qml.PauliX(wires=1)

# STEP 3: DIFFUSION OPERATOR (Amplifying phase)
# Implements aᵢ = 2*average - aᵢ
def diffusion():
    for i in range(n_qubits):
        qml.Hadamard(wires=i)
    for i in range(n_qubits):
        qml.PauliX(wires=i)
    qml.CZ(wires=[0, 1])
    for i in range(n_qubits):
        qml.PauliX(wires=i)
    for i in range(n_qubits):
        qml.Hadamard(wires=i)

# BUILD GROVER CIRCUIT AS A PENNYLANE QNODE
# In PennyLane, circuits are decorated functions (@qml.qnode)
def make_circuit(n_iter):
    @qml.qnode(dev)
    def grover_circuit():
        # Step 1: Superposition
        superposition()
        # Step 2 & 3: Grover iterations
        for _ in range(n_iter):
            oracle(target)
            diffusion()
        # Measurement
        return qml.probs(wires=range(n_qubits))
    return grover_circuit

# SIMULATE PROBABILITY AFTER EACH ITERATION
all_states = ['00', '01', '10', '11']
prob_history = {state: [] for state in all_states}

for k in range(4):  # 0 to 3
    circuit = make_circuit(k)
    probs = circuit()
    # PennyLane returns probs in order: |00⟩, |01⟩, |10⟩, |11⟩
    for idx, state in enumerate(all_states):
        prob_history[state].append(float(probs[idx]))
    print(f"\nIteration {k}:")
    for idx, state in enumerate(all_states):
        print(f"  |{state}⟩: {float(probs[idx]):.1%}")

# PLOT: probability evolution
iterations = list(range(4))
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
plt.title("Grover's Algorithm - Probability evolution per iteration (PennyLane)\n"
          f"Target state |{target}⟩, n={n_qubits} qubits, N={N} states",
          fontsize=13)
plt.xticks(iterations)
plt.ylim(-0.05, 1.05)
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('results/grover_pennylane_evolution.png', dpi=150)
print("\nEvolution plot saved to results/grover_pennylane_evolution.png")

# PRINT CIRCUIT DIAGRAM
circuit_final = make_circuit(optimal_iterations)
print("\nFinal Quantum Circuit (PennyLane):")
print(qml.draw(circuit_final)())
