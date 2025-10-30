# zeno.py
import math
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator


def apply_zeno_measurements(n_qubits: int, target_indices: list[int], num_measurements: int = 10) -> dict:
    """
    Apply the quantum Zeno effect through frequent measurements.
    This "freezes" the target states, making them less likely to be measured
    in a Grover search (the Zeno paradox: a watched pot never boils).
    
    Args:
        n_qubits: Number of qubits in the quantum system
        target_indices: List of state indices to protect with Zeno effect
        num_measurements: Number of intermediate measurements (more = stronger protection)
    
    Returns:
        Dictionary containing Zeno effect parameters for use in modified Grover searches
    """
    
    if not target_indices:
        raise ValueError("At least one target index must be provided for Zeno protection.")
    
    if num_measurements < 1:
        raise ValueError("Number of measurements must be at least 1.")
    
    N = 2 ** n_qubits
    M = len(target_indices)
    
    # Build a circuit that demonstrates the Zeno effect
    qc = QuantumCircuit(n_qubits, name="zeno_effect")
    
    # Initialize superposition
    qc.h(range(n_qubits))
    
    # Apply Zeno-like measurements: collapse and restore operations
    # This demonstrates how frequent measurements inhibit quantum evolution
    for measurement_round in range(num_measurements):
        # Create projection operators for protected states
        for target in target_indices:
            binary_target = format(target, f'0{n_qubits}b')
            
            # X gates to prepare for selective measurement
            for i, bit in enumerate(reversed(binary_target)):
                if bit == '0':
                    qc.x(i)
            
            # Apply Hadamard to last qubit for measurement-like operation
            qc.h(n_qubits - 1)
            
            # Multi-controlled operation (projection-like)
            if n_qubits > 1:
                qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
            
            qc.h(n_qubits - 1)
            
            # Uncompute X gates
            for i, bit in enumerate(reversed(binary_target)):
                if bit == '0':
                    qc.x(i)
        
        # Add a small evolution step between measurements
        if measurement_round < num_measurements - 1:
            qc.rx(0.1, 0)  # Small rotation to simulate evolution
    
    # Simulate to get Zeno effect statistics
    sim = AerSimulator()
    qc.measure_all()
    result = sim.run(qc, shots=1000).result()
    counts = result.get_counts()
    
    # Calculate protection strength: probability of measuring protected states
    protected_prob = 0
    for target in target_indices:
        state_str = format(target, f'0{n_qubits}b')
        protected_prob += counts.get(state_str, 0)
    
    protected_prob /= 1000.0  # Normalize to shots
    
    # Zeno effect parameters
    zeno_params = {
        "active": True,
        "protected_indices": target_indices,
        "protection_strength": max(0.1, min(0.5, protected_prob)),  # Clamp between 0.1 and 0.5
        "num_measurements": num_measurements,
        "measurement_decay": 0.95,  # Decay factor per Grover iteration
        "description": f"Quantum Zeno effect protects {len(target_indices)} ships with {num_measurements} measurements"
    }
    
    return zeno_params


def calculate_zeno_reduced_amplitude(target_index: int, zeno_params: dict, current_iteration: int) -> float:
    """
    Calculate the amplitude reduction for a Grover search due to Zeno protection.
    
    Args:
        target_index: Index of the state being queried
        zeno_params: Dictionary returned from apply_zeno_measurements
        current_iteration: Current iteration number in Grover's algorithm
    
    Returns:
        Amplitude reduction factor (0.0 to 1.0, where lower = more protected)
    """
    
    if not zeno_params.get("active"):
        return 1.0
    
    if target_index not in zeno_params.get("protected_indices", []):
        return 1.0
    
    # Calculate decay: protection weakens as Grover iterates
    decay = zeno_params["measurement_decay"] ** current_iteration
    
    # Protection strength provides a floor
    protection_floor = zeno_params["protection_strength"]
    
    # Result is a blend of protection strength and decay
    reduction = protection_floor + (1.0 - protection_floor) * decay
    
    return min(1.0, reduction)


def build_zeno_protected_oracle(n_qubits: int, target_indices: list[int], zeno_params: dict = None) -> QuantumCircuit:
    """
    Build an oracle that accounts for Zeno-protected ships.
    Protected ships have reduced oracle phase flips due to measurement inhibition.
    
    Args:
        n_qubits: Number of qubits
        target_indices: List of ship positions
        zeno_params: Zeno effect parameters (if None, creates default)
    
    Returns:
        Quantum circuit implementing the Zeno-aware oracle
    """
    
    if zeno_params is None:
        zeno_params = {"active": False, "protected_indices": []}
    
    qc = QuantumCircuit(n_qubits, name="zeno_oracle")
    
    for target_index in target_indices:
        binary_target = format(target_index, f'0{n_qubits}b')
        
        # For Zeno-protected ships, reduce the phase flip impact
        if zeno_params.get("active") and target_index in zeno_params.get("protected_indices", []):
            # Use partial phase application instead of full phase flip
            # This simulates the "freeze" effect
            qc.rz(math.pi / 2, range(n_qubits))  # Reduced rotation
        else:
            # Normal oracle phase flip for unprotected ships
            # Flip qubits for bits that are 0
            for i, bit in enumerate(reversed(binary_target)):
                if bit == '0':
                    qc.x(i)
            
            # Multi-controlled Z
            qc.h(n_qubits - 1)
            qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
            qc.h(n_qubits - 1)
            
            # Uncompute X gates
            for i, bit in enumerate(reversed(binary_target)):
                if bit == '0':
                    qc.x(i)
    
    return qc


if __name__ == "__main__":
    # Example: Protect 3 ships with Zeno effect
    n_qubits = 4
    protected_ships = [3, 7, 12]
    
    print("Applying Quantum Zeno Effect...")
    zeno_params = apply_zeno_measurements(n_qubits, protected_ships, num_measurements=15)
    print(f"\nZeno Parameters: {zeno_params}")
    
    print("\nAmplitude reductions over iterations:")
    for iteration in range(5):
        for ship in protected_ships:
            reduction = calculate_zeno_reduced_amplitude(ship, zeno_params, iteration)
            print(f"  Iteration {iteration}, Ship {ship}: {reduction:.3f}")