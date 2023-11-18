import json
import ecdsa
import utils
import hashlib


class Mint:
    def __init__(self, amount: float, token_address: str, signature=None):
        self.token_address = token_address
        self.amount = amount
        self.signature = signature

    def serialize(self, strict=False):
        if not strict:
            return json.dumps({
                "token_address": self.token_address,
                "amount": self.amount
            })
        elif strict:
            return json.dumps({
                "token_address": self.token_address,
                "amount": self.amount,
                "signature": self.signature
            })

    @staticmethod
    def from_dict(source):
        return Mint(
            token_address=source["token_address"],
            amount=source["amount"],
            signature=source["signature"],
        )
