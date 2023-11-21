import ecdsa
import hashlib
import base58
import config
import binascii
import base64
import math
import random

from typing import List

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

    return "nc" + bitcoin_address.decode()


def generate_serializable_address(token):
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

    return "sr" + bitcoin_address.decode()


def increment_mine(target):
    hash = get_hash(target)

    while hash[:config.strict] != "0"*config.strict:
        print(f"Hash: {hash} Try №{target.nonce}")
        target.nonce += 1
        hash = get_hash(target)

    print("\r" + hash)
    target.hash = hash


def random_mine(target):
    hash = get_hash(target)
    i = 1

    while hash[:config.strict] != "0" * config.strict:
        print(f"Hash: {hash} Try №{i}")
        target.nonce = random.randint(0, math.pow(10, 308))
        i += 1
        hash = get_hash(target)

    print("\r" + hash)
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


def array_minus_array(first_array, second_array):
    return [x for x in first_array if x not in second_array]


# def validate_transaction_inputs(transactions):
#     for tr in transactions:
#         input_objects = [i for i in transactions if i.address in tr.inputs]
#         input_amount = 0
#         for j in input_objects:
#             input_amount += j.amount
#
#         print(input_objects)
#         print(input_amount)

def get_all_unspent_outputs(blockchain):
    from Block import NewBlock

    outputs = {}
    inputs = []
    pre_result = {}
    result = []

    for i in range(len(blockchain.blockchain["blocks"])):
        one: dict = blockchain.blockchain["blocks"][i]
        block_object = NewBlock.from_dict(one)

        for tr in block_object.transactions:
            outputs[tr.address] = []
            for output in tr.outputs:
                outputs[tr.address].append(output)

            for _input in tr.inputs:
                inputs.append(_input)

    # print(inputs)
    # print(outputs)
    for out_transaction_address, out_list in outputs.items():
        # print(f"Processing {out_transaction_address}")

        for _in in inputs:
            if out_transaction_address == _in.transaction_address:
                tmp_out_list = out_list
                tmp_out_list.pop(_in.output_index)
                pre_result[out_transaction_address] = tmp_out_list
            else:
                pre_result[out_transaction_address] = out_list

    # print(pre_result)

    # for address, output in pre_result.items():
    #     if outputs[address] != []:
    #         for out in output:
    #             result.append(Input(address, [i.serialize() for i in outputs[address]].index(out.serialize())))
    for address, pre_result_outputs in pre_result.items():
        index = 0
        for out in pre_result_outputs:
            result.append([out, address, index])
            index += 1

    # print(f"result: {result}")
    # print(f"result2: {[i.serialize() for i in result]}")
    return result


def get_potential_inputs(blockchain, user_public_key, token_address="", target_amount=math.inf):
    from Transaction import Input
    outputs_format = get_all_unspent_outputs(blockchain)

    current_amount = 0
    result = []
    for i in outputs_format:
        if current_amount >= target_amount:
            print("Breaking!")
            break
        if i[0].to == generate_address(user_public_key):
            if i[0].token_address == token_address:
                result.append(Input(i[1], i[2]))
                current_amount += i[0].amount

    return result


def send_token(blockchain, user_private_key: ecdsa.SigningKey, to, amount, token_address=""):
    from Transaction import Transaction, Output, Input
    from Block import NewBlock
    inputs: List[Input] = get_potential_inputs(blockchain, user_private_key.get_verifying_key(), token_address, target_amount=amount)
    outputs: List[Output] = []
    all_blockchain_transaction_outputs = {}

    for i in range(len(blockchain.blockchain["blocks"])):
        one: dict = blockchain.blockchain["blocks"][i]
        block_object = NewBlock.from_dict(one)
        for tr in block_object.transactions:
            all_blockchain_transaction_outputs[tr.address] = []
            for out in tr.outputs:
                all_blockchain_transaction_outputs[tr.address].append(out)

    input_sum = 0
    output_sum = 0

    for _in in inputs:
        input_sum += all_blockchain_transaction_outputs[_in.transaction_address][_in.output_index].amount

    if token_address == "":
        outputs.append(Output(to, amount, token_address))

    for out in outputs:
        output_sum += out.amount

    outputs.append(Output(generate_address(user_private_key.get_verifying_key()), input_sum - output_sum, token_address))

    new_transaction = Transaction(public_key=user_private_key.get_verifying_key(), inputs=inputs, outputs=outputs)
    sign(private_key=user_private_key, target=new_transaction)
    print(f"Input sum: {input_sum}")
    print(f"Output sum: {output_sum}")

    return new_transaction

def get_token_balance():
    pass
