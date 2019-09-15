from ftp import FTP, Message, CD, LS, PWD, MKDIR, RMDIR, GET, PUT, DELETE, CLOSE, OPEN, QUIT, HELP
import socket
import sys
import base64
import os

base_path = os.getcwd()


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
            if not os.path.isdir('files'):
                os.mkdir('files')
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
                if command[0] == HELP:
                    with open('help.txt', 'r') as f:
                        print(f.read())
                elif command[0] == OPEN:
                    if len(command) == 2:
                        _, e = self.connect(command[1])
                        if e:
                            print(e)
                        else:
                            response = super().recv(self.tcp)
                            if response.data['text']:
                                print(response.data['text'])
                    else:
                        invalid = True
                elif command[0] == CLOSE:
                    print('NO OPENED SESSION')
                elif command[0] == QUIT:
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

                    if command[0] == HELP:
                        if len(command) == 1:
                            request = Message(HELP, {
                            })
                    elif command[0] == CD:
                        if len(command) == 2:
                            request = Message(CD, {
                                'dirname': command[1]
                            })
                    elif command[0] == LS:
                        if len(command) == 1:
                            request = Message(LS, {
                                'dirname': ''
                            })
                        elif len(command) == 2:
                            request = Message(LS, {
                                'dirname': command[1]
                            })
                    elif command[0] == PWD:
                        if len(command) == 1:
                            request = Message(PWD, {
                            })
                    elif command[0] == MKDIR:
                        if len(command) == 2:
                            request = Message(MKDIR, {
                                'dirname': command[1]
                            })
                    elif command[0] == RMDIR:
                        if len(command) == 2:
                            request = Message(RMDIR, {
                                'dirname': command[1]
                            })
                    elif command[0] == GET:
                        if len(command) == 2:
                            request = Message(GET, {
                                'filename': command[1]
                            })
                    elif command[0] == PUT:
                        if len(command) == 2:
                            filepath = command[1]
                            if os.path.isfile(filepath):
                                with open(filepath, 'rb') as file:
                                    encoded_file = base64.b64encode(file.read())
                                    request = Message(PUT, {
                                        'filename': filepath.split('/')[-1],
                                        'file': encoded_file
                                    })
                            else:
                                request = Message(PUT, {
                                    'filename': '',
                                    'file': ''
                                })
                    elif command[0] == DELETE:
                        if len(command) == 2:
                            request = Message(DELETE, {
                                'filename': command[1]
                            })
                    elif command[0] == CLOSE:
                        self.close()
                    elif command[0] == QUIT:
                        self.close()
                        sys.exit()

                if self.tcp:
                    super().send(self.tcp, request)
                    response = super().recv(self.tcp)
                    data = response.data
                    dirname = data['path']
                    if data['text']:
                        print(data['text'])
                    if data['file'] != '':
                        if request.method == GET:
                            with open(os.path.join('files', data['filename']), "wb") as f:
                                f.write(base64.b64decode(data['file']))

    def __del__(self):
        self.close()


if __name__ == '__main__':
    client = FTPClient()
    client.run()
