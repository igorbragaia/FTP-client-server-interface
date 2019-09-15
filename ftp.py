from abc import ABC, abstractmethod
import simplejson as json

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


class Message(object):
    def __init__(self, method: str, data: dict):
        self.method = method
        self.data = data


class FTP(ABC):
    def __init__(self):
        super().__init__()
        self.tcp = None

    @abstractmethod
    def connect(self, address: str):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def run(self):
        pass

    @staticmethod
    def send(con, message: Message):
        encoded_message = json.dumps(message.__dict__).encode('utf8')
        con.send(encoded_message)

    @staticmethod
    def recv(con):
        encoded_message = con.recv(BYTES_LEN)
        if not encoded_message:
            return None
        decoded_message = Message(**json.loads(encoded_message.decode('utf8')))
        return decoded_message
