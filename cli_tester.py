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
                                         amount=500,
                                         token_address="sr15QnAxL2vbk3vjgiVayGBH3vXBCE5yrTjE",
                                         type="mint")],
                                 )

stop_mint_transaction = Transaction(test1_public_key,
                                 [],
                                 [Output(utils.generate_address(test1_public_key),
                                         amount=500,
                                         token_address="sr15QnAxL2vbk3vjgiVayGBH3vXBCE5yrTjE",
                                         type="stop_mint")],
                                 )

some_test_token = NewToken("Solana", "SOL", test1_public_key, burn=0.5, commission=0.1)
utils.sign(test1_private_key, some_test_token)


def add_a_new_block(transaction):
    if not Validator.transaction_is_fraudulent(blockchain, transaction):
        new_block = NewBlock(blockchain.get_latest_block_id() + 1,
                         [transaction],
                         blockchain.get_latest_hash()
                         )
        utils.random_mine(new_block)
        blockchain.add_block(new_block)


while True:
    cmd = input(">> ")
    match cmd:
        case "genesis":
            utils.get_nonce_for_unique_address(blockchain, reward_transaction)
            utils.sign(test1_private_key, reward_transaction)
            add_a_new_block(reward_transaction)
            reward_transaction.nonce = 0
            reward_transaction.address = ""
        case "t1b":
            print(utils.get_token_balance(blockchain, test1_public_key, token_address=""))
        case "t2b":
            print(utils.get_token_balance(blockchain, test2_public_key, token_address=""))
        case "stt2":
            amount = int(input("Amount: "))
            add_a_new_block(utils.send_token(blockchain,
                                               test1_private_key,
                                               utils.generate_address(test2_public_key),
                                               amount,
                                               ""))
        case "stt1":
            amount = int(input("Amount: "))
            add_a_new_block(utils.send_token(blockchain,
                                               test2_private_key,
                                               utils.generate_address(test1_public_key),
                                               amount,
                                               ""))
        case "get_fraud":
            print(Validator.transaction_is_fraudulent(
                blockchain, utils.send_token(blockchain,
                                               test1_private_key,
                                               utils.generate_address(test1_public_key),
                                               2,
                                               "")
            ))
        case "add_token":
            utils.get_nonce_for_unique_address(blockchain, some_test_token)
            utils.sign(test1_private_key, some_test_token)
            add_a_new_block(utils.create_token_transaction(blockchain, test1_private_key, some_test_token))
        case "mint":
            utils.get_nonce_for_unique_address(blockchain, mint_transaction)
            utils.sign(test1_private_key, mint_transaction)
            add_a_new_block(mint_transaction)
            mint_transaction.nonce = 0
            mint_transaction.address = ""
        case "get_valid":
            print(blockchain.validate())
        case "gauo":
            print(utils.get_all_unspent_outputs(blockchain))
        case "gpit1":
            print([i.serialize() for i in utils.get_potential_inputs(blockchain, test1_public_key)])
        case "gpit2":
            print([i.serialize() for i in utils.get_potential_inputs(blockchain, test2_public_key)])
        case "stop_mint":
            add_a_new_block(stop_mint_transaction)
        case "token_list":
            print([i.address for i in blockchain.get_token_list()])