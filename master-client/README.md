# Master Client

The master client will send messages to the handler server to then be relayed to connected bots. The master client creates a socket to connect to the server and identifies itself as master for authentication. The master client can request and display a list of connected bots, and can set the target server and attack type for the bots. The master client can stop and start the attack once the relevant target information has been set. The master client can disconnect from the server manually or as a result of error handling. Whenever the connection is closed, the client will write a log of all events in that session and the program will terminate.

### How to run

1. Make sure your system has `python 3.9` 
2. Enter the command `python server.py`
   - Can change the default address from `''` to any address using the `host <address>` argument
   - Can change the default port from `8080` to any port using the `-p <port>` argument
