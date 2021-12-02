# Handler Server

The handler server will act as a middle-man for the attacker client and bot agents. It relays commands from the attacker client to bot agents connected to the server. It should be able to handle multiple bot agents and one master client. The master client should be able to request the list and information about the bot agents connected to the server. Both the attacker client and both agents will be connected to the server via TCP connection. To implement this server, a Python socket server will be created using the `socket` library. The server will be hosted in an EC2 instance.

### How to run

1. Make sure your system has `python 3.9` and install `pipenv`
2. Run `pipenv shell` to set the environment to use `python 3.9`
3. Enter the command `python server.py`
   - Can change the default address from `''` to any address using the `-a <address>` argument
   - Can change the default port from `8080` to any port using the `-p <port>` argument
