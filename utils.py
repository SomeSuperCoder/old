import datetime

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
    version_hash = config.chain_id + hash_ripemd160

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
    version_hash = config.chain_id + hash_ripemd160

    # Step 4: Compute the double SHA-256 hash of the version + RIPEMD-160 hash
    hash_sha256_2 = hashlib.sha256(hashlib.sha256(version_hash).digest()).digest()

    # Step 5: Take the first 4 bytes of the double SHA-256 hash (checksum)
    checksum = hash_sha256_2[:4]

    # Step 6: Append the checksum to the version + RIPEMD-160 hash
    address_bytes = version_hash + checksum

    # Step 7: Encode the address bytes using Base58 encoding
    bitcoin_address = base58.b58encode(address_bytes)

    return "sr" + bitcoin_address.decode()


# def increment_mine(target):
#     hash = get_hash(target)
#
#     while hash[:config.strict] != "0"*config.strict:
#         print(f"Hash: {hash} Try №{target.nonce}")
#         target.nonce += 1
#         hash = get_hash(target)
#
#     print("\r" + hash)
#     target.hash = hash


def random_mine(target):
    hash = get_hash(target)
    i = 1
    target.timestamp = datetime.datetime.utcnow().timestamp()
    while hash[:config.strict] != "0" * config.strict:
        print(f"Hash: {hash} Try №{i} UNIX Time: {target.timestamp}")
        target.timestamp = datetime.datetime.now(datetime.timezone.utc).timestamp()
        # print(round(target.timestamp))
        target.nonce = random.randint(0, math.pow(10, 308))
        i += 1
        hash = get_hash(target)

    print("\r" + hash)
    target.hash = hash


def get_hash(target):
    return hashlib.sha256(config.chain_id + target.serialize(False).encode()).hexdigest()


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
    print("capybara")

    outputs = {}
    inputs = []
    pre_result = {}
    result = []

    for i in reversed(range(len(blockchain.blockchain["blocks"]))):
        one: dict = blockchain.blockchain["blocks"][i]
        block_object = NewBlock.from_dict(one)

        for tr in block_object.transactions:
            print(f"Transaction {tr.address}")
            if outputs.get(tr.address) is None:
                outputs[tr.address] = []
            print(outputs)
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
                # tmp_out_list.pop(_in.output_index)
                tmp_out_list[_in.output_index] = None
                pre_result[out_transaction_address] = tmp_out_list
            else:
                pre_result[out_transaction_address] = out_list
        else:
            pre_result[out_transaction_address] = out_list

    print(pre_result)

    for address, pre_result_outputs in pre_result.items():
        for i in range(len(pre_result_outputs)):
            print(f"Unspent appending: {[pre_result_outputs[i], address, i]}")
            result.append([pre_result_outputs[i], address, i])

    print(f"result: {result}")
    # print(f"result2: {[i[0].serialize() for i in result]}")
    return result


def get_potential_inputs(blockchain, user_public_key, token_address="", target_amount=math.inf):
    print("Begin get_potential_inputs")
    from Transaction import Input
    outputs_format = get_all_unspent_outputs(blockchain)
    # outputs_format.reverse()
    # print(f"reversed: {outputs_format}")
    # print(outputs_format)
    # print("="*10)
    # for i in outputs_format:
        # print(i[0].serialize())
    # print("="*10)

    current_amount = 0
    reward_counter = 0
    current_reward = config.base_mining_reward
    result = []

    for i in outputs_format:
        if current_amount >= target_amount:
            break

        if i[0] is None:
            continue

        if i[0].to == generate_address(user_public_key):
            if i[0].token_address == token_address:
                print(i[0].type)
                if not i[0].type in ["burn", "gas", "reward"]:
                    current_amount += i[0].amount
                    print(f"Adding {i[0].amount}")

                if i[0].type == "":
                    if i[0].type == "reward":
                        if reward_counter >= config.halving_period:
                            reward_counter = 0
                            current_reward = max(current_reward/2, 1)
                        reward_counter += 1
                        current_amount += max(current_reward, 1)
                        current_amount += get_fee_amount_by_output(blockchain, i[0])

                print(f"Index is {i[2]}")
                result.append(Input(i[1], i[2]))
    print("Result:")
    return result


