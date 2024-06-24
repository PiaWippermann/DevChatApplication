import socket
import threading
import os

from time import sleep
import hosts
import multicast_sender

server_port = 10001


def thread(target, args):
    """Creates and starts a new daemon thread."""
    thread = threading.Thread(target=target, args=args)
    thread.daemon = True
    thread.start() 


def send_messages(username):
    """sending messages to the leader server"""
    global soc
    while True:
        message = input()
        try:
            send_message = f'{username}: {message}'.encode(hosts.unicode)
            soc.send(send_message)
        except Exception as e:
            print(e)
            soc.close()
            break



def receive_messages():
    """receiving messages from the leader server"""
    global soc
    while True:
        try:
            data = soc.recv(hosts.buffer_size)
            if not data:
                print("\nConnection to the server lost. Please wait for the reconnection.")
                soc.close()
                sleep(3)
                connect(username)
            print(data.decode(hosts.unicode))

        except socket.error as e:
            if e.errno == 10054:
                soc.close()
                print("\nConnection to the server lost. Please wait for the reconnection.")
                sleep(4)
                connect(username)
        except Exception as e:
            print(e)
            soc.close()
            break



def connect(username):
    """Create client socket and connect to server leader"""
    global soc

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_exist = multicast_sender.send_join_request()

    if server_exist:
        leader_address = (hosts.leader, server_port)
        print(f'This is the server leader: {leader_address}')

        soc.connect(leader_address)
        soc.send(f'JOIN {username}'.encode(hosts.unicode))
        print(f"Welcome to the Chat Room!")

    else:
        print("Please try again later.")
        os._exit(0)


# main Thread
if __name__ == '__main__':

    try:
        print("You try to enter the chat room.")
        username = input("Username: ")

        connect(username)
        thread(send_messages, (username,))
        thread(receive_messages, ())

        while True:
            pass

    except KeyboardInterrupt:
        print("\nYou left the chat room")
