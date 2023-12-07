from Token import NewToken
from typing import List
from SmartContract import SmartContract

import ecdsa
import utils
import json
import base64
import builtins


class Transaction:
    def __init__(self, public_key: str | ecdsa.VerifyingKey, outputs, tokens=None, smart_contracts=None, message="", only_after=None, nonce=0, signature=None):
        self.nonce = nonce

        if tokens is None:
            self.tokens = []
        else:
            self.tokens = tokens

        if smart_contracts is None:
            self.smart_contracts = []
        else:
            self.smart_contracts = smart_contracts

        if type(public_key) is str:
            self.public_key = utils.string_to_public_key(public_key)
        else:
            self.public_key = public_key

        self.signature = signature
        self.outputs: List[Output] = outputs
        self.message = utils.crop_message(message)
        self.only_after = only_after
        self.address = utils.generate_serializable_address(self)
        self.set_output_addresses()

    def serialize(self, strict=False):
        if not strict:
            return json.dumps({
                "public_key": utils.public_key_to_string(self.public_key),
                "outputs": [json.loads(i.serialize()) for i in self.outputs],
                "tokens": [json.loads(i.serialize(True)) for i in self.tokens],
                "smart_contracts": [json.loads(i.serialize(True)) for i in self.smart_contracts],
                "message": base64.b64encode(self.message.encode()).decode(),
                "only_after": self.only_after,
                "nonce": self.nonce
            })
        elif strict:
            return json.dumps({
                "address": self.address,
                "public_key": utils.public_key_to_string(self.public_key),
                "outputs": [json.loads(i.serialize()) for i in self.outputs],
                "tokens": [json.loads(i.serialize(True)) for i in self.tokens],
                "smart_contracts": [json.loads(i.serialize(True)) for i in self.smart_contracts],
                "message": base64.b64encode(self.message.encode()).decode(),
                "only_after": self.only_after,
                "nonce": self.nonce,
                "signature": self.signature
            })

    @staticmethod
    def from_dict(source):
        return Transaction(public_key=source["public_key"],
                           # inputs=[Input.from_dict(i) for i in source["inputs"]],
                           outputs=[Output.from_dict(i) for i in source["outputs"]],
                           tokens=[NewToken.from_dict(i) for i in source["tokens"]],
                           smart_contracts=[SmartContract.from_dict(i) for i in source["smart_contracts"]],
                           message=base64.b64decode(source["message"]).decode(),
                           only_after=source["only_after"],
                           # address=source["address"],
                           nonce=source["nonce"],
                           signature=source["signature"])

    def is_empty(self):
        return not bool(len(self.outputs) + len(self.tokens))

    def set_output_addresses(self):
        for i in range(len(self.outputs)):
            self.outputs[i].transaction_address = self.address

    def get_total_fee(self):
        neon_outputs = utils.sort_outputs_by_token(self.outputs)[""]
        fee = 0

        for i in neon_outputs:
            if i.type == "fee":
                fee += i.amount

        fee = abs(fee)
        return fee

    def get_size(self):
        return len(self.serialize(True).encode('utf-8'))

    def get_fee_per_byte(self):
        return self.get_total_fee() / self.get_size()


class Input:
    def __init__(self, transaction_address, output_index):
        self.transaction_address = transaction_address
        self.output_index = output_index

    def serialize(self):
        return json.dumps({
            "transaction_address": self.transaction_address,
            "output_index": self.output_index
        })

    @staticmethod
    def from_dict(source):
        return Input(
            transaction_address=source["transaction_address"],
            output_index=source["output_index"]
        )


class Output:
    def __init__(self, from_, to, amount, token_address, type):
        if builtins.type(from_) is str and from_ != "":
            self.from_ = utils.string_to_public_key(from_)
        else:
            self.from_ = from_

        self.to = to
        self.amount = abs(amount)
        self.token_address = token_address
        self.type = type
        self.transaction_address = None

    def serialize(self):
        return json.dumps({
            "from": utils.public_key_to_string(self.from_) if self.from_ != "" else self.from_,
            "to": self.to,
            "amount": abs(self.amount),
            "token_address": self.token_address,
            "type": self.type
        })

    @staticmethod
    def from_dict(source):
        return Output(
            from_=source["from"],
            to=source["to"],
            amount=abs(source["amount"]),
            token_address=source["token_address"],
            type=source["type"]
        )
