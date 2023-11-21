import json
import math
import ecdsa
import utils
import hashlib


class NewToken:
    def __init__(self, name: str, symbol: str, public_key: str | ecdsa.VerifyingKey, burn=0, commision=0, mintable=False, decimals=2, max_supply=math.inf, attach_file_url="", signature=None):
        self.name = name
        self.symbol = symbol
        self.burn = burn
        self.commision = commision
        self.mintable = mintable
        self.attach_file_url = attach_file_url
        self.decimals = decimals
        self.max_supply = max_supply
        if type(public_key) is str:
            self.public_key = ecdsa.VerifyingKey.from_pem(public_key)
        else:
            self.public_key = public_key
        self.address = utils.generate_serializable_address(self)
        print(f"MY TOKEN ADDRESS IS: {self.address}")
        self.signature = signature

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
                "public_key": self.public_key.to_pem().decode()
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
                "public_key": self.public_key.to_pem().decode(),
                "address": self.address,
                "signature": self.signature
            })

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
                        public_key=source["public_key"],
                        signature=source["signature"])
