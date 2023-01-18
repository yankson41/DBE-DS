# From this Script the MultiClient can be instanciated

import socket
import threading
import os

from time import sleep
import central
import com_Multicast

# create Port for server
server_port = 10001

# function for creating Client socket and establishing connection to Server Leadserver
def connect_to_server():
    global soc

    # creating TCP Socket for Client
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # send a join request to Multicast Address for receiving the current Server Leadserver address
    # if there is no response from the Server Leadserver, value False will be returned
    server_exist = com_Multicast.send_join_request()

    if server_exist:
        # assign Server Leadserver address
        Leadserver_address = (central.Leadserver, server_port)
        print(f'This is the server Leadserver: {Leadserver_address}')

        # connect to Server Leadserver
        soc.connect(Leadserver_address)
        soc.send('JOIN'.encode(central.format))
        print("You´ve entered the Chat Room.\nYou can start chatting now.")

    # if there is no Server available, exit the script
    else:
        print("Please try to enter later again.")
        os._exit(0)


# function for sending messages to the Server
def send_message():
    global soc

    while True:
        message = input("")

        try:
            send_message = message.encode(central.format)
            soc.send(send_message)

        except Exception as e:
            print(e)
            break


# function for receiving messages from the Server
def receive_message():
    global soc

    while True:

        try:
            data = soc.recv(central.buffer)
            print(data.decode(central.format))

            # if connection to server is lost (in case of server crash)
            if not data:
                print("\nSorry, the Chat server is currently not available."
                      "Please wait for reconnection with new server Leadserver.")
                soc.close()
                sleep(3)

                # Start reconnecting to new server Leadserver
                connect_to_server()

        except Exception as e:
            print(e)
            break

# standardized for creating and starting Threads

def thread(target, args):
    thread = threading.Thread(target=target, args=args)
    thread.daemon = True
    thread.start()



# main Thread
if __name__ == '__main__':
    try:
        print("You try to enter the chat room.")

        # Connect to Server Leadserver
        connect_to_server()

        # Start Threads for sending and receiving messages from other chat participants
        thread(send_message, ())
        thread(receive_message, ())

        while True:
            pass

    except KeyboardInterrupt:
        print("\nYou left the chat room")
