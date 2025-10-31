import math
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


# -------------------------------------------------------------------
# 🧠 Oracle — marks one or more hidden ships (target states)
# -------------------------------------------------------------------
def build_oracle(n_qubits: int, target_indices: list[int]) -> QuantumCircuit:
    """
    Oracle that flips the phase of each marked (ship) state.
    """
    qc = QuantumCircuit(n_qubits)

    for target_index in target_indices:
        binary_target = format(target_index, f'0{n_qubits}b')

        # Flip qubits for bits that are 0 so that the mcx hits only |target>
        for i, bit in enumerate(reversed(binary_target)):
            if bit == '0':
                qc.x(i)

        # Multi-controlled Z (implemented as H–MCX–H on the last qubit)
        qc.h(n_qubits - 1)
        qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
        qc.h(n_qubits - 1)

        # Uncompute the X gates
        for i, bit in enumerate(reversed(binary_target)):
            if bit == '0':
                qc.x(i)

    return qc


# -------------------------------------------------------------------
# 💫 Diffuser (inversion about the mean)
# -------------------------------------------------------------------
def build_diffuser(n_qubits: int) -> QuantumCircuit:
    qc = QuantumCircuit(n_qubits)
    qc.h(range(n_qubits))
    qc.x(range(n_qubits))
    qc.h(n_qubits - 1)
    qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    qc.h(n_qubits - 1)
    qc.x(range(n_qubits))
    qc.h(range(n_qubits))
    return qc


# -------------------------------------------------------------------
# 🚀 Run Grover’s algorithm for one shot on possibly multiple ships
# -------------------------------------------------------------------
def grover_shot(n_qubits: int, target_indices: list[int], shots: int = 1):
    """
    Run Grover's search for one or more targets (ships).

    Returns a dictionary with:
      - 'hit': True/False
      - 'measured_index': int (most probable state)
      - 'measured_state': str (bitstring)
      - 'iterations': number of Grover iterations used
      - 'counts': full measurement results
    """
    if not target_indices:
        raise ValueError("At least one target index (ship) must be provided.")

    M = len(target_indices)            # number of marked states
    N = 2 ** n_qubits                  # total states

    # 🧮 Use half of the optimal iterations (for gameplay uncertainty)
    n_iterations = max(1, int(math.floor((math.pi / 4) * math.sqrt(N / M))))

    # --- Build the quantum circuit ---
    oracle = build_oracle(n_qubits, target_indices)
    diffuser = build_diffuser(n_qubits)

    qc = QuantumCircuit(n_qubits)
    qc.h(range(n_qubits))  # uniform superposition

    for _ in range(n_iterations):
        qc.compose(oracle, inplace=True)
        qc.compose(diffuser, inplace=True)

    qc.measure_all()

    # --- Run on simulator ---
    sim = AerSimulator()
    result = sim.run(qc, shots=shots).result()
    counts = result.get_counts()

    # --- Extract measured state ---
    measured_state = max(counts, key=counts.get)
    measured_index = int(measured_state, 2)
    hit = measured_index in target_indices

    return {
        "hit": hit,
        "measured_index": measured_index,
        "measured_state": measured_state,
        "iterations": n_iterations,
        "counts": counts,
    }


# -------------------------------------------------------------------
# 🧩 Standalone test
# -------------------------------------------------------------------
if __name__ == "__main__":
    # Example: 5 qubits (32 possible cells), hidden ship at cell index 13
    n_qubits = 4          # 16 possible positions
    target_indices = [3, 9]  # two ships
    result = grover_shot(n_qubits, target_indices)
    print(result)
