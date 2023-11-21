from typing import List

import ecdsa
import utils
import json


class Transaction:
    def __init__(self, public_key: str | ecdsa.VerifyingKey, inputs, outputs, signature=None):
        if type(public_key) is str:
            self.public_key = ecdsa.VerifyingKey.from_pem(public_key)
        else:
            self.public_key = public_key
        self.signature = signature
        self.inputs: List[Input] = inputs
        self.outputs: List[Output] = outputs
        self.address = ""
        self.address = utils.generate_serializable_address(self)

    def serialize(self, strict=False):
        if not strict:
            return json.dumps({
                "address": self.address,
                "public_key": self.public_key.to_pem().decode(),
                "inputs": [json.loads(i.serialize()) for i in self.inputs],
                "outputs": [json.loads(i.serialize()) for i in self.outputs]
            })
        elif strict:
            return json.dumps({
                "address": self.address,
                "public_key": self.public_key.to_pem().decode(),
                "inputs": [json.loads(i.serialize()) for i in self.inputs],
                "outputs": [json.loads(i.serialize()) for i in self.outputs],
                "signature": self.signature
            })

    @staticmethod
    def from_dict(source):
        return Transaction(public_key=source["public_key"],
                           inputs=[Input.from_dict(i) for i in source["inputs"]],
                           outputs=[Output.from_dict(i) for i in source["outputs"]],
                           signature=source["signature"])


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
    def __init__(self, to, amount, token_address, type):
        self.to = to
        self.amount = amount
        self.token_address = token_address
        self.type = type

    def serialize(self):
        return json.dumps({
            "to": self.to,
            "amount": self.amount,
            "token_address": self.token_address,
            "type": self.type
        })

    @staticmethod
    def from_dict(source):
        return Output(
            to=source["to"],
            amount=source["amount"],
            token_address=source["token_address"],
            type=source["type"]
        )
