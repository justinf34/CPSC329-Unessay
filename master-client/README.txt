README: master-client backend and GUI
Authors: Cole C. and Khaled M.
Requirements: Python 3.8 or later

Outline:

This section of the program covers the master-client, which is the interface the attacker uses to
send orders to the bots remotely. It requries a connection to the IRC server to do so. Once a connection
has been made, the following commands can be issued:

iam:{master or bot} [identifies the client to the server. In this case you would specify 'master']

listbot: [displays a list of currently connected bots in the form "bot1timestamp;bot1ip;bot1port, bot2timestamp;bot2ip;bot2port..."]

chamgeip:{target ip} [sets the target ip]

changeattk:{attack type} [sets attack type]

startattk: [starts the attack]

stopattk: [stops the attack]

disconnect: [disconnects from the server]

When a command is called, the requisite info is sent to the IRC server who communicates the orders to the bots.

Usage:

	From command-line (master-client.py):
	
	If the program is run through the command-line, one must specify command-line arguments to 'master-client.py' in the form:
	-t {'master' or 'bot} -p {port to connect to the IRC through} {ip of the IRC server}.
	If this is done properly, the program will automatically try to connect to the server, and will close
	unless a connection is made. If a connection is successful, the program will allow the user to issue commands
	through the terminal in the form command:{any extra arguments}. Note that the iam command is made automatically
	and so authorization is automatic when connecting to the server.

	From the GUI (masterGUI.py)

	If the program is run through the GUI, simply run the 'masterGUI.py' file to view the application. Note that a connection
	must be made before any of the buttons are functional. To do so, input the ip of the IRC server into the dedicated field 
	and click 'connect.' The IRC connection status indicator light will turn green if your connection is successfull, after which
	you can upload a target ip and use any of the start/stop/quit/update botlist buttons. To close cleanly, press the 'Quit' button
	rather than the window's exit button

	Note: if you would like to test out the master-client you must have an IRC server to connect to. You can set one up on localhost
	by running the 'server.py' file with command-line arguments for localhost ip (see the READMDE in the server section). Then simply
	connect using the localhost ip. You can also run bot scripts on your machine and connect them to the IRC server to see the full range of 
	functionality.








