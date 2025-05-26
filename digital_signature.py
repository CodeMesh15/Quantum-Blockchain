import hashlib

def sign_data(data, private_key):
    """Simplified signing using hash + key"""
    combined = f"{data}{private_key}"
    return hashlib.sha256(combined.encode()).hexdigest()

def verify_signature(data, signature, public_key):
    expected_signature = hashlib.sha256(f"{data}{public_key}".encode()).hexdigest()
    return signature == expected_signature
