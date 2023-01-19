# get the IP-Adress of current device
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(("8.8.8.8", 80))
myIP = sock.getsockname()[0]

# General variables
server_port = 10001
buffer = 1024
format = 'utf-8'

# Variables for faulthandling
Leadserver = ''
neighbour = ''
client_running = False
network_changed = False
Leadserver_crashed = ''
DuplicateServer_crashed = ''

# Variables for multicast and lists
multicast_IP = '224.0.0.0'
multicast_port = 10000
server_overview = []
client_overview = []