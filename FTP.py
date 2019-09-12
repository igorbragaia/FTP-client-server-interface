import socket
import os, re, sys

pathRegex = "([a-z]|[A-Z]|[/])*[.]([a-z]|[A-Z])*"


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
                    print(got.decode('ascii'))
                if re.search('^close$', msg):
                    print('NO OPENED SESSION')
                elif re.search('^quit$', msg):
                    sys.exit()
            elif self.status == 'CONNECTED':
                host = self.tcp.getpeername()[0]
                port = self.tcp.getpeername()[1]

                msg = input('{0}:{1}: $ '.format(host, port))
                if re.search('^close$', msg):
                    self.close()
                elif re.search('^quit$', msg):
                    self.close()
                    sys.exit()
                elif re.search('^open ([A-Z]|[a-z]|[0-9]|[.])*:[0-9]*$', msg):
                    print("CLOSE YOUR CURRENT SESSION")
                else:
                    self.tcp.send(msg.encode())
                    got = self.tcp.recv(1024)
                    print(got.decode('ascii'))

    def __del__(self):
        self.close()


class FTPServer:
    def __init__(self):
        HOST = '127.0.0.1'  # Endereco IP do Servidor
        PORT = 5000  # Porta que o Servidor esta
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp.bind((HOST, PORT))
        self.tcp.listen(1)
        self.estado = 'NOT AUTHENTICATED'

    def run(self):
        while True:
            con, cliente = self.tcp.accept()
            path = os.path.join(os.getcwd(), "files")
            print('Conectado por', cliente)
            con.send('ENTER YOUR AUTH CODE'.encode())
            while True:
                msg = con.recv(1024).decode('ascii')
                if not msg:
                    break

                print(cliente, msg)
                if self.estado == 'NOT AUTHENTICATED':
                    if msg == 'codigo':
                        self.estado = 'AUTHENTICATED'
                        con.send('LOGGED IN'.encode())
                    else:
                        con.send('PERMISSION DENIED\nENTER YOUR AUTH CODE'.encode())
                elif self.estado == 'AUTHENTICATED':
                    # **********************************
                    # NAVEGACAO E LISTAGEM DE DIRETORIOS
                    # **********************************
                    # $ cd <dirname>
                    if re.search("^cd {0}$".format(pathRegex), msg):
                        dirname = re.split('cd ', msg)[1]
                    # $ ls <dirname>
                    elif re.search("^ls {0}$".format(pathRegex), msg):
                        dirname = re.split('ls ', msg)[1]
                    # $ ls
                    elif re.search("^ls$".format(pathRegex), msg):
                        content = os.listdir(path)
                        content_str = "\t".join(content)
                        con.send(content_str.encode())
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
