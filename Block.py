import json
import utils
import base64

from Transaction import Transaction
from Token import NewToken
from Mint import Mint
from Transaction import Transaction
from typing import List


class NewBlock:
    def __init__(self, id: int, transactions: list, previous_block_hash: str, hash=None, nonce=0, timestamp=None, message=""):
        self.id = id
        self.transactions: List[Transaction] = transactions
        self.previous_block_hash = previous_block_hash
        self.hash = hash
        self.nonce = nonce
        self.timestamp = timestamp
        self.message = message
        # self.signature = signature
        self.sc_data = {}

    def serialize(self, strict=False):
        if not strict:
            return json.dumps({
                "id": self.id,
                "transactions": [json.loads(i.serialize(True)) for i in self.transactions],
                "previous_block_hash": self.previous_block_hash,
                "timestamp": self.timestamp,
                "message": base64.b64encode(self.message.encode()).decode(),
                "sc_data": self.sc_data,
                "nonce": self.nonce
            })
        elif strict:
            return json.dumps({
                "id": self.id,
                "transactions": [json.loads(i.serialize(True)) for i in self.transactions],
                "previous_block_hash": self.previous_block_hash,
                "timestamp": self.timestamp,
                "message": base64.b64encode(self.message.encode()).decode(),
                "sc_data": self.sc_data,
                "nonce": self.nonce,
                "hash": self.hash,
                # "signature": self.signature
            })

    @staticmethod
    def from_dict(source):
        return NewBlock(id=source["id"],
                        transactions=[Transaction.from_dict(i) for i in source["transactions"]],
                        previous_block_hash=source["previous_block_hash"],
                        hash=source["hash"],
                        nonce=source["nonce"],
                        timestamp=source["timestamp"],
                        message=base64.b64decode(source["message"]).decode())

    def get_total_fee(self):
        fee = 0

        for transaction in self.transactions:
            fee += transaction.get_total_fee()

        return fee

    def get_size(self):
        return len(self.serialize(True).encode('utf-8'))

    def get_owner_public_key(self):
        for tx in self.transactions:
            for out in tx.outputs:
                if out.type == "reward":
                    return tx.public_key
