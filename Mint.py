import json
import ecdsa
import utils
import hashlib


class Mint:
    def __init__(self, amount: float, token_address: str, public_key: str | ecdsa.VerifyingKey, signature=None):
        self.token_address = token_address
        self.amount = amount
        self.signature = signature
        if type(public_key) is str:
            self.public_key = ecdsa.VerifyingKey.from_pem(public_key)
        else:
            self.public_key = public_key

    def serialize(self, strict=False):
        if not strict:
            return json.dumps({
                "token_address": self.token_address,
                "amount": self.amount,
                "public_key": self.public_key.to_pem().decode()
            })
        elif strict:
            return json.dumps({
                "token_address": self.token_address,
                "amount": self.amount,
                "public_key": self.public_key.to_pem().decode(),
                "signature": self.signature
            })

    @staticmethod
    def from_dict(source):
        return Mint(
            token_address=source["token_address"],
            amount=source["amount"],
            signature=source["signature"],
            public_key=source["public_key"]
        )
