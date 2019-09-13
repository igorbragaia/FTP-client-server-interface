from ftp import FTP
import socket
import os
import re
import sys
import json
import shutil


pathRegex = "([a-zA-Z0-9/.])*"


class FTPServer(FTP):
    def __init__(self):
        super().__init__()
        self.status = None
        self.tcp = None

    def __payload(self, path, basepath, data=None):
        payload = {
            'path': '~/{0}'.format(os.path.relpath(path, basepath)) if self.status == 'AUTHENTICATED' else '',
            'data': data
        }
        return json.dumps(payload, ensure_ascii=True).encode('utf8')

    def connect(self, host='127.0.0.1', port=5000):
        try:
            self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp.bind((host, port))
            self.tcp.listen(1)
            self.status = 'NOT AUTHENTICATED'
            return [True, None]
        except Exception as e:
            return [False, e]

    def close(self):
        if self.tcp is not None:
            self.tcp.close()
            self.tcp = None
            self.status = None
            print("server conn closed")

    def run(self):
        self.connect()
        while True:
            con, cliente = self.tcp.accept()
            base_path = os.path.join(os.getcwd(), "files")
            path = os.path.join(os.getcwd(), "files")
            print('Conectado por', cliente)
            self.status = 'NOT AUTHENTICATED'
            con.send(self.__payload(path, base_path, data='ENTER YOUR AUTH CODE'))
            while True:
                msg = con.recv(1024).decode('ascii')
                if not msg:
                    break

                print(cliente, msg)
                if self.status == 'NOT AUTHENTICATED':
                    if msg == 'codigo':
                        self.status = 'AUTHENTICATED'
                        con.send(self.__payload(path, base_path, data='LOGGED IN'))
                    else:
                        con.send(self.__payload(path, base_path, data='PERMISSION DENIED\nENTER YOUR AUTH CODE'))
                elif self.status == 'AUTHENTICATED':
                    # **********************************
                    # NAVEGACAO E LISTAGEM DE DIRETORIOS
                    # **********************************
                    # $ cd <dirname>
                    if re.search('^cd {0}$'.format(pathRegex), msg):
                        dirname = re.split('cd ', msg)[1]
                        new_path = os.path.realpath(os.path.join(path, dirname))
                        if os.path.exists(new_path) and os.path.isdir(new_path) \
                                and not str.endswith(os.path.relpath(new_path, base_path), '..'):
                            path = new_path
                            con.send(self.__payload(path, base_path))
                        else:
                            con.send(self.__payload(path, base_path, data='No such file or directory'))
                    # $ ls <dirname>
                    elif re.search('^ls {0}$'.format(pathRegex), msg):
                        dirname = re.split('ls ', msg)[1]
                        new_path = os.path.realpath(os.path.join(path, dirname))
                        if os.path.exists(new_path) and os.path.isdir(new_path) \
                                and not str.endswith(os.path.relpath(new_path, base_path), '..'):
                            content = os.listdir(new_path)
                            content_str = "\t".join(content)
                            con.send(self.__payload(path, base_path, data=content_str))
                        else:
                            con.send(self.__payload(path, base_path, data='No such file or directory'))
                    # $ ls
                    elif re.search('^ls$'.format(pathRegex), msg):
                        content = os.listdir(path)
                        content_str = "\t".join(content)
                        con.send(self.__payload(path, base_path, data=content_str))
                    # $ pwd
                    elif re.search("^pwd$".format(pathRegex), msg):
                        con.send(self.__payload(path, base_path, data=os.path.relpath(path, base_path)))
                    # *************************
                    # MANIPULACAO DE DIRETORIOS
                    # *************************
                    # $ mkdir <dirname>
                    elif re.search("^mkdir {0}$".format(pathRegex), msg):
                        dirname = re.split('mkdir ', msg)[1]
                        dirname = os.path.realpath(os.path.join(base_path, dirname))
                        previous_dir = os.path.realpath(os.path.join(dirname, '..'))
                        if not os.path.exists(dirname) and os.path.isdir(previous_dir) \
                            and not str.endswith(os.path.relpath(previous_dir, base_path), '..'):
                            os.mkdir(dirname)
                            con.send(self.__payload(path, base_path))
                        else:
                            con.send(self.__payload(path, base_path,
                                                    data='cannot create directory: no such file or directory'))
                    # rmdir <dirname>
                    elif re.search("^rmdir {0}$".format(pathRegex), msg):
                        dirname = re.split('rmdir ', msg)[1]
                        dirname = os.path.realpath(os.path.join(base_path, dirname))
                        if str.endswith(os.path.relpath(path, dirname), '..') and os.path.isdir(dirname):
                            shutil.rmtree(dirname)
                            con.send(self.__payload(path, base_path))
                        else:
                            con.send(self.__payload(path, base_path,
                                                    data='cannot remove directory: no such file or directory'))
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
        self.close()


if __name__ == '__main__':
    server = FTPServer()
    server.run()
