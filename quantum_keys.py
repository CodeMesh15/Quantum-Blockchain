from qiskit import QuantumCircuit, Aer, execute

def generate_quantum_key():
    # Create a quantum circuit with one qubit and one classical bit
    qc = QuantumCircuit(1, 1)
    qc.h(0)  # Apply Hadamard gate to create superposition
    qc.measure(0, 0)

    # Simulate the circuit
    backend = Aer.get_backend('qasm_simulator')
    result = execute(qc, backend, shots=1).result()
    key = list(result.get_counts().keys())[0]
    return key
