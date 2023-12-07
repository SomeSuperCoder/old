from Validator import Validator
from Block import NewBlock
from Blockchain import BlockChain
from Transaction import Transaction, Output, Input
from Token import NewToken
from SmartContract import SmartContract

import utils

test1_private_key = utils.string_to_private_key("test")
test1_public_key = test1_private_key.get_verifying_key()
print(f"Test1 address: {utils.generate_address(test1_public_key)}")

test2_private_key = utils.string_to_private_key("test2")
test2_public_key = test2_private_key.get_verifying_key()

miner_private_key = utils.string_to_private_key("miner")
miner_public_key = miner_private_key.get_verifying_key()

blockchain = BlockChain()
blockchain.load()

# print(blockchain.blockchain)

reward_transaction = Transaction(miner_public_key,
                                 outputs=[
                                     Output("",
                                            utils.generate_address(miner_public_key),
                                            amount=100000000000000,
                                            token_address="",
                                            type="reward")
                                          ],
                                 )

# mint_transaction = Transaction(test1_public_key,
#                                  [],
#                                  [Output(utils.generate_address(test1_public_key),
#                                          amount=500,
#                                          token_address="sr15QnAxL2vbk3vjgiVayGBH3vXBCE5yrTjE",
#                                          type="mint")],
#                                  )
mint_transaction = utils.create_special_transaction(blockchain,
                                                    test1_private_key,
                                                    token_address="",
                                                    amount=10,
                                                    type="mint")

stop_mint_transaction = utils.create_special_transaction(blockchain,
                                                    test1_private_key,
                                                    token_address="",
                                                    type="stop_mint")

empty_transaction = Transaction(test1_public_key,
                                [],
                                [],
                                []
                                )

some_test_token = NewToken("Solana", "SOL", test1_public_key, burn=0.5, commission=0.1)
utils.sign(test1_private_key, some_test_token)


def add_a_new_block(transaction):
    print(f"Adding a transaction: {transaction.serialize()}")
    if not Validator.transaction_is_fraudulent(blockchain, transaction):
        print("START ADDING PROCESS")
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
            utils.get_nonce_for_unique_address_and_set_output_addresses(blockchain, reward_transaction)
            utils.sign(miner_private_key, reward_transaction)
            add_a_new_block(reward_transaction)
            reward_transaction.nonce = 0
            reward_transaction.address = ""
        case "t1b":
            print(utils.get_token_balance(blockchain, test1_public_key, token_address=""))
        case "t2b":
            print(utils.get_token_balance(blockchain, test2_public_key, token_address=""))
        case "stt2":
            amount = float(input("Amount: "))
            add_a_new_block(utils.send_token(blockchain,
                                               test1_private_key,
                                               utils.generate_address(test2_public_key),
                                               amount,
                                               "",
                                             miner_fee=2
                                             ))
        case "stt1":
            amount = float(input("Amount: "))
            add_a_new_block(utils.send_token(blockchain,
                                             miner_private_key,
                                             utils.generate_address(test1_public_key),
                                             amount))
        case "get_fraud":
            print(Validator.transaction_is_fraudulent(
                blockchain, utils.send_token(blockchain,
                                                test1_private_key,
                                                utils.generate_address(test1_public_key),
                                                2,
                                                "")
            ))
        case "add_token":
            utils.get_nonce_for_unique_address_and_set_output_addresses(blockchain, some_test_token)
            utils.sign(test1_private_key, some_test_token)
            add_a_new_block(utils.create_special_transaction(blockchain,
                                                             test1_private_key,
                                                             "token",
                                                             token=some_test_token))
        case "mint":
            utils.get_nonce_for_unique_address_and_set_output_addresses(blockchain, mint_transaction)
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
            utils.get_nonce_for_unique_address_and_set_output_addresses(blockchain, stop_mint_transaction)
            utils.sign(test1_private_key, stop_mint_transaction)
            add_a_new_block(stop_mint_transaction)
        case "token_list":
            print([i.address for i in blockchain.get_token_list()])
        case "s":
            print(utils.generate_seed_phrase())
        case "em":
            print(empty_transaction.is_empty())
        case "glb":
            print(blockchain.get_latest_blocks())
        case "mb":
            print(utils.get_token_balance(blockchain, miner_public_key, token_address=""))
        case "sc_test":
            sc = SmartContract("with open(\"/result/result.json\", \"w\") as f: f.write(str(config.base_mining_reward))")
            sc.execute()
        case "diff":
            print(blockchain.get_current_difficulty())
