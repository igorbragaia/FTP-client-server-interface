import socket
import re
import sys
import json


class FTPClient:
    def __init__(self):
        self.status = 'NOT CONNECTED'
        self.tcp = None

    def connect(self, host: str, port: int):
        try:
            tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp.connect((host, port))
            self.tcp = tcp
            self.status = 'CONNECTED'
            return [True, None]
        except Exception as e:
            return [False, e]

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
                if re.search('^help$', msg):
                    with open('help.txt', 'r') as f:
                        print(f.read())
                elif re.search('^open ([A-Z]|[a-z]|[0-9]|[.])*:[0-9]*$', msg):
                    path = re.split('open ', msg)
                    server = path[1].split(':')[0]
                    port = path[1].split(':')[1]
                    _, e = self.connect(server, int(port))
                    if e:
                        print(e)
                    else:
                        got = self.tcp.recv(1024)
                        got_dict = json.loads(got.decode('ascii'))
                        data = got_dict['data']
                        if data:
                            print(data)
                elif re.search('^close$', msg):
                    print('NO OPENED SESSION')
                elif re.search('^quit$', msg):
                    sys.exit()
                else:
                    print('Command {0} not found'.format(msg))
            elif self.status == 'CONNECTED':
                host = self.tcp.getpeername()[0]
                port = self.tcp.getpeername()[1]

                msg = input('{0}:{1}:{2}$ '.format(host, port, dirname))
                if re.search('^help$', msg):
                    with open('server/help.txt', 'r') as f:
                        print(f.read())
                elif re.search('^close$', msg):
                    self.close()
                elif re.search('^quit$', msg):
                    self.close()
                    sys.exit()
                elif re.search('^open ([A-Z]|[a-z]|[0-9]|[.])*:[0-9]*$', msg):
                    print("CLOSE YOUR CURRENT SESSION")
                else:
                    self.tcp.send(msg.encode())
                    got = self.tcp.recv(1024)
                    got_dict = json.loads(got.decode('ascii'))
                    dirname = got_dict['path']
                    data = got_dict['data']
                    if data:
                        print(data)

    def __del__(self):
        self.close()


if __name__ == '__main__':
    client = FTPClient()
    client.run()