def send_token(blockchain, user_private_key: ecdsa.SigningKey, to, amount, token_address="", only_after=None, miner_fee=0):
    from Transaction import Transaction, Output, Input
    from Block import NewBlock
    from Token import NewToken

    current_reward = config.base_mining_reward
    print(f"Token balance: {get_token_balance(blockchain, user_private_key.get_verifying_key(), token_address)}")
    if amount > get_token_balance(blockchain, user_private_key.get_verifying_key(), token_address):
        print("Not enough money! ;(")
        return None

    inputs: List[Input] = get_potential_inputs(blockchain, user_private_key.get_verifying_key(), token_address, target_amount=amount)
    print("get_potential_inputs")
    print([i.serialize() for i in inputs])
    print("Before this")
    outputs: List[Output] = []

    input_sum = 0
    output_sum = 0

    for _in in inputs:
        some_out: Output = input_to_output(blockchain, _in)

        if not some_out.type in ["burn", "gas", "reward"]:
            input_sum += some_out.amount

        if some_out.token_address == "":
            if some_out.type == "reward":
                block_id = get_block_id_by_transaction_address(blockchain, _in.transaction_address)

                print(f"Adding to input_sum in send: {max(current_reward, 1)}")
                input_sum += max(current_reward, 1)
                input_sum += get_fee_amount_by_output(blockchain, some_out)
                if block_id-1 >= config.halving_period:
                    print("Halving!")
                    current_reward = max(current_reward / 2, 1)

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

    print(f"Input sum in send: {input_sum}")
    print(f"Output sum in send: {output_sum}")

    outputs.append(Output(generate_address(user_private_key.get_verifying_key()), input_sum+miner_fee - output_sum, token_address, type="return"))

    new_transaction = Transaction(public_key=user_private_key.get_verifying_key(), inputs=inputs, outputs=outputs, only_after=only_after)
    get_nonce_for_unique_address_and_set_output_addresses(blockchain, new_transaction)
    sign(private_key=user_private_key, target=new_transaction)
    # print(f"Input sum: {input_sum}")
    # print(f"Output sum: {output_sum}")

    return new_transaction

# def advanced_send_token(blockchain, user_private_key: ecdsa.SigningKey, to, amount, token_address="", miner_fee=0):
#     from Transaction import Transaction, Output, Input
#     from Block import NewBlock
#     from Token import NewToken
#
#     if token_address != "":
#         token_object: NewToken = [i for i in blockchain.get_token_list() if i.address == token_address][0]
#         amount = round(amount, token_object.decimals)
#     if token_address == "":
#         amount = round(amount, config.native_coin_decimals)
#
#     current_reward = config.base_mining_reward
#     # print(f"Token balance: {get_token_balance(blockchain, user_private_key.get_verifying_key(), token_address)}")
#     # if amount > get_token_balance(blockchain, user_private_key.get_verifying_key(), token_address):
#     #     print("Not enough money! ;(")
#     #     return None
#
#     inputs: List[Input] = get_potential_inputs(blockchain, user_private_key.get_verifying_key(), token_address, target_amount=amount)
#     print("get_potential_inputs")
#     print([i.serialize() for i in inputs])
#     outputs: List[Output] = []
#
#     input_sum = {}
#     output_sum = {}
#
#     for _in in inputs:
#         some_out: Output = input_to_output(blockchain, _in)
#         if input_sum.get(some_out.token_address) is None:
#             input_sum[some_out.token_address] = 0
#
#         if not some_out.type in ["burn", "gas", "reward"]:
#             input_sum[some_out.token_address] += some_out.amount
#
#         if some_out.token_address == "":
#             if some_out.type == "reward":
#                 block_id = get_block_id_by_transaction_address(blockchain, _in.transaction_address)
#
#                 if block_id-1 >= config.halving_period:
#                     current_reward = max(current_reward / 2, 1)
#                 input_sum[some_out.token_address] += max(current_reward, 1)
#
#     outputs.append(Output(to, amount, token_address, "send"))
#     if token_address != "":
#         for tk in blockchain.get_token_list():
#             tk: NewToken = tk
#             if tk.burn:
#                 outputs.append(Output("", amount * tk.burn, token_address, "burn"))
#             if tk.commission:
#                 outputs.append(Output(generate_address(tk.public_key), amount * tk.commission, token_address, "commission"))
#
#     for out in outputs:
#         if output_sum.get(out.token_address) is None:
#             output_sum[out.token_address] = 0
#
#         output_sum[out.token_address] += out.amount
#
#     # advanced token return
#     for tk_address, tk_sum in input_sum.items():
#         outputs.append(
#             Output(generate_address(user_private_key.get_verifying_key()),
#                    input_sum.get(token_address) - output_sum.get(tk_address) or 0,
#                    tk_address, type="return")
#         )
#
#     # check if user has enough of each token
#     for tk_address, tk_sum in output_sum.items():
#         if get_token_balance(blockchain,
#                              user_private_key.get_verifying_key(),
#                              tk_address) < tk_sum:
#             print("Advanced not enough money!")
#             return None
#
#     new_transaction = Transaction(public_key=user_private_key.get_verifying_key(), inputs=inputs, outputs=outputs)
#     get_nonce_for_unique_address(blockchain, new_transaction)
#     sign(private_key=user_private_key, target=new_transaction)
#     # print(f"Input sum: {input_sum}")
#     # print(f"Output sum: {output_sum}")
#
#     return new_transaction


