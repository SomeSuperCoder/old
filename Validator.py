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
