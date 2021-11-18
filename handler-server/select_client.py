import socket
import select
import errno
import sys

RECV_BUFFER = 4096
ENCODING = 'utf-8'


def req_handler(sock: socket.socket, client_type: str, recv_data: bytes):
    recv_data_str = str(recv_data, ENCODING)
    try:
        request = recv_data_str.split(':')
        req_type = request[0]
        print(request, recv_data_str)
        if req_type == 'whoami':
            print('sending identification...')
            response = f'iam:{client_type}'.encode(ENCODING)
            sock.send(response)
        else:
            print(f'received command/response > {recv_data_str}')
            # TODO: client custom client handler code here

    except ValueError as e:
        print('could not parse request')
        raise e


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("usage:", sys.argv[0], "<host> <port> <client_type>")
        sys.exit(1)

    host, port, client_type = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    client_socket.setblocking(False)

    # while True:
    #     if client_type == 'master':
    #         client_input = input()

    #         if client_input:
    #             request = client_input.encode(ENCODING)
    #             client_socket.send(request)
    #     try:
    #         while True:
    #             recv_data = client_socket.recv(RECV_BUFFER)

    #             if not recv_data:
    #                 client_socket.close()
    #                 sys.exit()

    #             req_handler(client_socket, client_type, recv_data)
    #     except IOError as e:
    #         if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
    #             print(f'Reading error: {str(e)}')
    #             sys.exit()

    #     except KeyboardInterrupt:
    #         print('caught keyboard interrupt, exiting')
    #         client_socket.close()
    #         sys.exit()
    #     except Exception as e:
    #         print(f'Reading error {str(e)}')
    #         sys.exit()

    while True:
        sockets_list = [sys.stdin, client_socket]
        read_sockets, write_socket, error_socket = select.select(
            sockets_list, [], [])
        for socks in read_sockets:
            if socks == client_socket:
                recv_data = socks.recv(RECV_BUFFER)
                if not recv_data:
                    client_socket.close()
                    sys.exit()

                req_handler(client_socket, client_type, recv_data)

        req = sys.stdin.readline()
        if req:
            client_socket.send(req.encode(ENCODING))
            sys.stdout.flush()
