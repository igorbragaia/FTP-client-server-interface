from ftp import FTP, Message, decode_message, encode_message
import socket
import re
import sys
import json
import base64


class FTPClient(FTP):
    def __init__(self):
        super().__init__()
        self.status = 'NOT CONNECTED'
        self.tcp = None

    def connect(self, address: str):
        try:
            host = address.split(':')[0]
            port = int(address.split(':')[1])
            tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp.connect((host, port))
            self.tcp = tcp
            self.status = 'CONNECTED'
            return [True, None]
        except Exception as e:
            return [False, 'Connection refused']

    def close(self):
        if self.tcp is not None:
            self.tcp.close()
            self.tcp = None
            print('LOGGED OUT')
            self.status = 'NOT CONNECTED'

    def run(self):
        print('''
        #***************************************************************************************#
        # FTP CLIENT                                                                            #
        # Developed by Igor Bragaia (https://igorbragaia.info) using Python3                    #
        # Network classes, ITA 2019.2 - Prof. Lourenço Alves Pereira Jr (https://ljr.github.io) #
        #***************************************************************************************#
        # For help, run                                                                         #
        # $ help                                                                                #
        #***************************************************************************************#
        ''')
        # **********************************
        # GERENCIAMENTO DE CONEXOES
        # **********************************
        begin = True
        dirname = ''
        while begin or msg != '\x18':
            begin = False
            if self.status == 'NOT CONNECTED':
                msg = input('$ ')
                command = [el for el in msg.split(' ') if el != '']

                invalid = False
                if command[0] == 'help':
                    with open('help.txt', 'r') as f:
                        print(f.read())
                elif command[0] == 'open':
                    if len(command) == 2:
                        _, e = self.connect(command[1])
                        if e:
                            print(e)
                        else:
                            encoded_message = self.tcp.recv(1024)
                            decoded_message = decode_message(encoded_message)

                            data = decoded_message.data
                            if data['text']:
                                print(data['text'])
                    else:
                        invalid = True
                elif command[0] == 'close':
                    print('NO OPENED SESSION')
                elif command[0] == 'quit':
                    sys.exit()
                else:
                    invalid = True

                if invalid:
                    print('Command {0} not found'.format(msg))
            elif self.status == 'CONNECTED':
                host = self.tcp.getpeername()[0]
                port = self.tcp.getpeername()[1]

                request = Message('undefined', {'data': msg})
                if dirname == '':
                    username = input('username: ')
                    password = input('passowrd: ')
                    request = Message('login', {'username': username, 'password': password})
                else:
                    msg = input('{0}:{1}:{2}$ '.format(host, port, dirname))
                    command = [el for el in msg.split(' ') if el != '']

                    if command[0] == 'help':
                        if len(command) == 1:
                            request = Message('help', {
                            })
                    elif command[0] == 'cd':
                        if len(command) == 2:
                            request = Message('cd', {
                                'dirname': command[1]
                            })
                    elif command[0] == 'ls':
                        if len(command) == 1:
                            request = Message('ls', {
                                'dirname': ''
                            })
                        elif len(command) == 2:
                            request = Message('ls', {
                                'dirname': command[1]
                            })
                    elif command[0] == 'mkdir':
                        if len(command) == 2:
                            request = Message('mkdir', {
                                'dirname': command[1]
                            })
                    elif command[0] == 'rmdir':
                        if len(command) == 2:
                            request = Message('rmdir', {
                                'dirname': command[1]
                            })
                    elif command[0] == 'get':
                        if len(command) == 2:
                            request = Message('get', {
                                'filename': command[1]
                            })
                    elif command[0] == 'put':
                        if len(command) == 2:
                            request = Message('put', {
                                'filename': command[1]
                            })
                    elif command[0] == 'delete':
                        if len(command) == 2:
                            request = Message('delete', {
                                'filename': command[1]
                            })
                    elif command[0] == 'close':
                        self.close()
                    elif command[0] == 'quit':
                        self.close()
                        sys.exit()

                if self.tcp:
                    self.tcp.send(encode_message(request))
                    encoded_message = self.tcp.recv(4096)
                    server_response = decode_message(encoded_message)
                    data = server_response.data
                    dirname = data['path']
                    if data['text']:
                        print(data['text'])
                    if data['file'] != '':
                        pass

    def __del__(self):
        self.close()


if __name__ == '__main__':
    client = FTPClient()
    client.run()
