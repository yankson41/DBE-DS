# This script is needed to perform to detect faults and handle faults connected to the Leadserver (Heartbeats & Leadserver Elecetion)

import socket
import sys

from time import sleep
import central

# create a Port for server
server_port = 10001

def heartbeat_check():
    while True:
        # create the TCP socket for Heartbeat
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc.settimeout(0.5)

        # get own Server Neighbour by using Leadserver Election algorithm
        central.neighbour = start_Leadserver_elec(
            central.server_overview, central.myIP)
        host_address = (central.neighbour, server_port)

        # only executed if a Neighbour is available to whom the Server can establish a connection
        if central.neighbour:
            sleep(5)

            # Heartbeat is realized by connecting to the Neighbour
            try:
                soc.connect(host_address)
                print(f'[HEARTBEAT] Neighbour {central.neighbour} response',
                      file=sys.stderr)

            # if connecting to Neighbour was not possible, the Heartbeat failed -> Neighbour crashed
            except:
                # remove crashed Neighbour from Server List
                central.server_overview.remove(central.neighbour)

                # used if the crashed Neighbour was the Server Leadserver
                if central.Leadserver == central.neighbour:
                    print(f'[HEARTBEAT] Server Leadserver {central.neighbour} crashed',
                          file=sys.stderr)
                    central.Leadserver_crashed = True

                    # assign own IP address as new Server Leadserver
                    central.Leadserver = central.myIP
                    central.network_changed = True

                # used if crashed Neighbour was a Server Replica
                else:
                    print(f'[HEARTBEAT] Server Replica {central.neighbour} crashed',
                          file=sys.stderr)
                    central.DuplicateServer_crashed = 'True'

            finally:
                soc.close()

def form_ring(members):
    sorted_ring_binary = sorted([socket.inet_aton(member)
                                for member in members])
    sorted_ring_ip = [socket.inet_ntoa(node) for node in sorted_ring_binary]
    return sorted_ring_ip


def find_neighbour(members, current_member_ip, direction='left'):
    current_member_index = members.index(
        current_member_ip) if current_member_ip in members else -1
    if current_member_index != -1:
        if direction == 'left':
            if current_member_index + 1 == len(members):
                return members[0]
            else:
                return members[current_member_index + 1]
        else:
            if current_member_index - 1 == 0:
                return members[0]
            else:
                return members[current_member_index - 1]
    else:
        return None


def start_Leadserver_elec(server_overview, Leadserver_server):
    ring = form_ring(server_overview)
    neighbour = find_neighbour(ring, Leadserver_server, 'right')
    return neighbour if neighbour != central.myIP else None
