from Transaction import Transaction

import utils


class Validator:
    @staticmethod
    def check_only_one_block_reward(block):
        output_list = utils.get_block_outputs(block)
        formatted = utils.sort_outputs_by_type(output_list)
        block_reward_list = formatted.get("reward")

        if block_reward_list is None:
            return True

        if len(block_reward_list) > 1:
            return False

        return True

    @staticmethod
    def check_if_transaction_is_fraudulent(blockchain, transaction):
        sored_by_token = utils.sort_outputs_by_token(transaction.outputs)
        all_non_native = []
        for token_address, outputs in sored_by_token.items():
            for out in outputs:
                if token_address != "":
                    all_non_native.append(out)

        print(sored_by_token)
        print(all_non_native)
