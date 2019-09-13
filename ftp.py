from abc import ABC, abstractmethod
import simplejson as json


class FTP(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def connect(self, host, port):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def run(self):
        pass


class Message(object):
    def __init__(self, method: str, data: dict):
        self.method = method
        self.data = data


def encode_object(obj: object) -> str:
    return json.dumps(obj.__dict__)


def decode_object(encoded_obj: str) -> object:
    return Message(**json.loads(encoded_obj))
