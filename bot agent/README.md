# Bot Script

This script is the bot agent component of the DDoS attack. It connects to the handler server (through TCP) and the master client must be running to issue commands to the bot scripts.
It uses Pythons `socket` and `http.client` libraries.
It contains two potential DDoS attacks:
1. RequestAttack() - an HTTP Flood attack (code modified from [pyddos](http://github.com/t7hm1/pyddos) by \___T7hM1___)
2. SlowlorisAttack() - Slowloris attack (code modified from [SlowLoris](https://github.com/0xc0d/Slow-Loris/blob/master/SlowLoris.py) by 0xc0d)

The script was tested on Python 3.8 and 3.9

3 command line arguments are required:
* `-a` : the IP of the handler server
* `-p` : the port of the handler server
* `-t` : the number of threads to use in the attacks
