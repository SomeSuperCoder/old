from Block import NewBlock
from Transaction import Transaction
from Mint import Mint
from Token import NewToken
import json
import utils


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

    def add_user(self):
        pass

    def get_latest_hash(self):
        try:
            return self.blockchain["blocks"][-1]["hash"]
        except IndexError as e:
            return "0"*64

    def get_latest_id(self):
        try:
            return self.blockchain["blocks"][-1]["id"]
        except IndexError:
            return 0

    def validate(self, test):
        # validate hashes
        for i in range(len(self.blockchain["blocks"])):
            one: dict = self.blockchain["blocks"][i]
            block_object = NewBlock(
                                id=one["id"],
                                transactions=[Transaction.from_dict(i) for i in one["transactions"]],
                                previous_block_hash=one["previous_block_hash"],
                                mints=[Mint.from_dict(i) for i in one["mints"]],
                                hash=one["hash"],
                                nonce=one["nonce"],
                                tokens=[NewToken.from_dict(i) for i in one["tokens"]])
            try:
                if one["id"] != 1:
                    if block_object.hash != self.blockchain["blocks"][i+1]["previous_block_hash"]:
                        print("one[\"hash\"] != two[\"previous_block_hash\"]")
                        return False
            except IndexError:
                pass

            print("log stop")
            if utils.get_hash(block_object) != one["hash"]:
                print("get_hash(one) != one[\"hash\"]")

                return False

        return True
