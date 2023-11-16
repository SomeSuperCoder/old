import json
import ecdsa
import utils
import hashlib


class Mint:
    def __init__(self, amount: float, token_address: str, signature_r=None, signature_s=None):
        self.token_address = token_address
        self.amount = amount
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
                "token_address": self.token_address,
                "amount": self.amount
            })
        elif strict:
            return json.dumps({
                "token_address": self.token_address,
                "amount": self.amount,
                "signature_r": self.signature_r,
                "signature_s": self.signature_s
            })

    @staticmethod
    def from_dict(source):
        return Mint(
            token_address=source["token_address"],
            amount=source["amount"],
            signature_r=source["signature_r"],
            signature_s=source["signature_s"]
        )
