import json

from Transaction import Transaction
from Token import NewToken
from Mint import Mint


class NewBlock:
    def __init__(self, id: int, transactions: list, tokens: list, mints: list, previous_block_hash: str, hash=None, nonce=0):
        self.id = id
        self.transactions = transactions
        self.tokens = tokens
        self.mints = mints
        self.previous_block_hash = previous_block_hash
        self.hash = hash
        self.nonce = nonce

    def serialize(self, strict=False):
        if not strict:
            return json.dumps({
                "id": self.id,
                "transactions": [json.loads(i.serialize()) for i in self.transactions],
                "tokens": [json.loads(i.serialize()) for i in self.tokens],
                "mints": [json.loads(i.serialize()) for i in self.mints],
                "previous_block_hash": self.previous_block_hash,
                "nonce": self.nonce
            })
        elif strict:
            return json.dumps({
                "id": self.id,
                "transactions": [json.loads(i.serialize(True)) for i in self.transactions],
                "tokens": [json.loads(i.serialize(True)) for i in self.tokens],
                "mints": [json.loads(i.serialize(True)) for i in self.mints],
                "previous_block_hash": self.previous_block_hash,
                "hash": self.hash,
                "nonce": self.nonce
            })

    @staticmethod
    def from_dict(source):
        NewBlock(id=source["id"],
                 previous_block_hash=source["previous_block_hash"],
                 hash=source["hash"],
                 nonce=source["nonce"],
                 transactions=[Transaction.from_dict(i) for i in source["transactions"]],
                 tokens=[NewToken.from_dict(i) for i in source["transactions"]],
                 mints=[Mint.from_dict(i) for i in source["mints"]])


# class ExistingBlock:
#     def __init__(self, id: int, transactions: list, hash: str, previous_block_hash: str, nonce: int):
#         self.id = id
#         self.transactions = transactions
#         self.previous_block_hash = previous_block_hash
#         self.hash = hash
#         self.nonce = nonce
#
#         def serialize(self, strict=False):
#             if not strict:
#                 return json.dumps({
#                     "id": self.id,
#                     "transactions": [json.loads(i.serialize()) for i in self.transactions],
#                     "tokens": [json.loads(i.serialize()) for i in self.tokens],
#                     "mints": [json.loads(i.serialize()) for i in self.mints],
#                     "previous_block_hash": self.previous_block_hash,
#                     "nonce": self.nonce
#                 })
#             elif strict:
#                 return json.dumps({
#                     "id": self.id,
#                     "transactions": [json.loads(i.serialize()) for i in self.transactions],
#                     "tokens": [json.loads(i.serialize()) for i in self.tokens],
#                     "mints": [json.loads(i.serialize()) for i in self.mints],
#                     "previous_block_hash": self.previous_block_hash,
#                     "hash": self.hash,
#                     "nonce": self.nonce
#                 })
