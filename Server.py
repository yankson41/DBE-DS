# From this Script the MultiServer can be instanciated

import socket
import sys
import threading
import queue

import central
import com_Multicast
import Faulthandling

"""
create Port for server
creating TCP Socket for Server
get the own IP from central
and create a First in First out queue for messages
"""
server_port = 10001
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host_address = (central.myIP, server_port)
message_backlog = queue.Queue()

# This function is used to print some information on the terminal


def print_info():
    print(
        f'\nList of Servers: {central.server_overview} --> The Leadserver is: {central.Leadserver}')
    print(f'\nList of Clients: {central.client_overview}')
    print(f'\nServers Neighbour ==> {central.neighbour}\n')


# standardized for creating and starting Threads
def thread(target, args):
    thread = threading.Thread(target=target, args=args)
    thread.daemon = True
    thread.start()


# send all messages waiting in the Queue to all Clients
def send_message_backlog():
    message = ''
    while not message_backlog.empty():
        message += f'{message_backlog.get()}'
        message += '\n' if not message_backlog.empty() else ''

    if message:
        for member in central.client_overview:
            member.send(message.encode(central.format))


# handle all received messages from connected Clients
def handle_recvd_msgs(client, address):
    while True:
        try:
            data = client.recv(central.buffer)

            # if Client is disconnected or lost the connection
            if not data:
                print(f'{address} disconnected')
                message_backlog.put(f'\n{address} disconnected\n')
                central.client_overview.remove(client)
                client.close()
                break

            message_backlog.put(f'{address} said: {data.decode(central.format)}')
            print(f'Message from {address} ==> {data.decode(central.format)}')

        except Exception as e:
            print(e)
            break


# bind the TCP Server Socket and listen for connections
def binding():
    soc.bind(host_address)
    soc.listen()
    print(f'\nStarting and listening on IP {central.myIP} and on PORT {server_port}',
          file=sys.stderr)

    while True:
        try:
            client, address = soc.accept()
            data = client.recv(central.buffer)

            # used just for Chat-Clients (filter out heartbeat)
            if data:
                print(f'{address} connected')
                message_backlog.put(f'\n{address} connected\n')
                central.client_overview.append(client)
                thread(handle_recvd_msgs, (client, address))

        except Exception as e:
            print(e)
            break


# main Thread
if __name__ == '__main__':

    # trigger Multicast Sender to check if a Multicast Receiver with given Multicast Address from central exists
    multicast_receiver_exist = com_Multicast.multicast_send()

    # append the own IP to the Server List and assign the own IP as the Server Leadserver
    if not multicast_receiver_exist:
        central.server_overview.append(central.myIP)
        central.Leadserver = central.myIP

    # calling functions as Threads
    thread(com_Multicast.multicast_receive, ())
    thread(binding, ())
    thread(Faulthandling.heartbeat_check, ())

    # loop main Thread
    while True:
        try:
            # send Multicast Message to all Multicast Receivers (Servers)
            # used from Server Leadserver or if a Server Replica recognizes another Server Replica crash
            if central.Leadserver == central.myIP and central.network_changed or central.DuplicateServer_crashed:
                if central.Leadserver_crashed:
                    central.client_overview = []
                com_Multicast.multicast_send()
                central.Leadserver_crashed = False
                central.network_changed = False
                central.DuplicateServer_crashed = ''
                print_info()

            # used from Server Replica to set the variable to False
            if central.Leadserver != central.myIP and central.network_changed:
                central.network_changed = False
                print_info()

            # function to send the message_backlog Queue messages
            send_message_backlog()

        except KeyboardInterrupt:
            soc.close()
            print(
                f'\nClosing Server on IP {central.myIP} with PORT {server_port}', file=sys.stderr)
            break
