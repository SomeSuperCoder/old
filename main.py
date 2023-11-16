from Blockchain import BlockChain
from Block import NewBlock
from Transaction import Transaction
from Mint import Mint
from Token import NewToken

import utils

blockchain = BlockChain()
blockchain.load()

private_key = utils.string_to_private_key("aboba")

transaction = Transaction("abc", "123", 10, "")
transaction.sign(private_key)

token = NewToken("Test", "TST", utils.generate_address(private_key.get_verifying_key()))
token.sign(private_key)

mint = Mint(amount=10, token_address=token.address)
mint.sign(private_key=private_key)

block = NewBlock(blockchain.get_latest_id()+1, transactions=[transaction], tokens=[token], mints=[mint], previous_block_hash=blockchain.get_latest_hash())
utils.increment_mine(block)

blockchain.add_block(block)
blockchain.save()

print(blockchain.blockchain)

print(blockchain.validate(block))
