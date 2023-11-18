import ecdsa.ecdsa

from Blockchain import BlockChain
from Block import NewBlock
from Transaction import Transaction
from Mint import Mint
from Token import NewToken

import utils

blockchain = BlockChain()
blockchain.load()

private_key = utils.string_to_private_key("aaa")

transaction = Transaction(private_key.get_verifying_key(), "123", 10, "")
utils.sign(private_key, transaction)
print(utils.verify(transaction))


token = NewToken("Test", "TST", private_key.get_verifying_key())
utils.sign(private_key, token)
print(utils.verify(token))


mint = Mint(amount=10, token_address=token.address, public_key=private_key.get_verifying_key())
utils.sign(private_key, mint)
print(utils.verify(mint))

block = NewBlock(blockchain.get_latest_id()+1, transactions=[transaction], tokens=[token], mints=[mint], previous_block_hash=blockchain.get_latest_hash())
utils.increment_mine(block)

blockchain.add_block(block)
blockchain.save()

print(blockchain.blockchain)

print(blockchain.validate())

utils.get_token_balance(blockchain, token, utils.generate_address(private_key.get_verifying_key()))
