import datetime

from Block import NewBlock
from Transaction import Transaction
from Mint import Mint
from Token import NewToken
from Validator import Validator

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

        prev_block_id = 0

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
            for token in self.get_token_list():
                if not utils.verify(token):
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

            # validate emptiness
            if block_object.is_empty():
                print("Block is empty!")
                return False

            # validate only one reward
            if not Validator.check_only_one_block_reward(block_object):
                print("Block has more than one reward!")
                return False

            # validate block id
            if block_object.id != prev_block_id+1:
                return False

            prev_block_id += 1

        return True

    def get_token_list(self) -> list[NewToken]:
        result = []
        for i in range(len(self.blockchain["blocks"])):
            one: dict = self.blockchain["blocks"][i]
            block_object = NewBlock.from_dict(one)

            for transaction in block_object.transactions:
                for token in transaction.tokens:
                    result.append(token)

        return result

    def get_transaction_list(self) -> list[NewToken]:
        result = []
        for i in range(len(self.blockchain["blocks"])):
            one: dict = self.blockchain["blocks"][i]
            block_object = NewBlock.from_dict(one)

            for transaction in block_object.transactions:
                result.append(transaction)

        return result

    def get_latest_blocks(self):
        print(-max(len(self.blockchain["blocks"]), config.amount_of_last_blocks_for_checks))
        return self.blockchain[
            "blocks"
        ][
            ::-min(len(self.blockchain["blocks"]), config.amount_of_last_blocks_for_checks)
        ]

    def get_current_difficulty(self):
        latest_block_list = self.get_latest_blocks()
        if len(latest_block_list) < 2:
            return config.strict

        pre_latest = latest_block_list[-2]
        latest_block = latest_block_list[-1]
        zeros = latest_block

        for char in latest_block.hash:
            if char == "0":
                zeros += 1
            else:
                break

        if datetime.datetime.utcfromtimestamp(
                latest_block.timestamp
        ) - datetime.datetime.utcfromtimestamp(
                pre_latest.timestamp
        ) > config.target_block_time:
            zeros -= 1
        if datetime.datetime.utcfromtimestamp(
                latest_block.timestamp
        ) - datetime.datetime.utcfromtimestamp(
            pre_latest.timestamp
        ) < config.target_block_time:
            zeros += 1

        return zeros

    def get_block_by_id(self, id):
        for i in self.blockchain["blocks"]:
            block_object = NewBlock.from_dict(i)

            if block_object.id == id:
                return block_object
