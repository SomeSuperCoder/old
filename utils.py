import ecdsa
import hashlib
import base58

import config
import binascii
import base64


def string_to_private_key(string):
    return ecdsa.SigningKey.from_string(hashlib.sha256(string.encode()).digest(), curve=ecdsa.SECP256k1)


def generate_address(public_key):
    # Step 1: Compute the SHA-256 hash of the public key
    hash_sha256 = hashlib.sha256(public_key.to_string()).digest()

    # Step 2: Compute the RIPEMD-160 hash of the SHA-256 hash
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(hash_sha256)
    hash_ripemd160 = ripemd160.digest()

    # Step 3: Add version byte to the RIPEMD-160 hash
    version_hash = b'\x00' + hash_ripemd160

    # Step 4: Compute the double SHA-256 hash of the version + RIPEMD-160 hash
    hash_sha256_2 = hashlib.sha256(hashlib.sha256(version_hash).digest()).digest()

    # Step 5: Take the first 4 bytes of the double SHA-256 hash (checksum)
    checksum = hash_sha256_2[:4]

    # Step 6: Append the checksum to the version + RIPEMD-160 hash
    address_bytes = version_hash + checksum

    # Step 7: Encode the address bytes using Base58 encoding
    bitcoin_address = base58.b58encode(address_bytes)

    return bitcoin_address.decode()


def generate_token_address(token):
    # Step 1: Compute the SHA-256 hash of the public key
    hash_sha256 = hashlib.sha256(token.serialize().encode()).digest()

    # Step 2: Compute the RIPEMD-160 hash of the SHA-256 hash
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(hash_sha256)
    hash_ripemd160 = ripemd160.digest()

    # Step 3: Add version byte to the RIPEMD-160 hash
    version_hash = b'\x00' + hash_ripemd160

    # Step 4: Compute the double SHA-256 hash of the version + RIPEMD-160 hash
    hash_sha256_2 = hashlib.sha256(hashlib.sha256(version_hash).digest()).digest()

    # Step 5: Take the first 4 bytes of the double SHA-256 hash (checksum)
    checksum = hash_sha256_2[:4]

    # Step 6: Append the checksum to the version + RIPEMD-160 hash
    address_bytes = version_hash + checksum

    # Step 7: Encode the address bytes using Base58 encoding
    bitcoin_address = base58.b58encode(address_bytes)

    return bitcoin_address.decode()


def increment_mine(target):
    hash = get_hash(target)

    while hash[:config.strict] != "0"*config.strict:
        print(hash)
        target.nonce += 1
        hash = get_hash(target)

    print(hash)
    target.hash = hash


def get_hash(target):
    return binascii.hexlify(
        hashlib.sha256(
            target.serialize(False).encode()
                       ).digest()).decode()


def sign(private_key, target):
    signature = private_key.sign(target.serialize().encode())
    signature_string = base64.b64encode(signature).decode()

    target.signature = signature_string


def verify(target):
    try:
        signature_bytes = base64.b64decode(target.signature.encode())

        is_valid = target.public_key.verify(signature_bytes, target.serialize().encode())

        return is_valid
    except ecdsa.BadSignatureError:
        return False


def send_token(private_key: str | ecdsa.SigningKey, receiver_id: str, amount: float, token=""):
    from Transaction import Transaction
    tmp = Transaction(public_key=private_key.get_verifying_key(), receiver_id=receiver_id, amount=amount, token=token)
    sign(private_key, tmp)
    return tmp


def get_token_balance(blockchain, token, address):
    balance = 0
    mints = []
    for i in blockchain.blockchain["blocks"]:
        for j in i["mints"]:
            mints.append(j)

    print(mints)
    for i in mints:
        if i["token_address"] == token.address:
            balance += i["amount"]

    print(balance)
