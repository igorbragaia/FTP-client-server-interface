from ftp import FTP, Message, decode_message, encode_message, \
    BYTES_LEN, CD, LS, PWD, MKDIR, RMDIR, GET, PUT, DELETE
import socket
import os
import shutil
import base64
import _thread

pathRegex = "([a-zA-Z0-9/.])*"


class FTPServer(FTP):
    def __init__(self):
        super().__init__()
        self.tcp = None
        with open('users.txt', 'r') as f:
            users = f.read()
            self.users = [el.split(';') for el in users.split('\n')]

    @staticmethod
    def make_message(path: str, base_path: str, auth: str, text='', file='', filename=''):
        return Message('response', {
            'path': '~/{0}'.format(os.path.relpath(path, base_path)) if auth == 'AUTHENTICATED' else '',
            'text': text,
            'file': file,
            'filename': filename
        })

    def connect(self, address='127.0.0.1:2121'):
        try:
            host = address.split(':')[0]
            port = int(address.split(':')[1])
            self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp.bind((host, port))
            self.tcp.listen(1)
            return [True, None]
        except Exception as e:
            print(e)
            return [False, e]

    def close(self):
        if self.tcp is not None:
            self.tcp.close()
            self.tcp = None
            print("server conn closed")

    def run(self):
        self.connect()
        while True:
            con, client = self.tcp.accept()
            _thread.start_new_thread(self.connected, tuple([con, client]))

    def connected(self, con, client):
        base_path = os.path.join(os.getcwd(), "files")
        path = os.path.join(os.getcwd(), "files")
        print('Conectado por', client)
        status = 'NOT AUTHENTICATED'

        message = self.make_message(path, base_path, status, text='ENTER YOUR AUTH CODE')
        con.send(encode_message(message))
        while True:
            msg = con.recv(BYTES_LEN)
            if not msg:
                break

            request = decode_message(msg)
            print(client, msg)
            message = self.make_message(path, base_path, status, text='Command not found')
            if status == 'NOT AUTHENTICATED':
                if [request.data['username'], request.data['password']] in self.users:
                    status = 'AUTHENTICATED'
                    message = self.make_message(path, base_path, status, text='LOGGED IN')
                else:
                    message = self.make_message(path, base_path, status,
                                                text='PERMISSION DENIED\nENTER YOUR AUTH CODE')
            elif status == 'AUTHENTICATED':
                # **********************************
                # NAVEGACAO E LISTAGEM DE DIRETORIOS
                # **********************************
                # cd <dirname>
                if request.method == CD:
                    dirname = request.data['dirname']
                    new_path = os.path.realpath(os.path.join(path, dirname))
                    if os.path.exists(new_path) and os.path.isdir(new_path) \
                            and not str.endswith(os.path.relpath(new_path, base_path), '..'):
                        path = new_path
                        message = self.make_message(path, base_path, status)
                    else:
                        message = self.make_message(path, base_path, status, text='No such file or directory')
                # ls <dirname>
                elif request.method == LS:
                    dirname = request.data['dirname']
                    new_path = os.path.realpath(os.path.join(path, dirname))
                    if os.path.exists(new_path) and os.path.isdir(new_path) \
                            and not str.endswith(os.path.relpath(new_path, base_path), '..'):
                        content = os.listdir(new_path)
                        content_str = '\t'.join(content)
                        message = self.make_message(path, base_path, status, text=content_str)
                    else:
                        message = self.make_message(path, base_path, status, text='No such file or directory')
                # pwd
                elif request.method == PWD:
                    message = self.make_message(path, base_path, status, text=os.path.relpath(path, base_path))
                # *************************
                # MANIPULACAO DE DIRETORIOS
                # *************************
                # mkdir <dirname>
                elif request.method == MKDIR:
                    dirname = request.data['dirname']
                    dirname = os.path.realpath(os.path.join(path, dirname))
                    previous_dir = os.path.realpath(os.path.join(dirname, '..'))
                    if not os.path.exists(dirname) and os.path.isdir(previous_dir) \
                            and not str.endswith(os.path.relpath(previous_dir, base_path), '..'):
                        os.mkdir(dirname)
                        message = self.make_message(path, base_path, status)
                    else:
                        message = self.make_message(path, base_path, status,
                                                    text='Cannot create directory: no such file or directory')
                # rmdir <dirname>
                elif request.method == RMDIR:
                    dirname = request.data['dirname']
                    dirname = os.path.realpath(os.path.join(path, dirname))
                    if str.endswith(os.path.relpath(path, dirname), '..') and os.path.isdir(dirname):
                        shutil.rmtree(dirname)
                        message = self.make_message(path, base_path, status)
                    else:
                        message = self.make_message(path, base_path, status,
                                                    text='Cannot remove directory: no such file or directory')
                # ***********************
                # MANIPULACAO DE ARQUIVOS
                # ***********************
                # get <dirname>
                elif request.method == GET:
                    filename_relpath = os.path.join('files', request.data['filename'])
                    filename = os.path.realpath(os.path.join(base_path, request.data['filename']))
                    if os.path.isfile(filename):
                        with open(filename_relpath, 'rb') as file:
                            encoded_file = base64.b64encode(file.read())
                            message = self.make_message(path, base_path, status, file=encoded_file,
                                                        filename=request.data['filename'].split('/')[-1])
                    else:
                        message = self.make_message(path, base_path, status, text='No such file or directory')
                # put <dirname>
                elif request.method == PUT:
                    if request.data['filename'] != '':
                        with open(os.path.join(path, request.data['filename']), "wb") as f:
                            f.write(base64.b64decode(request.data['file']))
                            message = self.make_message(path, base_path, status, text='')
                    else:
                        message = self.make_message(path, base_path, status, text='No such file or directory')
                # delete <dirname>
                elif request.method == DELETE:
                    filename = os.path.realpath(os.path.join(base_path, request.data['filename']))
                    if os.path.isfile(filename):
                        os.remove(filename)
                        message = self.make_message(path, base_path, status, text='')
                    else:
                        message = self.make_message(path, base_path, status, text='No such file or directory')

            con.send(encode_message(message))

        print('Finalizando conexao do cliente', client)
        con.close()

    def __del__(self):
        self.close()


if __name__ == '__main__':
    server = FTPServer()
    server.run()
