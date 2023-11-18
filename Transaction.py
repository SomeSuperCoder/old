import ecdsa
import utils
import json


class Transaction:
    def __init__(self, public_key: str | ecdsa.VerifyingKey, receiver_id: str, amount: float, token: str, signature=None):
        if type(public_key) is str:
            self.public_key = ecdsa.VerifyingKey.from_pem(public_key)
        else:
            self.public_key = public_key
        self.receiver_id = receiver_id
        self.amount = amount
        self.token = token
        self.signature = signature

    def serialize(self, strict=False):
        if not strict:
            return json.dumps({
                "public_key": self.public_key.to_pem().decode(),
                "receiver_id": self.receiver_id,
                "amount": self.amount,
                "token": self.token
            })
        elif strict:
            return json.dumps({
                "public_key": self.public_key.to_pem().decode(),
                "receiver_id": self.receiver_id,
                "amount": self.amount,
                "token": self.token,
                "signature": self.signature
            })

    @staticmethod
    def from_dict(source):
        return Transaction(public_key=source["public_key"], receiver_id=source["receiver_id"], amount=source["amount"], token=source["token"], signature=source["signature"])
