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

print(blockchain.blockchain)

reward_transaction = Transaction(test1_public_key,
                                 [],
                                 [Output(utils.generate_address(test1_public_key),
                                         amount=1000000000000000000000000000000000000000,
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

some_test_token = NewToken("Solana", "SOL", test1_public_key, burn=0.5, commission=0.1)
utils.sign(test1_private_key, some_test_token)

while True:
    cmd = input(">> ")
    match cmd:
        case "genesis":
            utils.get_nonce_for_unique_address(blockchain, reward_transaction)
            utils.sign(test1_private_key, reward_transaction)
            block = NewBlock(blockchain.get_latest_block_id()+1,
                             [reward_transaction],
                             blockchain.get_latest_hash()
                             )
            utils.random_mine(block)
            blockchain.add_block(block)
            reward_transaction.nonce = 0
            reward_transaction.address = ""
        case "t1b":
            print(utils.get_token_balance(blockchain, test1_public_key, token_address=""))
        case "t2b":
            print(utils.get_token_balance(blockchain, test2_public_key, token_address=""))
        case "stt2":
            amount = int(input("Amount: "))
            block = NewBlock(blockchain.get_latest_block_id()+1,
                             [utils.send_token(blockchain,
                                               test1_private_key,
                                               utils.generate_address(test2_public_key),
                                               amount,
                                               "")],
                             blockchain.get_latest_hash()
                             )
            utils.random_mine(block)
            blockchain.add_block(block)
        case "stt1":
            amount = int(input("Amount: "))
            block = NewBlock(blockchain.get_latest_block_id() + 1,
                             [utils.send_token(blockchain,
                                               test2_private_key,
                                               utils.generate_address(test1_public_key),
                                               amount,
                                               "")],
                             blockchain.get_latest_hash()
                             )
            utils.random_mine(block)
            blockchain.add_block(block)
        case "get_fraud":
            print(Validator.check_if_transaction_is_fraudulent(blockchain, reward_transaction))
        case "add_token":
            print("test")
            utils.get_nonce_for_unique_address(blockchain, some_test_token)
            print("test")
            utils.sign(test1_private_key, some_test_token)
            block = NewBlock(blockchain.get_latest_block_id() + 1,
                             [utils.create_token_transaction(blockchain, test1_private_key, some_test_token)],
                             blockchain.get_latest_hash()
                             )
            utils.random_mine(block)
            blockchain.add_block(block)
        case "mint":
            utils.get_nonce_for_unique_address(blockchain, mint_transaction)
            utils.sign(test1_private_key, mint_transaction)
            block = NewBlock(blockchain.get_latest_block_id() + 1,
                             [mint_transaction],
                             blockchain.get_latest_hash()
                             )
            utils.random_mine(block)
            blockchain.add_block(block)
            mint_transaction.nonce = 0
            mint_transaction.address = ""
        case "get_valid":
            print(blockchain.validate())
        case "gauo":
            print(utils.get_all_unspent_outputs(blockchain))
