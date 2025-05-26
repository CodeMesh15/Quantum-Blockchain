import numpy as np
from qiskit import QuantumCircuit, Aer, execute
import random
import hashlib
import time

class QuantumResistantBlockchain:
    def __init__(self, num_nodes, num_candidates):
        self.num_nodes = num_nodes
        self.num_candidates = num_candidates
        self.blockchain = []
        self.keys = self.generate_post_quantum_keys()

    def generate_post_quantum_keys(self):
        """Generate hash-based post-quantum keys for all nodes."""
        keys = {}
        for node in range(self.num_nodes):
            private_key = self.generate_hash_private_key()
            public_key = self.generate_hash_public_key(private_key)
            keys[node] = (private_key, public_key)
        return keys

    def generate_hash_private_key(self):
        """Generate a private key for Lamport signatures."""
        private_key = [[random.getrandbits(256).to_bytes(32, 'big') for _ in range(256)] for _ in range(2)]
        return private_key

    def generate_hash_public_key(self, private_key):
        """Generate a public key by hashing the private key components."""
        public_key = [[hashlib.sha256(pk).digest() for pk in pair] for pair in private_key]
        return public_key

    def hash_message(self, message):
        """Hash a message to a 256-bit digest."""
        return hashlib.sha256(message.encode()).digest()

    def sign_message(self, message, private_key):
        """Sign a message using Lamport one-time signature."""
        hashed_message = self.hash_message(message)
        signature = [private_key[bit][i] for i, bit in enumerate(hashed_message)]
        return signature

    def verify_signature(self, message, signature, public_key):
        """Verify a Lamport signature using the public key."""
        hashed_message = self.hash_message(message)
        for i, bit in enumerate(hashed_message):
            if hashlib.sha256(signature[i]).digest() != public_key[bit][i]:
                return False
        return True

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

            _, public_key = self.keys[sender]
            if self.verify_signature(message, signature, public_key):
                valid_transactions.append(transaction)

        if len(valid_transactions) >= len(transactions) * 2 / 3:  # Require 2/3 majority validation
            previous_hash = self.blockchain[-1]["header"]["block_hash"] if self.blockchain else "0"
            new_block = self.create_block(valid_transactions, previous_hash)
            self.blockchain.append(new_block)
            print("Block added to the blockchain.")
        else:
            print("Block validation failed.")

    def display_blockchain(self):
        """Display the blockchain."""
        for i, block in enumerate(self.blockchain):
            print(f"Block {i}:")
            print(block)

# Example Usage
if __name__ == "__main__":
    # Initialize quantum-resistant blockchain parameters
    num_nodes = 10
    num_candidates = 6

    # Create a quantum-resistant blockchain instance
    qr_blockchain = QuantumResistantBlockchain(num_nodes, num_candidates)

    # Simulate voting with behavior weights
    malicious_behavior_weights = [0.9, 0.8, 1.0, 0.7, 0.6, 0.5]  # Higher weight = better behavior
    selected_nodes = qr_blockchain.simulate_voting(malicious_behavior_weights)
    print(f"Selected Witness Nodes: {selected_nodes}")

    # Generate sample transactions
    transactions = []
    for sender in range(2):
        message = f"Message from node {sender}"
        private_key, _ = qr_blockchain.keys[sender]
        signature = qr_blockchain.sign_message(message, private_key)
        transactions.append({"sender": sender, "message": message, "signature": signature})

    # Validate and add a block
    qr_blockchain.validate_and_add_block(transactions, selected_nodes)

    # Display the blockchain
    qr_blockchain.display_blockchain()
