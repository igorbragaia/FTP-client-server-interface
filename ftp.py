from abc import ABC, abstractmethod


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
