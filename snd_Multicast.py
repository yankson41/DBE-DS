import socket
import sys
import struct
import pickle

from time import sleep
import central

# create Port for multicast
multicast_port = 10000

# get the Multicast IP
multicast_address = (central.multicast_IP, multicast_port)

# create the UDP Socket for Multicast
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# set the timeout to the Socket
sock.settimeout(1)

# set the time-to-live for messages to 1 so they do not go past the local network segment
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)


# used from Server
def multicast_send():
    sleep(1)

    # send own variables from the central to the Multicast Receivers(Servers)
    # pickle used for sending data as Lists
    message = pickle.dumps([central.server_overview, central.Leadserver, central.Leadserver_crashed, central.DuplicateServer_crashed,
                            str(central.client_overview)])
    sock.sendto(message, multicast_address)
    print(f'\n[MULTICAST SENDER {central.myIP}] Sending data to Multicast Receivers {multicast_address}',
          file=sys.stderr)

    # if Multicast Receiver exists then return True otherwise return False
    try:
        sock.recvfrom(central.buffer)

        if central.Leadserver == central.myIP:
            print(f'[MULTICAST SENDER {central.myIP}] All Servers have been updated\n',
                  file=sys.stderr)
        return True

    except socket.timeout:
        print(f'[MULTICAST SENDER {central.myIP}] Multicast Receiver not detected',
              file=sys.stderr)
        return False


# used from Clients
def send_join_request():

    print(f'\n[MULTICAST SENDER {central.myIP}] Sending join chat request to Multicast Address {multicast_address}',
          file=sys.stderr)
    message = pickle.dumps(['JOIN', '', '', ''])
    sock.sendto(message, multicast_address)

    # try to get Server Leadserver
    try:
        data, address = sock.recvfrom(central.buffer)
        central.Leadserver = pickle.loads(data)[0]
        return True

    except socket.timeout:
        print(f'[MULTICAST SENDER {central.myIP}] Multicast Receiver not detected -> Chat Server is offline.',
              file=sys.stderr)
        return False
