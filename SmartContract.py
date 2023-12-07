import json
import base64
import config
import utils
import time
import docker
import os


class SmartContract:
    def __init__(self, code, language="python", nonce=0, docs=""):
        self.nonce = nonce

        if language == "python":
            if "eval" in code or "exec" in code or "import" in code:
                self.code = ""
            else:
                self.code = config.sc_code_prefix + code

        else:
            self.code = ""

        self.docs = docs
        self.language = language
        self.address = utils.generate_serializable_address(self)

        print("The code is:")
        print(self.code)

    def execute(self):
        with open("sc_code.py", "w") as file:
            file.write(self.code)
        # Connect to the Docker daemon
        start = time.perf_counter()

        client = docker.from_env()

        print("Start create")
        # Create a container from the alpine image
        container = client.containers.run('python:3.11-alpine', detach=True, remove=True, tty=True, volumes={
            os.getcwd(): {'bind': '/code', 'mode': 'ro'},
            os.path.join(os.getcwd(), "result"): {'bind': '/result', 'mode': 'rw'}
        })
        print("End create")

        if self.language == "python":
            # Execute the /code/contract.py file in the container
            container.exec_run('pip install -r /code/requirements.txt')
            container.exec_run('python3 /code/sc_code.py')

        print("Pre stop")

        container.stop()

        print("End exec")

        with open("result/result.json", "r") as file:
            return file.read(), time.perf_counter()-start

    def serialize(self, strict=False):
        return json.dumps(
            {
                "address": self.address if strict else None,
                "nonce": self.nonce,
                "language": self.language,
                "code": base64.b64encode(self.code.encode()).decode(),
                "docs": base64.b64encode(self.docs.encode()).decode()
            }
        )

    @staticmethod
    def from_dict(source):
        return SmartContract(
                code=base64.b64decode(source["code"]).decode(),
                docs=base64.b64decode(source["docs"]).decode(),
                nonce=source["nonce"],
                language=source["language"]
        )
