import central

import socket
import sys
import threading
import queue

import recv_Multicast
import snd_Multicast
import Faulthandling

server_port = central.server_port
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host_address = (central.myIP, server_port)

# First in first out Queue for all the messages
message_backlog = queue.Queue()


# bind the TCP Server Socket and listen for connections
def binding():
    soc.bind(host_address)
    soc.listen()
    print(f'\nStarting and listening on IP {central.myIP} and on PORT {server_port}')

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

        except Exception:
            print(Exception)
            break

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

        except Exception:
            print(Exception)
            break

# send all messages waiting in the Queue to all Clients
def send_message_backlog():
    messages = [message_backlog.get() for _ in range(message_backlog.qsize())]
    message = "\n".join(messages)
    if message:
        for member in central.client_overview:
            try:
                member.send(message.encode(central.format))
            except ConnectionError:
                # Handle the error, for example by removing the client from the overview
                central.client_overview.remove(member)
                print(f"Error sending message to {member}, client has been removed from the overview.")

# standardized for creating and starting Threads
def thread(target, args):
    thread = threading.Thread(target=target, args=args)
    thread.daemon = True
    thread.start()

def print_info():
    print(
        f'\nList of Servers: {central.server_overview} --> The Leadserver is: {central.Leadserver}')
    print(f'\nList of Clients: {central.client_overview}')
    print(f'\nServers Neighbour ==> {central.neighbour}\n')


# main Thread
if __name__ == '__main__':

    # trigger Multicast Sender to check if a Multicast Receiver with given Multicast Address from central exists
    multicast_receiver_exist = snd_Multicast.multicast_send()

    # append the own IP to the Server List and assign the own IP as the Server Leadserver
    if not multicast_receiver_exist:
        central.server_overview.append(central.myIP)
        central.Leadserver = central.myIP

    # calling functions as Threads
    thread(recv_Multicast.multicast_receive, ())
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
                snd_Multicast.multicast_send()
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
                f'\nClosing Server on IP {central.myIP} with PORT {server_port}')
            break