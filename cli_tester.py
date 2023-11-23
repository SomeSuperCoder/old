from Validator import Validator
from Block import NewBlock
from Blockchain import BlockChain
from Transaction import Transaction, Output
from Token import NewToken

import utils

test1_private_key = utils.string_to_private_key("test")
test1_public_key = test1_private_key.get_verifying_key()
print(f"Test1 address: {utils.generate_address(test1_public_key)}")

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

mint_transaction = Transaction(test1_public_key,
                                 [],
                                 [Output(utils.generate_address(test1_public_key),
                                         amount=15,
                                         token_address="sr1J6rKxnhWMhMu2StX3cevFCypVk6HBbz2j",
                                         type="mint")],
                                 )

utils.sign(test1_private_key, reward_transaction)

some_test_token = NewToken("Solana", "SOL", test1_public_key, burn=0.5, commission=0.1)
utils.sign(test1_private_key, some_test_token)

while True:
    cmd = input(">> ")
    match cmd:
        case "genesis":
            block = NewBlock(blockchain.get_latest_block_id()+1,
                             [reward_transaction],
                             blockchain.get_latest_hash()
                             )
            utils.random_mine(block)
            blockchain.add_block(block)
        case "test1_balance":
            print(utils.get_token_balance(blockchain, test1_public_key, token_address="sr1J6rKxnhWMhMu2StX3cevFCypVk6HBbz2j"))
        case "test2_balance":
            print(utils.get_token_balance(blockchain, test2_public_key, token_address="sr1J6rKxnhWMhMu2StX3cevFCypVk6HBbz2j"))
        case "send_to_test2":
            block = NewBlock(blockchain.get_latest_block_id()+1,
                             [utils.send_token(blockchain,
                                               test1_private_key,
                                               utils.generate_address(test2_public_key),
                                               2,
                                               "sr1J6rKxnhWMhMu2StX3cevFCypVk6HBbz2j")],
                             blockchain.get_latest_hash()
                             )
            utils.random_mine(block)
            blockchain.add_block(block)
        case "send_to_test1":
            block = NewBlock(blockchain.get_latest_block_id() + 1,
                             [utils.send_token(blockchain,
                                               test2_private_key,
                                               utils.generate_address(test1_public_key),
                                               2,
                                               "sr1J6rKxnhWMhMu2StX3cevFCypVk6HBbz2j")],
                             blockchain.get_latest_hash()
                             )
            utils.random_mine(block)
            blockchain.add_block(block)
        case "get_fraud":
            print(Validator.check_if_transaction_is_fraudulent(blockchain, reward_transaction))
        case "add_token":
            block = NewBlock(blockchain.get_latest_block_id() + 1,
                             [utils.create_token_transaction(blockchain, test1_private_key, some_test_token)],
                             blockchain.get_latest_hash()
                             )
            utils.random_mine(block)
            blockchain.add_block(block)
        case "mint10":
            block = NewBlock(blockchain.get_latest_block_id() + 1,
                             [mint_transaction],
                             blockchain.get_latest_hash()
                             )
            utils.random_mine(block)
            blockchain.add_block(block)

