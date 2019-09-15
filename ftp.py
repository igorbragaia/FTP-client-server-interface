from abc import ABC, abstractmethod
import simplejson as json


class FTP(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def connect(self, address: str):
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


def encode_message(message: Message) -> bytes:
    return json.dumps(message.__dict__).encode('utf8')


def decode_message(encoded_message: bytes) -> Message:
    return Message(**json.loads(encoded_message.decode('utf8')))


BYTES_LEN = 1024*1024  # 1MB
HELP = 'help'
CD = 'cd'
LS = 'ls'
PWD = 'pwd'
MKDIR = 'mkdir'
RMDIR = 'rmdir'
GET = 'get'
PUT = 'put'
DELETE = 'delete'
CLOSE = 'close'
OPEN = 'open'
QUIT = 'quit'