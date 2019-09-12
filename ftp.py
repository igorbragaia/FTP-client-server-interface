import socket
import os
import re
import sys
import json


pathRegex = "([a-zA-Z0-9/.])*"


class FTPClient:
    def __init__(self):
        self.status = 'NOT CONNECTED'
        self.tcp = None

    def connect(self, host: str, port: int):
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp.connect((host, port))
        self.status = 'CONNECTED'

    def close(self):
        if self.tcp is not None:
            self.tcp.close()
            self.status = 'NOT CONNECTED'

    def run(self):
        print('Para sair use CTRL+X\n')
        # **********************************
        # GERENCIAMENTO DE CONEXOES
        # **********************************
        begin = True
        dirname = ''
        while begin or msg != '\x18':
            begin = False
            if self.status == 'NOT CONNECTED':
                msg = input('$ ')
                if re.search('^open ([A-Z]|[a-z]|[0-9]|[.])*:[0-9]*$', msg):
                    path = re.split('open ', msg)
                    server = path[1].split(':')[0]
                    port = path[1].split(':')[1]
                    self.connect(server, int(port))
                    got = self.tcp.recv(1024)
                    got_dict = json.loads(got.decode('ascii'))
                    data = got_dict['data']
                    if data:
                        print(data)
                if re.search('^close$', msg):
                    print('NO OPENED SESSION')
                elif re.search('^quit$', msg):
                    sys.exit()
            elif self.status == 'CONNECTED':
                host = self.tcp.getpeername()[0]
                port = self.tcp.getpeername()[1]

                msg = input('{0}:{1}:{2}$ '.format(host, port, dirname))
                if re.search('^close$', msg):
                    self.close()
                elif re.search('^quit$', msg):
                    self.close()
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


class FTPServer:
    def __init__(self, host='127.0.0.1', port=5000):
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp.bind((host, port))
        self.tcp.listen(1)
        self.estado = 'NOT AUTHENTICATED'

    def payload(self, path, basepath, data=None):
        payload = {
            'path': '~/{0}'.format(os.path.relpath(path, basepath)) if self.estado == 'AUTHENTICATED' else '',
            'data': data
        }
        return json.dumps(payload, ensure_ascii=True).encode('utf8')

    def run(self):
        while True:
            con, cliente = self.tcp.accept()
            base_path = os.path.join(os.getcwd(), "files")
            path = os.path.join(os.getcwd(), "files")
            print('Conectado por', cliente)
            con.send(self.payload(path, base_path, data='ENTER YOUR AUTH CODE'))
            while True:
                msg = con.recv(1024).decode('ascii')
                if not msg:
                    break

                print(cliente, msg)
                if self.estado == 'NOT AUTHENTICATED':
                    if msg == 'codigo':
                        self.estado = 'AUTHENTICATED'
                        con.send(self.payload(path, base_path, data='LOGGED IN'))
                    else:
                        con.send(self.payload(path, base_path, data='PERMISSION DENIED\nENTER YOUR AUTH CODE'))
                elif self.estado == 'AUTHENTICATED':
                    # **********************************
                    # NAVEGACAO E LISTAGEM DE DIRETORIOS
                    # **********************************
                    # $ cd <dirname>
                    if re.search('^cd {0}$'.format(pathRegex), msg):
                        dirname = re.split('cd ', msg)[1]
                        new_path = os.path.realpath(os.path.join(path, dirname))
                        if os.path.exists(new_path) and os.path.isdir(new_path) \
                                and os.path.relpath(new_path, base_path) != '..':
                            path = new_path
                            con.send(self.payload(path, base_path))
                        else:
                            con.send(self.payload(path, base_path, data='No such file or directory'))
                    # $ ls <dirname>
                    elif re.search('^ls {0}$'.format(pathRegex), msg):
                        dirname = re.split('ls ', msg)[1]
                        new_path = os.path.realpath(os.path.join(path, dirname))
                        if os.path.exists(new_path) and os.path.isdir(new_path) \
                                and os.path.relpath(new_path, base_path) != '..':
                            content = os.listdir(new_path)
                            content_str = "\t".join(content)
                            con.send(self.payload(path, base_path, data=content_str))
                        else:
                            con.send(self.payload(path, base_path, data='No such file or directory'))
                    # $ ls
                    elif re.search('^ls$'.format(pathRegex), msg):
                        content = os.listdir(path)
                        content_str = "\t".join(content)
                        con.send(self.payload(path, base_path, data=content_str))
                    # $ pwd
                    elif re.search("^pwd$".format(pathRegex), msg):
                        dirname = re.split('pwd ', msg)[1]
                    # *************************
                    # MANIPULACAO DE DIRETORIOS
                    # *************************
                    # $ mkdir <dirname>
                    elif re.search("^mkdir {0}$".format(pathRegex), msg):
                        dirname = re.split('mkdir ', msg)[1]
                    # rmdir <dirname>
                    elif re.search("^rmdir {0}$".format(pathRegex), msg):
                        dirname = re.split('rmdir ', msg)[1]
                    # ***********************
                    # MANIPULACAO DE ARQUIVOS
                    # ***********************
                    # get <dirname>
                    elif re.search("^get {0}$".format(pathRegex), msg):
                        dirname = re.split('get ', msg)[1]
                    # put <dirname>
                    elif re.search("^put {0}$".format(pathRegex), msg):
                        dirname = re.split('put ', msg)[1]
                    # delete <dirname>
                    elif re.search("^delete {0}$".format(pathRegex), msg):
                        dirname = re.split('delete ', msg)[1]


            print('Finalizando conexao do cliente', cliente)
            con.close()

    def __del__(self):
        self.tcp.close()
        print("server conn closed")
