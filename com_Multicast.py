# this is a Multicast Receiver

import socket
import sys
import struct
import pickle

from time import sleep
import central


# create Port for multicast
multicast_port = 10000

# get the Multicast Address
multicast_address = (central.multicast_IP, multicast_port)

# create the UDP Socket for Multicast
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# set the timeout to the Socket
sock.settimeout(1)

# set the time-to-live for messages to 1 so they do not go past the local network segment
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

# get the Multicast IP
multicast_ip = central.multicast_IP
server_address = ('', multicast_port)


# used from Servers
def multicast_receive():

    # bind the Server address
    sock.bind(server_address)

    # tell the operating system to add the socket to the multicast group on all interfaces
    group = socket.inet_aton(multicast_ip)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f'\n[MULTICAST RECEIVER {central.myIP}] Starting UDP Socket and listening on Port {multicast}',
          file=sys.stderr)

    # receive/respond loop
    while True:
        try:
            data, address = sock.recvfrom(central.buffer)
            print(f'\n[MULTICAST RECEIVER {central.myIP}] Received data from {address}\n',
                  file=sys.stderr)

            # used from Server Leadserver if a join message was sent from a Chat Client
            if central.Leadserver == central.myIP and pickle.loads(data)[0] == 'JOIN':

                # answer Chat Client with Server Leadserver address
                message = pickle.dumps([central.Leadserver, ''])
                sock.sendto(message, address)
                print(f'[MULTICAST RECEIVER {central.myIP}] Client {address} wants to join the Chat Room\n',
                      file=sys.stderr)

            # used from Server Leadserver if a Server Replica joined
            if len(pickle.loads(data)[0]) == 0:
                central.server_overview.append(
                    address[0]) if address[0] not in central.server_overview else central.server_overview
                sock.sendto('ack'.encode(central.format), address)
                central.network_changed = True

            # used from Server Replicas to update the own variables or if a Server Replica crashed
            elif pickle.loads(data)[1] and central.Leadserver != central.myIP or pickle.loads(data)[3]:
                central.server_overview = pickle.loads(data)[0]
                central.Leadserver = pickle.loads(data)[1]
                central.client_overview = pickle.loads(data)[4]
                print(f'[MULTICAST RECEIVER {central.myIP}] All Data have been updated',
                      file=sys.stderr)

                sock.sendto('ack'.encode(central.format), address)
                central.network_changed = True

        except KeyboardInterrupt:
            print(f'[MULTICAST RECEIVER {central.myIP}] Closing UDP Socket',
                  file=sys.stderr)


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
