# import of required modules
import os
import socket
import hosts
import multicast_sender
import threading
from time import sleep

server_port = 10001     # Example port number, change as needed

def connect(username):
    """
    Create client socket and connect to the server leader.
    
    Parameters:
    username (str): The username of the client.
    """
    global soc

    # Create a new socket object
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Check if the server exists
    server_exist = multicast_sender.send_join_request()

    if server_exist:
        leader_address = (hosts.leader, server_port)
        print(f'Connection successful! The Server leader is located at: {leader_address}')

        # Connect to the server leader
        soc.connect(leader_address)
        # Send a join message with the username
        soc.send(f'JOIN {username}'.encode(hosts.unicode))
        print(f"Welcome to the Chat Room, {username}! You have successfully connected to the Server Leader.")

    else:
        print("Unable to find a Server at the moment. Please try to connect again later.")
        os._exit(0)


def receive_messages():
    """
    Receive messages from the server leader.
    """
    global soc
    while True:
        try:
            data = soc.recv(hosts.buffer_size)
            if not data:
                print("\nThe Connection to the Server has been lost. Attempting to reconnect...")
                soc.close()
                sleep(3)
                connect(username)
            print(f"Received message: {data.decode(hosts.unicode)}")

        except socket.error as e:
            if e.errno == 10054:
                soc.close()
                print("\nThe Connection to the Server has been unexpectedly lost. Attempting to reconnect...")
                sleep(4)
                connect(username)
        except Exception as e:
            print(f"An error occurred: {e}")
            soc.close()
            break


def send_messages(username):
    """
    Send messages to the server leader.
    
    Parameters:
    username (str): The username of the client.
    """
    global soc
    while True:
        message = input()
        try:
            send_message = f'{username}: {message}'.encode(hosts.unicode)
            soc.send(send_message)
            print(f"Sent message: {message}")
        except Exception as e:
            print(f"An error occurred while sending your message: {e}")
            soc.close()
            break


def thread(target, args):
    """
    Creates and start a new daemon thread.
    
    Parameters:
    target (function): The target function to be executed in the thread.
    args (tuple): The arguments to be passed to the target function.
    """
    thread = threading.Thread(target=target, args=args)
    thread.daemon = True
    thread.start()


# main Thread
if __name__ == '__main__':
    """
    The following block of code will only run if this script is executed directly. 
    If the script is imported as a module in another script, this block will not run.
    This is controlled by checking if the special variable `__name__` is set to `'__main__'`.
    """
    try:
        print("Attempting to enter the chat room.")
        username = input("Please enter your username: ")

        connect(username)
        thread(send_messages, (username,))
        thread(receive_messages, ())

        # Keep the main thread running to keep the daemon threads active
        while True:
            pass

    except KeyboardInterrupt:
        print("\nYou have exited the chat room. Goodbye!")
