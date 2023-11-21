from Block import NewBlock
from Transaction import Transaction
from Mint import Mint
from Token import NewToken
import json
import utils
import config
import binascii
import hashlib


class BlockChain:
    def __init__(self):
        self.blockchain = {
            "version": 1,
            "blocks": [],
        }

    def load(self, filename="blockchain.json"):
        try:
            with open(filename, "r") as f:
                self.blockchain = json.loads(f.read())
        except FileNotFoundError:
            pass

    def save(self, filename="blockchain.json"):
        with open(filename, "w") as f:
            f.write(json.dumps(self.blockchain, indent="    "))

    def add_block(self, block):
        self.blockchain["blocks"].append(json.loads(block.serialize(True)))
        self.save()

    def get_latest_hash(self):
        try:
            return self.blockchain["blocks"][-1]["hash"]
        except IndexError:
            return "0"*64

    def get_latest_block_id(self):
        try:
            return self.blockchain["blocks"][-1]["id"]
        except IndexError:
            return 0

    def get_latest_transaction_id(self):
        try:
            return NewBlock.from_dict(self.blockchain["blocks"][-1]).transactions[-1].id
        except IndexError:
            return 0

    def validate(self):
        input_hash_list = []

        for i in range(len(self.blockchain["blocks"])):
            one: dict = self.blockchain["blocks"][i]
            block_object = NewBlock.from_dict(one)

            # validate hashes
            try:
                if one["id"] != 1:
                    if block_object.hash != self.blockchain["blocks"][i+1]["previous_block_hash"]:
                        print("one[\"hash\"] != two[\"previous_block_hash\"]")
                        return False
            except IndexError:
                pass

            if utils.get_hash(block_object) != one["hash"]:
                print("get_hash(one) != one[\"hash\"]")

                return False

            # validate transactions
            for transaction in block_object.transactions:
                if not utils.verify(transaction):
                    return False

            # validate tokens
            for token in block_object.tokens:
                if not utils.verify(token):
                    return False

            # validate mints
            for mint in block_object.mints:
                if not utils.verify(mint):
                    return False
                array = [[token.address, token.public_key] for token in block_object.tokens]

                if not any(item == [mint.token_address, mint.public_key] for item in array):
                    return False

            # validate difficulty
            if block_object.hash[:config.strict] != "0" * config.strict:
                return False

            # check for input double usage
            for tr in block_object.transactions:
                for _in in tr.inputs:
                    input_hash_list.append(binascii.hexlify(hashlib.sha256(_in.serialize().encode()).digest()).decode())

            if len(input_hash_list) != len(set(input_hash_list)):
                return False

        return True
