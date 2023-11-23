from Blockchain import BlockChain
from Block import NewBlock
from Transaction import Transaction, Input, Output
from Mint import Mint
from Token import NewToken

import utils

blockchain = BlockChain()
blockchain.load()

private_key = utils.string_to_private_key("aaa")
public_key = private_key.get_verifying_key()
print(f"User address: {utils.generate_address(private_key.get_verifying_key())}")

# print(public_key)
# print(utils.public_key_to_string(public_key))
# print(utils.string_to_public_key(utils.public_key_to_string(public_key)))

# token = NewToken("Test", "TST", private_key.get_verifying_key())
# utils.sign(private_key, token)
# print(utils.verify(token))

# print("Potential inputs:")
# potential = utils.get_potential_inputs(blockchain, private_key.get_verifying_key())
# print([i.serialize() for i in potential])

# print(utils.send_token(blockchain, private_key, "lox", 1).serialize(True))
# transaction = utils.create_token_transaction(blockchain, private_key, token)

# utils.validate_transaction_inputs(blockchain.blockchain["transactions"])

# utils.get_token_balance(blockchain, token, utils.generate_address(private_key.get_verifying_key()))

# block = NewBlock(blockchain.get_latest_block_id() + 1, transactions=[transaction], previous_block_hash=blockchain.get_latest_hash())
# utils.random_mine(block)

# blockchain.add_block(block)
# blockchain.save()

print(blockchain.validate())

# print(utils.get_token_balance(blockchain, public_key))

# print(f"Is empty: {transaction.is_empty()}")