def get_token_balance(blockchain, public_key: ecdsa.VerifyingKey, token_address=""):
    balance = 0
    reward_counter = 0
    current_reward = config.base_mining_reward
    inputs = get_potential_inputs(blockchain, public_key, token_address)
    print("Get potential inputs in the get token balance")
    print([i.serialize() for i in inputs])

    for _in in inputs:
        out = input_to_output(blockchain, _in)
        print("input_to_output result")
        print(out.serialize())
        if not out.type in ["burn", "gas", "reward"]:
            if out.token_address == token_address:
                if out.to == generate_address(public_key):
                    print(f"Before: {balance}")
                    print(f"Adding: {out.amount}")
                    balance += out.amount
                    print(f"After: {balance}")

        if out.type == "reward":
            if token_address == "":
                if out.to == generate_address(public_key):
                    if reward_counter >= config.halving_period:
                        reward_counter = 0
                        current_reward = max(current_reward/2, 1)
                    reward_counter += 1
                    balance += max(current_reward, 1)
                    balance += get_fee_amount_by_output(blockchain, out)

    return balance


def create_special_transaction(blockchain, private_key: ecdsa.SigningKey, type: str, token=None, amount=0, token_address="", only_after=None, miner_fee=0):
    if type not in ["token", "mint", "stop_mint", "burn"]:
        return None

    from Transaction import Transaction, Output

    if type in ["mint", "burn"]:
        if token_address != "":
            token_object = [i for i in blockchain.get_token_list() if i.address == token_address][0]
            amount = round(amount, token_object.decimals)
        if token_address == "":
            amount = round(amount, config.native_coin_decimals)

    inputs = get_potential_inputs(blockchain, private_key.get_verifying_key(), token_address="", target_amount=config.creation_gas_fee)
    # inputs_converted = [input_to_output(blockchain, i) for i in inputs]
    input_sum = 0
    current_reward = config.base_mining_reward

    for _in in inputs:
        some_out = input_to_output(blockchain, _in)
        if not some_out.type in ["burn", "gas", "reward"]:
            input_sum += some_out.amount

        if some_out.token_address == "":
            if some_out.type == "reward":
                block_id = get_block_id_by_transaction_address(blockchain, _in.transaction_address)

                if block_id - 1 >= config.halving_period:
                    current_reward = max(current_reward / 2, 1)
                input_sum += max(current_reward, 1)
                input_sum += get_fee_amount_by_output(blockchain, some_out)

    outputs = [Output("", config.creation_gas_fee, "", "gas"),
               Output(generate_address(private_key.get_verifying_key()),
                      input_sum+miner_fee-config.creation_gas_fee, "",
                      "return")]
    tokens = []

    match type:
        case "token":
            tokens.append(token)
        case "mint":
            outputs.append(
                Output(generate_address(private_key.get_verifying_key()),
                       amount,
                       token_address,
                       "mint")
            )
        case "stop_mint":
            outputs.append(
                Output(
                    generate_address(private_key.get_verifying_key()),
                    0,
                    token_address,
                    "stop_mint"
                )
            )
        case "burn":
            outputs.append(
                Output(
                    "",
                    amount,
                    token_address,
                    "burn"
                )
            )

    # print(f"THE INPUT SUM IS: {input_sum}")
    new_transaction = Transaction(private_key.get_verifying_key(),
                                  inputs,
                                  outputs,
                                  tokens,
                                  only_after=only_after)

    get_nonce_for_unique_address_and_set_output_addresses(blockchain, new_transaction)
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
            print("The input is:")
            print(input)
            if tr.address == input.transaction_address:
                return tr.outputs[input.output_index]


