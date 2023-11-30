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
        sored_by_token = utils.sort_outputs_by_token(transaction.outputs)
        all_non_native: list[Output] = []
        for token_address, outputs in sored_by_token.items():
            for out in outputs:
                if token_address != "":
                    all_non_native.append(out)

        print(sored_by_token)
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

        # check if the transaction inputs are real
        transaction_outputs = [utils.input_to_output(blockchain, i) for i in transaction.inputs]
        print("Transaction outputs:")
        print([i.serialize() for i in transaction_outputs])
        # NOTE: create a get input sum and a get output sum function(I am tired of copying the code all the time!)

        return False
