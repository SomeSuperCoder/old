import json
import math
import ecdsa
import utils
import hashlib


class NewToken:
    def __init__(self, name: str, symbol: str, public_key: str | ecdsa.VerifyingKey, nonce=0, burn=0, commission=0, decimals=2, max_supply=math.inf, attach_file_url="", collection=""):
        self.nonce = nonce
        self.name = name
        self.symbol = symbol
        self.burn = burn
        self.commission = commission
        self.attach_file_url = attach_file_url
        self.decimals = decimals
        self.max_supply = max_supply
        self.collection = collection

        if type(public_key) is str:
            self.public_key = utils.string_to_public_key(public_key)
        else:
            self.public_key = public_key

        self.address = utils.generate_serializable_address(self)
        # self.signature = signature

    def serialize(self, strict=False):
        if not strict:
            return json.dumps({
                "name": self.name,
                "symbol": self.symbol,
                "burn": self.burn,
                "commission": self.commission,
                "attach_file_url": self.attach_file_url,
                "decimals": self.decimals,
                "max_supply": self.max_supply,
                "collection": self.collection,
                "public_key": utils.public_key_to_string(self.public_key),
                "nonce": self.nonce
            })
        else:
            return json.dumps({
                "name": self.name,
                "symbol": self.symbol,
                "burn": self.burn,
                "commission": self.commission,
                "attach_file_url": self.attach_file_url,
                "decimals": self.decimals,
                "max_supply": self.max_supply,
                "collection": self.collection,
                "public_key": utils.public_key_to_string(self.public_key),
                "address": self.address,
                "nonce": self.nonce,
                # "signature": self.signature
            })

    @staticmethod
    def from_dict(source):
        return NewToken(name=source["name"],
                        symbol=source["symbol"],
                        nonce=source["nonce"],
                        burn=source["burn"],
                        commission=source["commission"],
                        attach_file_url=source["attach_file_url"],
                        decimals=source["decimals"],
                        max_supply=source["max_supply"],
                        public_key=source["public_key"],
                        collection=source["collection"])
