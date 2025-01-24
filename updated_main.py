import numpy as np
from qiskit import QuantumCircuit, Aer, execute
import random
import hashlib
import time

class QuantumBlockchain:
    def __init__(self, num_qubits, num_nodes, num_candidates):
        self.num_qubits = num_qubits
        self.num_nodes = num_nodes
        self.num_candidates = num_candidates
        self.blockchain = []
        self.keys = self.generate_keys()

    def generate_keys(self):
        """Generate quantum keys for all nodes."""
        keys = {}
        for node in range(self.num_nodes):
            keys[node] = self.generate_quantum_key(self.num_qubits)
        return keys

    def generate_quantum_key(self, num_qubits):
        """Generate a quantum key represented as quantum states."""
        qc = QuantumCircuit(num_qubits)
        for qubit in range(num_qubits):
            qc.h(qubit)  # Apply Hadamard gate for superposition
        return qc

    def generate_signature(self, message, private_key):
        """Generate a quantum signature using the private key."""
        num_qubits = len(message)
        qc = QuantumCircuit(num_qubits)
        for i, bit in enumerate(message):
            if bit == '1':
                qc.x(i)  # Apply X gate for '1'
        qc.compose(private_key, inplace=True)
        return qc

    def verify_signature(self, message, signature, public_key):
        """Verify the signature using the public key."""
        num_qubits = len(message)
        reconstructed_signature = QuantumCircuit(num_qubits)
        for i, bit in enumerate(message):
            if bit == '1':
                reconstructed_signature.x(i)  # Apply X gate for '1'
        reconstructed_signature.compose(public_key, inplace=True)

        backend = Aer.get_backend('statevector_simulator')
        result = execute(signature, backend).result()
        statevector_signature = result.get_statevector()

        result_public = execute(reconstructed_signature, backend).result()
        statevector_reconstructed = result_public.get_statevector()

        return np.allclose(statevector_signature, statevector_reconstructed)

    def simulate_voting(self, malicious_behavior_weights):
        """Simulate node voting and calculate Borda scores for candidate nodes."""
        votes = {candidate: 0 for candidate in range(self.num_candidates)}

        for voter in range(self.num_nodes):
            # Randomly vote based on behavior weights
            preference = sorted(range(self.num_candidates), key=lambda x: random.random() * malicious_behavior_weights[x])
            for rank, candidate in enumerate(preference):
                votes[candidate] += self.num_candidates - rank  # Borda scoring

        # Sort candidates by votes
        sorted_candidates = sorted(votes.items(), key=lambda item: item[1], reverse=True)
        return sorted_candidates[:int(self.num_candidates / 2)]  # Return top candidates

    def create_block(self, transactions, previous_hash="0"):
        """Create a new block for the blockchain."""
        timestamp = time.time()
        block = {
            "header": {
                "previous_hash": previous_hash,
                "timestamp": timestamp
            },
            "body": {
                "transactions": transactions
            }
        }
        # Hash the block for immutability
        block_hash = hashlib.sha256(str(block).encode()).hexdigest()
        block["header"]["block_hash"] = block_hash
        return block

    def validate_and_add_block(self, transactions, witness_nodes):
        """Validate transactions and add a new block to the blockchain."""
        valid_transactions = []
        for transaction in transactions:
            sender = transaction["sender"]
            message = transaction["message"]
            signature = transaction["signature"]

            public_key = self.keys[sender]
            if self.verify_signature(message, signature, public_key):
                valid_transactions.append(transaction)

        if len(valid_transactions) >= len(transactions) * 2 / 3:  # Require 2/3 majority validation
            previous_hash = self.blockchain[-1]["header"]["block_hash"] if self.blockchain else "0"
            new_block = self.create_block(valid_transactions, previous_hash)
            self.blockchain.append(new_block)
            print("Block added to the blockchain.")
        else:
            print("Block validation failed.")

    def quantum_key_distribution(self, num_qubits):
        """Simulate quantum key distribution (QKD) using the BB84 protocol."""
        sender_key = ""
        receiver_key = ""

        # Sender generates random key and basis
        sender_bits = np.random.randint(2, size=num_qubits)
        sender_basis = np.random.choice(["X", "Z"], size=num_qubits)

        # Receiver chooses random basis
        receiver_basis = np.random.choice(["X", "Z"], size=num_qubits)

        for bit, s_basis, r_basis in zip(sender_bits, sender_basis, receiver_basis):
            if s_basis == r_basis:  # Basis match, key bit is valid
                sender_key += str(bit)
                receiver_key += str(bit)
            else:  # Basis mismatch, discard the bit
                continue

        print("QKD Sender Key:", sender_key)
        print("QKD Receiver Key:", receiver_key)
        return sender_key, receiver_key

    def quantum_entanglement_verification(self):
        """Simulate quantum entanglement verification for secure communication."""
        qc = QuantumCircuit(2)
        qc.h(0)  # Create superposition on qubit 0
        qc.cx(0, 1)  # Entangle qubit 0 with qubit 1

        backend = Aer.get_backend('statevector_simulator')
        result = execute(qc, backend).result()
        statevector = result.get_statevector()

        print("Entangled State Vector:", statevector)
        return statevector

    def display_blockchain(self):
        """Display the blockchain."""
        for i, block in enumerate(self.blockchain):
            print(f"Block {i}:")
            print(block)

# Example Usage
if __name__ == "__main__":
    # Initialize quantum blockchain parameters
    num_qubits = 3
    num_nodes = 10
    num_candidates = 6

    # Create a quantum blockchain instance
    q_blockchain = QuantumBlockchain(num_qubits, num_nodes, num_candidates)

    # Simulate voting with behavior weights
    malicious_behavior_weights = [0.9, 0.8, 1.0, 0.7, 0.6, 0.5]  # Higher weight = better behavior
    selected_nodes = q_blockchain.simulate_voting(malicious_behavior_weights)
    print(f"Selected Witness Nodes: {selected_nodes}")

    # Generate sample transactions
    transactions = [
        {
            "sender": 0,
            "message": "101",
            "signature": q_blockchain.generate_signature("101", q_blockchain.keys[0])
        },
        {
            "sender": 1,
            "message": "110",
            "signature": q_blockchain.generate_signature("110", q_blockchain.keys[1])
        }
    ]

    # Validate and add a block
    q_blockchain.validate_and_add_block(transactions, selected_nodes)

    # Perform Quantum Key Distribution
    q_blockchain.quantum_key_distribution(num_qubits)

    # Perform Quantum Entanglement Verification
    q_blockchain.quantum_entanglement_verification()

    # Display the blockchain
    q_blockchain.display_blockchain()
