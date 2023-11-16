import ecdsa

# Generate a new private key
private_key = ecdsa.SigningKey.generate()

# Generate a public key from the private key
public_key = private_key.get_verifying_key()

# Sign a message
message = b"Hello, world!"
signature = private_key.sign(message)

# Save the signature to a file
with open("signature.bin", "wb") as file:
    file.write(signature)

# Load the signature from the file
with open("signature.bin", "rb") as file:
    loaded_signature = file.read()

# Validate the signature
is_valid = public_key.verify(loaded_signature, message)
print(f"Signature is valid: {is_valid}")
