import ecdsa
import hashlib
import base58

import config
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
    return hashlib.sha256(target.serialize(False).encode()).hexdigest()


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

    print(inputs)
    print(outputs)
    for out_transaction_address, out_list in outputs.items():
        print(f"Processing {out_transaction_address}")

        for _in in inputs:
            if out_transaction_address == _in.transaction_address:
                tmp_out_list = out_list
                tmp_out_list.pop(_in.output_index)
                pre_result[out_transaction_address] = tmp_out_list
            else:
                pre_result[out_transaction_address] = out_list
        else:
            pre_result[out_transaction_address] = out_list

    print(pre_result)

    for address, pre_result_outputs in pre_result.items():
        index = 0
        for out in pre_result_outputs:
            result.append([out, address, index])
            index += 1
    # do not use these prints
    print(f"result: {result}")
    print(f"result2: {[i[0].serialize() for i in result]}")
    return result


def get_potential_inputs(blockchain, user_public_key, token_address="", target_amount=math.inf):
    print("Begin get_potential_inputs")
    from Transaction import Input
    outputs_format = get_all_unspent_outputs(blockchain)
    print(outputs_format)
    print("="*10)
    for i in outputs_format:
        print(i[0].serialize())
    print("="*10)


    current_amount = 0
    result = []
    for i in outputs_format:
        print("For!")
        print(current_amount)
        print(target_amount)
        print(current_amount >= target_amount)
        if current_amount >= target_amount:
            print("Breaking!")
            break
        print(f"To: {i[0].to}")
        print(f"Address: {generate_address(user_public_key)}")
        if i[0].to == generate_address(user_public_key):
            print("If1")
            print(i[0].token_address)
            print(token_address)
            if i[0].token_address == token_address:
                result.append(Input(i[1], i[2]))
                print("Append!")
                current_amount += i[0].amount

    return result


def send_token(blockchain, user_private_key: ecdsa.SigningKey, to, amount, token_address=""):
    from Transaction import Transaction, Output, Input
    from Block import NewBlock
    from Token import NewToken
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

    outputs.append(Output(to, amount, token_address, "send"))
    if token_address != "":
        for tk in blockchain.get_token_list():
            tk: NewToken = tk
            if tk.burn:
                outputs.append(Output("", amount * tk.burn, token_address, "burn"))
            if tk.commission:
                outputs.append(Output(generate_address(tk.public_key), amount * tk.commission, token_address, "commission"))

    for out in outputs:
        output_sum += out.amount

    outputs.append(Output(generate_address(user_private_key.get_verifying_key()), input_sum - output_sum, token_address, type="return"))

    new_transaction = Transaction(public_key=user_private_key.get_verifying_key(), inputs=inputs, outputs=outputs)
    sign(private_key=user_private_key, target=new_transaction)
    print(f"Input sum: {input_sum}")
    print(f"Output sum: {output_sum}")

    return new_transaction


def get_token_balance(blockchain, public_key: ecdsa.VerifyingKey, token_address=""):
    balance = 0
    inputs = get_potential_inputs(blockchain, public_key, token_address)
    print(inputs)
    for _in in inputs:
        out = input_to_output(blockchain, _in)
        if out.type not in ["burn", "gas"]:
            if out.token_address == token_address:
                if out.to == generate_address(public_key):
                    balance += out.amount

    return balance


def create_token_transaction(blockchain, private_key: ecdsa.SigningKey, token):
    from Transaction import Transaction, Output

    new_transaction = Transaction(private_key.get_verifying_key(),
                                  get_potential_inputs(blockchain,
                                                       private_key.get_verifying_key(),
                                                       target_amount=config.creation_gas_fee),
                                  [Output("", config.creation_gas_fee, "", "gas")],
                                  tokens=[token])

    sign(private_key, new_transaction)

    return new_transaction


def public_key_to_string(public_key: ecdsa.VerifyingKey):
    der = public_key.to_der()
    return base64.b64encode(der).decode()


def string_to_public_key(string):
    der = base64.b64decode(string)
    return ecdsa.VerifyingKey.from_der(der)


def sort_outputs_by_type(data):
    result = {}

    for obj in data:
        obj_type = obj.type
        if obj_type in result:
            result[obj_type].append(obj)
        else:
            result[obj_type] = [obj]

    return result


def sort_outputs_by_token(data):
    result = {}

    for obj in data:
        obj_type = obj.token_address
        if obj_type in result:
            result[obj_type].append(obj)
        else:
            result[obj_type] = [obj]

    return result


def get_block_outputs(block):
    from Block import NewBlock
    block: NewBlock = block

    result = []

    for tr in block.transactions:
        for out in tr.outputs:
            result.append(out)

    return result


def input_to_output(blockchain, input):
    from Block import NewBlock
    from Transaction import Transaction
    for block in blockchain.blockchain["blocks"]:
        block = NewBlock.from_dict(block)
        for tr in block.transactions:
            tr: Transaction = tr
            if tr.address == input.transaction_address:
                return tr.outputs[input.output_index]
