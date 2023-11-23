import json

from Transaction import Transaction
from Token import NewToken
from Mint import Mint
from Transaction import Transaction
from typing import List


class NewBlock:
    def __init__(self, id: int, transactions: list, previous_block_hash: str, hash=None, nonce=0):
        self.id = id
        self.transactions: List[Transaction] = transactions
        self.previous_block_hash = previous_block_hash
        self.hash = hash
        self.nonce = nonce

    def serialize(self, strict=False):
        if not strict:
            return json.dumps({
                "id": self.id,
                "transactions": [json.loads(i.serialize(True)) for i in self.transactions],
                "previous_block_hash": self.previous_block_hash,
                "nonce": self.nonce
            })
        elif strict:
            return json.dumps({
                "id": self.id,
                "transactions": [json.loads(i.serialize(True)) for i in self.transactions],
                "previous_block_hash": self.previous_block_hash,
                "hash": self.hash,
                "nonce": self.nonce
            })

    @staticmethod
    def from_dict(source):
        return NewBlock(id=source["id"],
                            transactions=[Transaction.from_dict(i) for i in source["transactions"]],
                            previous_block_hash=source["previous_block_hash"],
                            hash=source["hash"],
                            nonce=source["nonce"],)

    def is_empty(self):
        if self.id == 1:
            return False

        if not bool(len(self.transactions)):
            return True

        for i in self.transactions:
            if i.is_empty():
                print("Transaction is empty")
                return False

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
