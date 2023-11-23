from Block import NewBlock
from Blockchain import BlockChain
from Transaction import Transaction, Output

import utils

test1_private_key = utils.string_to_private_key("test")
test1_public_key = test1_private_key.get_verifying_key()

test2_private_key = utils.string_to_private_key("test2")
test2_public_key = test2_private_key.get_verifying_key()

blockchain = BlockChain()
blockchain.load()

reward_transaction = Transaction(test1_public_key,
                                 [],
                                 [Output(utils.generate_address(test1_public_key),
                                         amount=10,
                                         token_address="",
                                         type="reward")],
                                 )

utils.sign(test1_private_key, reward_transaction)

while True:
    cmd = input(">> ")
    match cmd:
        case "genesis":
            block = NewBlock(blockchain.get_latest_block_id(),
                             [reward_transaction],
                             blockchain.get_latest_hash()
                             )
            utils.increment_mine(block)
            blockchain.add_block(block)
        case "test1_balance":
            print(utils.get_token_balance(blockchain, test1_public_key))