def get_nonce_for_unique_address_and_set_output_addresses(blockchain, target):
    from Block import NewBlock

    print(blockchain.blockchain)
    existing_addresses = []

    for i in range(len(blockchain.blockchain["blocks"])):
        one: dict = blockchain.blockchain["blocks"][i]
        block_object = NewBlock.from_dict(one)
        for tr in block_object.transactions:
            existing_addresses.append(tr.address)
            for token in tr.tokens:
                existing_addresses.append(token.address)

    print(existing_addresses)

    target.address = generate_serializable_address(target)

    while target.address in existing_addresses:
        print("In loop")
        target.nonce = random.randint(0, math.pow(10, 308))
        target.address = generate_serializable_address(target)

    target.set_output_addresses()


def get_block_id_by_transaction_address(blockchain, transaction_address):
    from Block import NewBlock

    for i in range(len(blockchain.blockchain["blocks"])):
        one: dict = blockchain.blockchain["blocks"][i]
        block_object = NewBlock.from_dict(one)

        for tr in block_object.transactions:
            if tr.address == transaction_address:
                return block_object.id


def mints_are_stopped(blockchain, token_address):
    from Block import NewBlock

    for i in range(len(blockchain.blockchain["blocks"])):
        one: dict = blockchain.blockchain["blocks"][i]
        block_object = NewBlock.from_dict(one)

        for tr in block_object.transactions:
            for out in tr.outputs:
                if out.type == "stop_mint":
                    return True
    return False


def get_token_minted_amount(blockchain, token_address):
    from Block import NewBlock

    minted_amount = 0

    for i in range(len(blockchain.blockchain["blocks"])):
        one: dict = blockchain.blockchain["blocks"][i]
        block_object = NewBlock.from_dict(one)

        for tr in block_object.transactions:
            for out in tr.outputs:
                if out.type == "mint" and out.token_address == token_address:
                    minted_amount += out.amount

    return minted_amount


def get_output_sum_from_input_list(blockchain, inputs: list):
    current_reward = config.base_mining_reward
    output_sum = 0

    for _in in inputs:
        some_out = input_to_output(blockchain, _in)
        if some_out.type not in ["burn", "gas", "reward"]:
            output_sum += some_out.amount

        if some_out.token_address == "":
            if some_out.type == "reward":
                print(f"Again the input is: {_in}")
                block_id = get_block_id_by_transaction_address(blockchain, _in.transaction_address)

                if block_id - 1 >= config.halving_period:
                    current_reward = max(current_reward / 2, 1)
                output_sum += max(current_reward, 1)
                output_sum += get_fee_amount_by_output(blockchain, some_out)


    return output_sum


def sort_inputs_by_output_token_address(blockchain, inputs):
    result = {}
    for _in in inputs:
        print("In")
        print(_in)
        out = input_to_output(blockchain, _in)
        if result.get(out.token_address) is None:
            result[out.token_address] = []

        result[out.token_address].append(_in)

    return result


def generate_seed_phrase(words=12):
    result = []
    result_str = ""

    with open("words.txt") as file:
        word_list = file.read().strip().split("\n")

    for i in range(words):
        result.append(random.choice(word_list))

    for word in result:
        result_str = f"{result_str} {word}"

    return result_str.strip()


def get_fee_amount_by_output(blockchain, output):
    from Block import NewBlock

    block_id = get_block_id_by_transaction_address(output.transaction_address)
    block: NewBlock = blockchain.get_block_by_id(block_id)
    fee = block.get_total_fee()
    return fee
