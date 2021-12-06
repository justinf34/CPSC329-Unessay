# CPSC 329 - Group 12 Unessay
# Target Webserver - Made by Brody Long 30022870

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from json.decoder import JSONDecodeError
from os import cpu_count
import time, json, argparse, psutil


class serverHandler(SimpleHTTPRequestHandler):
    
    def do_GET(self):
        #If user just tries connecting to IP:PORT, server them index.html
        self.path = self.path if self.path != '/' else "/index.html"
        request_ip = ':'.join([str(i) for i in self.client_address])
        request_timestamp = self.log_date_time_string()
        
        try:
            file_to_open = open(self.path[1:], 'rb').read()
            self.send_response(200)
        except:
            #Could not find/open file, return 404 error
            file_to_open = bytes("404 File not found", 'utf-8')
            self.send_response(404)
        self.end_headers()
        try:
            self.wfile.write(file_to_open)
        except:
            print("Unexpected Error occured when trying to write GET response!\n")

        current_cpu_usage = psutil.cpu_percent() #Get the current CPU usage at time of request
        logRequest(request_ip, request_timestamp, self.requestline, self.request_version, current_cpu_usage)
    
    def do_POST(self):
        #Used for parsing and saving comments inputted by users into comments.json
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len).decode('utf-8')

        request_ip = ':'.join([str(i) for i in self.client_address])
        request_timestamp = self.log_date_time_string()
        request_path = self.path if self.path != '/' else "/index.html"
        addComment(parseComment(post_body, request_path, request_ip, request_timestamp))        
        
        self.send_response(201)
        self.end_headers()
        
        current_cpu_usage = psutil.cpu_percent() #Get the current CPU usage at time of request
        logRequest(request_ip, request_timestamp, self.requestline, self.request_version, current_cpu_usage)    
            
def logRequest(ip, time, request, version, cpu_usage):
    with open('./server_logs/requests.log', 'a') as request_log:
            # Log request as: IP - TIME - REQUEST - PATH - VERSION
            log_string = ip + ' - ' + '[' + time + ']' + ' - ' + request + ' - ' + version
            #If CPU usage is high at time of logging, add one of the following 
            if 65 <= cpu_usage < 75:
                log_string += "\n Warning! High CPU usage (" + str(cpu_usage) + "%), server may be under stress!"
            if 75 <= cpu_usage < 85:
                log_string += "\n Warning! Very High CPU usage (" + str(cpu_usage) + "%), server is being attacked! Users may be experiencing loss in service!"
            if 85 <= cpu_usage:
                log_string += "\n Warning! Extreme CPU usage (" + str(cpu_usage) + "%), server is about to die!!! Users are experiencing denial of service!!!"
            log_string += '\n'
            request_log.write(log_string)

def parseComment(input, path, ip, timestamp):
    #The comments generated by the HTML form on the website
    #are in the form: Username='firstname+lastname'&Comment='this+is+a+comment'
    comment_data = input.split('&') 
    for i in range(len(comment_data)):
        comment_data[i] = comment_data[i].split('=')[-1].replace('+', ' ')
    return comment_data + [path, ip, timestamp]

def addComment(newComment):
    try:
        try:    
            with open('./server_logs/comments.json', 'r') as file:
                #If the file exists then load the contents as a JSON object
                comment_dict = json.load(file)
        except FileNotFoundError:
            #Create a new dictionary in the case when no such file exists
            comment_dict = dict()
        except JSONDecodeError: 
            #Create a new dictionary in the case a valid JSON object cannot be created
            comment_dict = dict()
        # newComment = [Username, comment, rating, path, ip, timestamp]
        if comment_dict.get(newComment[0]): 
            #Check if the user commenting is already in the dictionary
            #If so add the comment to this key
            comment_dict[newComment[0]].append(newComment[1:])
        else: 
            #Create a new key:value pair with the username and comment
            comment_dict.update( { newComment[0] : [ newComment[1:] ] } )
        with open('./server_logs/comments.json', 'w') as file:
            #Write the updated dictinary to comments.json
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
    except RuntimeError:
        with open('./server_logs/requests.log', 'a') as request_log:                
            request_log.write(" Warning! All available threads in use! Server is under attack, cannot accept new user connections!\n")
    except:
        print("Unexpected Error! Server stopping!")
        
    