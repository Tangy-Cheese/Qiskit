# Minimal Grover + Zeno effect simulation using Qiskit's DensityMatrix utilities.
# The "Zeno" step performs a partial dephasing (weak measurement) between the
# marked-subspace and its complement, suppressing amplitude amplification when strong/frequent.

import math
import numpy as np
from qiskit.quantum_info import DensityMatrix

def bitstring_to_index(bitstring: str) -> int:
    return int(bitstring, 2)

def uniform_density(n: int) -> np.ndarray:
    N = 2**n
    psi = np.ones(N, dtype=complex) / math.sqrt(N)
    rho = np.outer(psi, psi.conj())
    return rho

def oracle_unitary(n: int, target_index: int) -> np.ndarray:
    N = 2**n
    U = np.eye(N, dtype=complex)
    U[target_index, target_index] = -1.0
    return U

def diffuser_unitary(n: int) -> np.ndarray:
    N = 2**n
    s = np.ones(N, dtype=complex) / math.sqrt(N)
    P = np.outer(s, s.conj())
    D = 2 * P - np.eye(N, dtype=complex)
    return D

def projector_for_indices(n: int, indices) -> np.ndarray:
    N = 2**n
    P = np.zeros((N, N), dtype=complex)
    for i in indices:
        e = np.zeros(N, dtype=complex)
        e[i] = 1.0
        P += np.outer(e, e.conj())
    return P

def apply_zeno_dephasing(rho: np.ndarray, projector: np.ndarray, strength: float) -> np.ndarray:
    """
    Partial projective measurement that dephases coherences between subspaces:
    Full projective measurement map: rho -> P rho P + (I-P) rho (I-P)
    Weak (lambda in [0,1]) interpolation:
      rho' = (1-lambda) * rho + lambda * (P rho P + (I-P) rho (I-P))
    This preserves trace and gradually kills off-diagonal terms between the two subspaces.
    """
    I = np.eye(rho.shape[0], dtype=complex)
    Q = I - projector
    measured = projector @ rho @ projector + Q @ rho @ Q
    return (1.0 - strength) * rho + strength * measured

def run_grover_with_zeno_qiskit(n: int,
                                target_index: int,
                                iterations: int = None,
                                zeno_strength: float = 0.0,
                                observations_per_iteration: int = 0):
    """
    Simulate Grover iterations on a density matrix with optional Zeno-style partial
    observations applied after the oracle in each iteration.

    - n: qubits
    - target_index: integer index of marked state
    - iterations: number of Grover iterations (default: floor(pi/4*sqrt(N)))
    - zeno_strength: in [0,1], 0=no effect, 1=full projective measurement
    - observations_per_iteration: number of repeated weak measurements per iteration
    """
    N = 2**n
    if iterations is None:
        iterations = math.floor((math.pi/4) * math.sqrt(N))

    Uo = oracle_unitary(n, target_index)
    Ud = diffuser_unitary(n)
    P = projector_for_indices(n, [target_index])

    rho = uniform_density(n)

    for _ in range(iterations):
        # Oracle
        rho = Uo @ rho @ Uo.conj().T

        # Zeno: repeated weak dephasing (partial measurements)
        for _ in range(observations_per_iteration):
            rho = apply_zeno_dephasing(rho, P, zeno_strength)

        # Diffuser
        rho = Ud @ rho @ Ud.conj().T

    # wrap into Qiskit's DensityMatrix if user wants to inspect via Qiskit types
    dm = DensityMatrix(rho)
    probs = np.real(np.diag(dm.data))
    return probs

if __name__ == "__main__":
    # Demo: compare plain Grover vs Grover with Zeno partial observations
    n = 4
    target = bitstring_to_index("1000")
    N = 2**n
    R = math.floor((math.pi/4) * math.sqrt(N))

    probs_plain = run_grover_with_zeno_qiskit(n, target, iterations=R,
                                              zeno_strength=0.0, observations_per_iteration=0)

    # tune zeno_strength and observations_per_iteration to model stronger/more frequent observations
    probs_zeno = run_grover_with_zeno_qiskit(n, target, iterations=R,
                                             zeno_strength=0.25, observations_per_iteration=4)

    def pretty_top(probs, k=6):
        idx = np.argsort(probs)[::-1][:k]
        return [(format(i, f"0{n}b"), probs[i]) for i in idx]

    print(f"Grover iterations: {R}, target: 1000 (index {target})\n")
    print("Top results (plain Grover):")
    for b, p in pretty_top(probs_plain):
        print(f"  {b}  p={p:.4f}")

    print("\nTop results (with Zeno):")
    for b, p in pretty_top(probs_zeno):
        print(f"  {b}  p={p:.4f}")

    print("\nTarget probability plain: {:.4f}".format(probs_plain[target]))
    print("Target probability with Zeno: {:.4f}".format(probs_zeno[target]))