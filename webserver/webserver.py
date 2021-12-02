from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from json.decoder import JSONDecodeError
import time, json, argparse


class serverHandler(SimpleHTTPRequestHandler):
    
    def do_GET(self):
        self.path = self.path if self.path != '/' else "/index.html"
        request_ip = ':'.join([str(i) for i in self.client_address])
        request_timestamp = self.log_date_time_string()
        logRequest(request_ip, request_timestamp, self.requestline, self.request_version)
        
        try:
            file_to_open = open(self.path[1:], 'rb').read()
            self.send_response(200)
        except:
            file_to_open = bytes("404 File not found", 'utf-8')
            self.send_response(404)
        self.end_headers()
        try:
            self.wfile.write(file_to_open)
        except:
            print("Unexpected Error occured when trying to write GET response!\n")
    
    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len).decode('utf-8')
    
        request_ip = ':'.join([str(i) for i in self.client_address])
        request_timestamp = self.log_date_time_string()
        request_path = self.path if self.path != '/' else "/index.html"
        addComment(parseComment(post_body, request_path, request_ip, request_timestamp))        
        
        self.send_response(201)
        self.end_headers()

        logRequest(request_ip, request_timestamp, self.requestline, self.request_version)    
            
def logRequest(ip, time, request, version):
    with open('./server_logs/requests.log', 'a') as request_log:
            # Log request as: IP - TIME - REQUEST - PATH - VERSION
            request_log.write(ip + ' - ' + '[' + time + ']' + ' - ' + request + ' - ' + version + '\n')

def parseComment(input, path, ip, timestamp):
    comment_data = input.split('&')     
    for i in range(len(comment_data)):
        comment_data[i] = comment_data[i].split('=')[-1].replace('+', ' ')
    return comment_data + [path, ip, timestamp]

def addComment(newComment):
    try:
        try:    
            with open('./server_logs/comments.json', 'r') as file:
                comment_dict = json.load(file)
        except FileNotFoundError:
            comment_dict = dict()
        except JSONDecodeError: 
            comment_dict = dict()
        # newComment = [Username, comment, rating, path, ip, timestamp]
        if comment_dict.get(newComment[0]): 
            comment_dict[newComment[0]].append(newComment[1:])
        else: 
            comment_dict.update( { newComment[0] : [ newComment[1:] ] } )
        with open('./server_logs/comments.json', 'w') as file:
            json.dump(comment_dict, file, ensure_ascii=False, indent=4)
    except:
        print("Unexpected error occured when trying to add comment to comments.json")

if __name__ == "__main__": 
    try:
        parser = argparse.ArgumentParser(description='CPSC 329 Unessay Webserver')
        parser.add_argument('ip', metavar='ip', type=str, default='localhost', nargs='?', help='The IP number the webserver will utilize.')
        parser.add_argument('port', metavar='port', type=int, default=8080, nargs='?', help='The port number the webserver will utilize.')
        args = parser.parse_args()
        ip = args.ip
        port = args.port
        #PC IP: 10.0.0.84
        #PC PORT: 9555
        #R_Pi IP: 10.0.0.244
        #R_Pi PORT: 9999
        webServer = ThreadingHTTPServer((ip, port), serverHandler)
        print("Server started http://%s:%s" % (ip, port))
        webServer.serve_forever()
    except KeyboardInterrupt:
        print("Keyboard Interrrupt detected! Server stopping!")
        webServer.server_close()
    except:
        print("Unexpected Error! Server stopping!")
        
    