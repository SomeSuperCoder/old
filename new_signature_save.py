import ecdsa
import base64
import hashlib
import utils

# Generate an ECDSA key pair
private_key = ecdsa.SigningKey.from_string(hashlib.sha256("lox".encode()).digest(), curve=ecdsa.SECP256k1)  # Replace with your private key

# Get the public key
public_key = private_key.get_verifying_key()
print(public_key.to_string())

# Serialize the public key to a string
public_key_str = public_key.to_pem().decode()

# Print the string representation of the public key
print(public_key_str)

print(ecdsa.VerifyingKey.from_pem(public_key_str).to_string())