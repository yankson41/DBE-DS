# In this script the central are stored

import socket

# get the IP-Adress of the machine
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(("8.8.8.8", 80))
myIP = sock.getsockname()[0]

"""
declaration of variables for encoding, decoding messages
for the address for multicasts
and for Leadserver and neighbour
"""

buffer = 1024
format = 'utf-8'
multicast_IP = '224.0.0.0'
Leadserver = ''
neighbour = ''
# definition of lists for clients and servers
server_overview = []
client_overview = []

# central state variables
client_running = False
network_changed = False
Leadserver_crashed = ''
DuplicateServer_crashed = ''
