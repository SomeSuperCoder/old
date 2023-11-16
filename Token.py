import json
import math
import ecdsa
import utils
import hashlib

from Transaction import Transaction

class NewToken:
    def __init__(self, name: str, symbol: str, owner_id: str, burn=0, commision=0, mintable=False, decimals=2, max_supply=math.inf, attach_file_url="", signature_r=None, signature_s=None):
        self.name = name
        self.symbol = symbol
        self.burn = burn
        self.commision = commision
        self.mintable = mintable
        self.attach_file_url = attach_file_url
        self.decimals = decimals
        self.max_supply = max_supply
        self.owner_id = owner_id
        self.address = utils.generate_token_address(self)
        self.signature_r = signature_r
        self.signature_s = signature_s

    def serialize(self, strict=False):
        if not strict:
            return json.dumps({
                "name": self.name,
                "symbol": self.symbol,
                "burn": self.burn,
                "commision": self.commision,
                "mintable": self.mintable,
                "attach_file_url": self.attach_file_url,
                "decimals": self.decimals,
                "max_supply": self.max_supply,
                "owner_id": self.owner_id
            })
        else:
            return json.dumps({
                "name": self.name,
                "symbol": self.symbol,
                "burn": self.burn,
                "commision": self.commision,
                "mintable": self.mintable,
                "attach_file_url": self.attach_file_url,
                "decimals": self.decimals,
                "max_supply": self.max_supply,
                "owner_id": self.owner_id,
                "address": self.address,
                "signature_r": self.signature_r,
                "signature_s": self.signature_s,
            })

    def send(self, private_key: ecdsa.SigningKey, receiver_id, amount: float):
        transaction = Transaction(sender_key=utils.generate_address(private_key.get_verifying_key()), receiver_id=receiver_id, amount=amount, token=self.symbol)
        transaction.sign(private_key)
        return transaction

    def balance(self, address, blockchain):
        balance = 0

        for i in blockchain.mints:
            if i["symbol"] == self.symbol and i[""]:
                balance += i["amount"]

        return round(balance, self.decimals)

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

    @staticmethod
    def from_dict(source):
        return NewToken(name=source["name"],
                        symbol=source["symbol"],
                        burn=source["burn"],
                        commision=source["commision"],
                        mintable=source["mintable"],
                        attach_file_url=source["attach_file_url"],
                        decimals=source["decimals"],
                        max_supply=source["max_supply"],
                        owner_id=source["owner_id"],
                        signature_r=source["signature_r"],
                        signature_s=source["signature_s"])
