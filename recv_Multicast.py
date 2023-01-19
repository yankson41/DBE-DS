import central

import socket
import sys
import struct
import pickle

multicast_ip = central.multicast_IP
server_address = ('', central.multicast_port)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# used from Servers
def multicast_receive():

    # bind the Server address
    sock.bind(server_address)

    # tell the operating system to add the socket to the multicast group on all interfaces
    group = socket.inet_aton(multicast_ip)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f'\n[MULTICAST RECEIVER {central.myIP}] Starting UDP Socket and listening on Port {central.multicast_port}')

    # receive/respond loop
    while True:
        try:
            data, address = sock.recvfrom(central.buffer)
            print(f'\n[MULTICAST RECEIVER {central.myIP}] Received data from {address}\n')

            # used from Server Leadserver if a join message was sent from a Chat Client
            if central.Leadserver == central.myIP and pickle.loads(data)[0] == 'JOIN':

                # answer Chat Client with Server Leadserver address
                message = pickle.dumps([central.Leadserver, ''])
                sock.sendto(message, address)
                print(f'[MULTICAST RECEIVER {central.myIP}] Client {address} wants to join the Chat Room\n')

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
                print(f'[MULTICAST RECEIVER {central.myIP}] All Data have been updated')

                sock.sendto('ack'.encode(central.format), address)
                central.network_changed = True

        except KeyboardInterrupt:
            print(f'[MULTICAST RECEIVER {central.myIP}] Closing UDP Socket')