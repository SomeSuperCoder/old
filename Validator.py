import datetime

import ecdsa
import statistics
import utils
import config

from Transaction import Transaction, Output
from Token import NewToken


class Validator:
    @staticmethod
    def block_is_fraudulent(blockchain, block):
        from Block import NewBlock
        block: NewBlock = block
        block_zeros = 0

        for char in block.hash:
            if char == "0":
                block_zeros += 1
            else:
                break

        latest_timestamps = [i.timestamp for i in blockchain.get_latest_blocks(config.amount_of_last_blocks_for_checks)]
        if block.id != blockchain.get_latest_block_id()+1:
            return True
        if block.previous_block_hash != blockchain.get_latest_hash():
            return True
        if block.timestamp < statistics.median(latest_timestamps):
            return True
        if block.timestamp > datetime.datetime.utcnow() + config.room_for_timestamp_error:
            return True
        if block_zeros < blockchain.get_current_difficulty():
            return True
        if block.get_size() > config.max_block_size:
            return False

    @staticmethod
    def check_only_one_block_reward(block):
        output_list = utils.get_block_outputs(block)
        formatted = utils.sort_outputs_by_type(output_list)
        block_reward_list = formatted.get("reward")

        # disallow more than one reward per block
        if block_reward_list is None:
            return True

        if len(block_reward_list) > 1:
            return False

        return True

    @staticmethod
    def transaction_is_fraudulent(blockchain, transaction, created_by_smart_contract=False):
        # Get all non-native token outputs
        sorted_by_token = utils.sort_outputs_by_token(transaction.outputs)
        all_non_native: list[Output] = []
        all_native: list[Output] = []
        for token_address, outputs in sorted_by_token.items():
            for out in outputs:
                if token_address != "":
                    all_non_native.append(out)

        for token_address, outputs in sorted_by_token.items():
            for out in outputs:
                if token_address == "":
                    all_native.append(out)

        print(sorted_by_token)
        print(all_non_native)
        # ===========================

        send_counter = {i.token_address:0 for i in all_non_native}
        print(send_counter)

        for out in all_non_native:
            # check if the token even exists in the first place
            if out.token_address not in [i.address for i in blockchain.get_token_list()]:
                print("check if the token even exists in the first place")
                return True

            token: NewToken = [i for i in blockchain.get_token_list() if i.address == out.token_address][0]

            # check if mint is allowed
            if out.type == "mint":
                if utils.mints_are_stopped(blockchain, out.token_address):
                    print("check if mint is allowed")
                    return True
                print("Start")
                print(utils.get_token_minted_amount(blockchain, out.token_address) + out.amount)
                print(token.max_supply)
                if utils.get_token_minted_amount(blockchain, out.token_address) + out.amount > token.max_supply:
                    print("Max supply reached")
                    return True

            # check if send outputs follow token rules
            if out.type == "send":
                send_counter += 1
                commission_done = 0
                burn_done = 0
                for checker in all_non_native:
                    if checker.type == "commission" and checker.amount >= token.commission:
                        commission_done += 1
                    if checker.type == "burn" and checker.amount >= token.burn:
                        burn_done += 1

                if commission_done >= send_counter[out.token_address] or not burn_done >= send_counter[out.token_address]:
                    print("check if send outputs follow token rules")
                    return True

            if out.type in ["mint", "stop_mint"]:
                token_owner = None
                for i in blockchain.get_token_list():
                    if i.address == out.token_address:
                        token_owner = i.owner_id
                        break

                if utils.generate_address(transaction.public_key) != token_owner:
                    print("Token signature verify error")
                    return True

            # do the non-negative check
            if out.amount < 0:
                print("do the non-negative check")
                return True

            # check decimals for non-native
            if str(out.amount) != str(round(out.amount, token.decimals)):
                print("check decimals for non-native")
                return True

            # check from is set only to the transaction public key
            if out.from_ != transaction.public_key:
                print("check from is set only to the transaction public key")
                return True

            # allow miner fee only in Neon
            if out.type == "fee":
                print("allow miner fee only in Neon")
                return True

        for out in all_native:
            # check decimals for NATIVE
            if out.amount != round(out.amount, config.native_coin_decimals):
                print("check decimals for NATIVE")
                return True

            # disallow minting neon
            if out.type in ["mint", "stop_mint"]:
                return True

        # # check if the transaction inputs are not bigger than the outputs
        # print("Transaction outputs:")
        # sorted_ins = utils.sort_inputs_by_output_token_address(blockchain, transaction.inputs)
        # sorted_outs = utils.sort_outputs_by_output_token_address(blockchain, transaction.outputs)
        # print(sorted_ins)
        #
        # sums_for_outs = {}
        # sums_for_ins = {}
        #
        # for token_address in sorted_ins.keys():
        #     sums_for_ins[token_address] = utils.get_output_sum_from_input_list(blockchain, sorted_ins[token_address])
        # print(f"sorted_outs: {sorted_outs}")
        # for token_address in sorted_outs.keys():
        #     print(f"Some token_address: {token_address}")
        #     print(f"Some index get: {sorted_outs[token_address]}")
        #     sums_for_outs[token_address] = utils.get_output_sum_from_output_list(blockchain, sorted_outs[token_address])
        #
        # print(sums_for_ins)
        # print(sums_for_outs)
        #
        # print("Before for capybara top")
        #
        # for token_address, amount in sums_for_outs.items():
        #     print("="*20)
        #     print("IN IO CHECKER")
        #     # print(sums_for_ins[token_address])
        #     if sums_for_ins.get(token_address) is None:
        #         continue
        #     print(amount)
        #     print("="*20)
        #     if sums_for_ins[token_address] < amount:
        #         print("check if the transaction inputs are not smaller than the outputs")
        #         return True
        #
        # print("END")

        # # check if transaction inputs are real
        # for _in in transaction.inputs:
        #     if utils.input_to_output(blockchain, _in) is None:
        #         print("check if transaction inputs are real")
        #         return True

        # check if the user has enough money
        each_token_spent = utils.get_output_sums_from_output_list(blockchain, transaction.outputs, public_key=transaction.public_key, already_added=False)
        for token_address, amount_spent in each_token_spent.items():
            if amount_spent > utils.get_token_balance(blockchain, transaction.public_key, token_address):
                print("check if the user has enough money")
                print("Spent:")
                print(amount_spent)
                print("Balance:")
                print(utils.get_token_balance(blockchain, transaction.public_key, token_address))
                return True

        # check if a transaction with the same address exists
        for i in blockchain.get_transaction_list():
            if i.address == transaction.address:
                print("check if a transaction with the same address exists")
                return True

        transaction_token_address_list = [i.address for i in transaction.tokens]

        # check if any of the added token have an existing duplicate with the same address
        for i in blockchain.get_token_list():
            if i.address in transaction_token_address_list:
                print("check if any of the added token have an existing duplicate with the same address")
                return True

        # token collection owner check
        for token in transaction.tokens:
            if token.collection == "":
                pass
            else:
                collection_owner = blockchain.get_collection_owner(token.collection)
                if collection_owner is not None and collection_owner != token.public_key:
                    print("token collection owner check")
                    return True

        # check gas for tokens
        print("="*20)
        print("START gas for tokens")
        sorted_by_type_for_gas_check_in_neon_outputs = utils.sort_outputs_by_type(sorted_by_token[""]).get("gas") or []
        print([i.serialize() for i in sorted_by_type_for_gas_check_in_neon_outputs])
        sorted_by_type_for_gas_check_in_neon_output_sum = 0

        for some_out in sorted_by_type_for_gas_check_in_neon_outputs:
            if some_out.type == "gas":
                sorted_by_type_for_gas_check_in_neon_output_sum += some_out.amount

        total_fee_required = 0
        total_fee_required += len(transaction.tokens) * config.creation_gas_fee

        for i in utils.sort_outputs_by_type(transaction.outputs).get("") or []:
            if i.type in ["mint", "stop_mint"]:
                total_fee_required += config.creation_gas_fee

        print(f"THE SUM YOU ARE LOOKING FOR: {sorted_by_type_for_gas_check_in_neon_output_sum}")
        if sorted_by_type_for_gas_check_in_neon_output_sum < total_fee_required:
            print("check gas for tokens")
            return True

        print("END gas for tokens")
        print("="*20)

        # check the digital signature
        if not created_by_smart_contract:
            if not utils.verify(transaction):
                print("check the digital signature for transaction")
                return True

        # check only after
        if transaction.only_after is not None:
            if transaction.only_after not in [i.address for i in blockchain.get_transaction_list()]:
                print("check only after")
                return True

        # # max transaction message length
        # if len(transaction.message) > config.max_message_len:
        #     print("max transaction message length")
        #     return True

        # check if transaction is empty
        if transaction.is_empty():
            print("check if transaction is empty")
            return True

        return False
