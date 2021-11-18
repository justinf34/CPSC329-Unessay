import threading
import socket
import argparse
import os
import sys

RECV_BUFFER = 4096
ENCODING = 'utf-8'


class Send(threading.Thread):

    def __init__(self, sock: socket.socket) -> None:
        super().__init__()
        self.sock = sock

    def run(self):
        print('Can enter commands now.')
        while True:
            sys.stdout.flush()
            message = sys.stdin.readline()[:-1]

            if message.upper() == 'QUIT':
                # TODO: send message to server that socket is leaving
                break
            else:
                self.sock.sendall(message.encode(ENCODING))

        print('Quiting...')
        self.sock.close()
        os._exit(0)


class Receive(threading.Thread):

    def __init__(self, sock: socket.socket, client_type: str, client) -> None:
        super().__init__()
        self.sock = sock
        self.client_type = client_type
        self.client = client

    def run(self) -> None:
        while True:
            recv_data = self.sock.recv(RECV_BUFFER)

            if recv_data:
                self._req_handler(recv_data)
            else:
                print('Disconnected from server')
                print('Quitting...')
                self.sock.close()
                os._exit(0)

    def _req_handler(self, recv_data: bytes) -> None:
        recv_data_str = str(recv_data, ENCODING)
        try:
            request = recv_data_str.split(':')
            req_type = request[0]
            if req_type == 'whoami':
                print('Sending identification...')
                response = f'iam:{self.client_type}'.encode(ENCODING)
                self.sock.send(response)
            elif req_type == 'iam':
                if request[1] == 'success':
                    self.client.set_authenticated()
                else:
                    print('Cannot be authenticated.')
                    print('Quitting...')
                    self.sock.close()
                    os._exit(0)
            else:
                print(
                    f'\rReceived command/response -> {recv_data_str}')
                # TODO: client custom client handler code here

        except ValueError as e:
            print('Could not parse request')
            # raise e


class Client:

    def __init__(self, host: str, port: int, type: str) -> None:
        self.host = host
        self.port = port
        self.type = type
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.authenticated = False

    def start(self) -> None:
        print(f'Connecting to {self.host}:{self.port}...')
        self.sock.connect((self.host, self.port))
        print(f'Successfully connected to {self.host}:{self.port}...')

        # try:
        receive = Receive(self.sock, self.type, self)
        receive.start()
        # if self.type == 'master':
        #     send = Send(self.sock)
        #     send.start()
        # except KeyboardInterrupt:
        #     print("caught keyboard interrupt, exiting")
        # except Exception as e:
        #     print(f'ran into an error:\n{e}')
        # finally:
        #     self.sock.close()
        #     os._exit(0)

    def set_authenticated(self) -> None:
        self.authenticated = True
        print('Successfully authorized')
        if self.type == 'master':
            send = Send(self.sock)
            send.start()


def main() -> None:
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Client CLI')
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int,
                        default=8080, help='TCP port (default 8080)')
    parser.add_argument('-t', metavar='TYPE', type=str,
                        default='master', help='Client type (master or bot)')
    args = parser.parse_args()
    client = Client(args.host, args.p, args.t)
    client.start()
