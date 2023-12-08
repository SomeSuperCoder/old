import datetime

# strict = 1
creation_gas_fee = 10
chain_id = b'\x00'
# halving_period = 500
# base_mining_reward = 50
# target_block_time = datetime.timedelta(minutes=2)
room_for_timestamp_error = datetime.timedelta(minutes=10)
native_coin_decimals = 2
amount_of_last_blocks_for_checks = 5
max_message_len = 200
max_block_size = 4e+6
stake_time_weight = 2.5  # the smaller, the faster it will glow
stake_amount_weight = 2.5  # the smaller, the faster it will glow
stake_earn_percentage = 0.05
stake_slash_percentage = 0.5
blocks_before_release = 5
sc_code_prefix = """
import Block, Blockchain, config, SmartContract, Token, Validator
import sys

args = sys.argv
del sys

"""
