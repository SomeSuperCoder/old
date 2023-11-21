from Blockchain import BlockChain
from Block import NewBlock
from Transaction import Transaction, Input, Output
from Mint import Mint
from Token import NewToken

import utils

blockchain = BlockChain()
blockchain.load()

private_key = utils.string_to_private_key("aaa")
print(f"User address: {utils.generate_address(private_key.get_verifying_key())}")

# transaction = Transaction(public_key=private_key.get_verifying_key(), inputs=[], outputs=[Output("nc15FXbS1nct4G8iku1dQkcbLzTPZEgp8BGg", 10, "")])
# utils.sign(private_key, transaction)
# print(utils.verify(transaction))


# token = NewToken("Test", "TST", private_key.get_verifying_key())
# utils.sign(private_key, token)
# print(utils.verify(token))


# mint = Mint(amount=10, token_address=token.address, public_key=private_key.get_verifying_key())
# utils.sign(private_key, mint)
# print(utils.verify(mint))

# block = NewBlock(blockchain.get_latest_block_id() + 1, transactions=[transaction], tokens=[], mints=[], previous_block_hash=blockchain.get_latest_hash())
# utils.random_mine(block)
#
# blockchain.add_block(block)
blockchain.save()

print(blockchain.blockchain)

print(blockchain.validate())

# print("Potential inputs:")
# potential = utils.get_potential_inputs(blockchain, private_key.get_verifying_key())
# print([i.serialize() for i in potential])

print(utils.send_token(blockchain, private_key, "lox", 1).serialize(True))

# utils.validate_transaction_inputs(blockchain.blockchain["transactions"])

# utils.get_token_balance(blockchain, token, utils.generate_address(private_key.get_verifying_key()))
