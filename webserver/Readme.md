README: Target Webserver + Website
Authors: Brody Long

The webserver is a basic implementation of the built in http.server library. It is set up to handle simple GET and POST requests
in order to serve files and media playback to connected users, and to recieve and process comments inputted by connected users.
Video playback is implemented using the video-js library, for more info on video-js see: https://docs.videojs.com/
Everytime a new request is recieved and processed by the webserver, the request is logged in requests.log. Each entry in the log
is in the form: IP - TIME - REQUEST - PATH - VERSION - CPU USAGE WARNING (optional). The optional CPU usage warning is added to
the end of the log whenever CPU usage is above 65%, to get a better idea of what is happening to the server at the time of an 
attack. Both the comment dictionary and request log file are located in the server_logs folder.

Usage: The webserver is run by executing the following command via the command line:
	
	python3 webserver.py IP_NUMBER PORT_NUMBER

If no command line arguments are provided, the server address defaults to "localhost:8080".
The server is shutdown by simply entering the keyboard interrupt: ^C