import ecdsa
import hashlib
import json


class Transaction:
    def __init__(self, sender_key: str, receiver_id: str, amount: float, token: str, signature_r=None, signature_s=None):
        self.sender_key = sender_key
        self.receiver_id = receiver_id
        self.amount = amount
        self.token = token
        self.signature_r = signature_r
        self.signature_s = signature_s

    def sign(self, private_key):
        signature = private_key.sign(self.serialize().encode(), hashfunc=hashlib.sha256,
                                     sigencode=ecdsa.util.sigencode_der)
        self.signature_r, self.signature_s = ecdsa.util.sigdecode_der(signature, ecdsa.SECP256k1.order)

    def verify(self, public_key: ecdsa.VerifyingKey):
        try:
            public_key.verify(ecdsa.util.sigencode_der(self.signature_r,
                                                   self.signature_s,
                                                   ecdsa.SECP256k1.order),
                          self.serialize().encode(),
                          hashfunc=hashlib.sha256,
                          sigdecode=ecdsa.util.sigdecode_der)

            return True
        except ecdsa.BadSignatureError:
            return False

    def serialize(self, strict=False):
        if not strict:
            return json.dumps({
                "sender_key": self.sender_key,
                "receiver_id": self.receiver_id,
                "amount": self.amount,
                "token": self.token
            })
        elif strict:
            return json.dumps({
                "sender_key": self.sender_key,
                "receiver_id": self.receiver_id,
                "amount": self.amount,
                "token": self.token,
                "signature_r": self.signature_r,
                "signature_s": self.signature_s
            })

    @staticmethod
    def from_dict(source):
        return Transaction(sender_key=source["sender_key"], receiver_id=source["receiver_id"], amount=source["amount"], token=source["token"], signature_r=source["signature_r"], signature_s=source["signature_s"])
