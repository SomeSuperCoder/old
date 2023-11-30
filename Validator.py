import config
from Transaction import Transaction, Output
from Token import NewToken

import utils


class Validator:
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
    def transaction_is_fraudulent(blockchain, transaction):
        # Get all non-native token outputs
        sorted_by_token = utils.sort_outputs_by_token(transaction.outputs)
        all_non_native: list[Output] = []
        for token_address, outputs in sorted_by_token.items():
            for out in outputs:
                if token_address != "":
                    all_non_native.append(out)

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

            # do the non-negative check
            if out.amount < 0:
                return True

        # check if the transaction inputs are not bigger than the outputs
        print("Transaction outputs:")
        sorted_ins = utils.sort_inputs_by_output_token_address(blockchain, transaction.inputs)
        print(sorted_ins)

        sums_for_outs = {}
        sums_for_ins = {}

        for token_address in sorted_ins.keys():
            sums_for_ins[token_address] = utils.get_output_sum_from_input_list(blockchain, sorted_ins[token_address])

        for token_address in sums_for_outs.keys():
            sums_for_outs[token_address] = utils.get_output_sum_from_input_list(blockchain, sorted_by_token[token_address])

        print(sums_for_ins)
        print(sums_for_outs)

        for token_address, amount in sums_for_outs:
            if sums_for_ins[token_address] < amount:
                return True

        print("END")

        # check if transaction inputs are real
        for _in in transaction.inputs:
            if utils.input_to_output(blockchain, _in) is None:
                return True

        # check if a transaction with the same address exists
        for i in blockchain.get_transaction_list():
            if i.address == transaction.address:
                return True

        # check if any of the added token have an existing duplicate with the same address
        transaction_token_address_list = [i.address for i in transaction.tokens]
        for i in blockchain.get_token_list():
            if i.address in transaction_token_address_list:
                return True

        # check gas for tokens
        sorted_by_type_for_gas_check_in_neon_outputs = utils.sort_outputs_by_type(sorted_by_token[""])["gas"]
        sorted_by_type_for_gas_check_in_neon_output_sum = 0

        current_reward = config.base_mining_reward

        for some_out in sorted_by_type_for_gas_check_in_neon_outputs:
            if some_out.type not in ["burn", "gas", "reward"]:
                sorted_by_type_for_gas_check_in_neon_output_sum += some_out.amount

            if some_out.token_address == "":
                if some_out.type == "reward":
                    block_id = utils.get_block_id_by_transaction_address(blockchain, transaction.address)

                    if block_id - 1 >= config.halving_period:
                        current_reward = max(current_reward / 2, 1)
                    sorted_by_type_for_gas_check_in_neon_output_sum += max(current_reward, 1)

        if sorted_by_type_for_gas_check_in_neon_output_sum < len(transaction.tokens) * config.creation_gas_fee:
            return True

        return False
