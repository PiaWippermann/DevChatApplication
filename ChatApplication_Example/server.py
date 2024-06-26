# import of required modules
import socket
import hosts
import multicast_receiver
import multicast_sender
import heartbeat
import sys
import threading
import queue


server_port = 10001     # Example port number, change as needed

# Create a new TCP socket for the server
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Get the server's own IP address from the hosts module
host_address = (hosts.my_ip, server_port)

# Create a First-In-First-Out (FIFO) queue for storing messages
fifoQueue = queue.Queue()

# Boolean flag to indicate if the server is running
server_running = True


def handle_clients(client, address, username):
    """
    Handle received messages from connected clients.
    
    Parameters:
    client (socket): The client socket.
    address (tuple): The client's address.
    username (str): The client's username.
    """
    while True:
        try:
            data = client.recv(hosts.buffer_size)
            if not data:
                print(f'Client with Address {address} and Username {username} has disconnected.')
                fifoQueue.put(f'\nClient with Address {address} and Username {username} has disconnected.\n')
                break

            username, message = data.decode(hosts.unicode).split(': ', 1)
            fifoQueue.put(f'{username} said: {message}')
            print(f'New Message from {username}: {message}')

        except Exception as e:
            print(f"An Error occurred: {e}")
            break

    if client in hosts.client_list:
        hosts.client_list.remove(client)
    client.close()


def send_data():
    """
    Send all messages waiting in the queue to all clients.
    """
    message = ''
    while not fifoQueue.empty():
        message += f'{fifoQueue.get()}'
        message += '\n' if not fifoQueue.empty() else ''

    if message:
        for member in hosts.client_list:
            member.send(message.encode(hosts.unicode))


def show_participants():
    """
    Display information about the current server and client situation.
    """
    print(
        f'\nActive Servers: {hosts.server_list} --> The Leader Server is: {hosts.leader}')
    print(f'\nActive Clients: {hosts.client_list}')
    print(f'\nServer Neighbour: {hosts.neighbour}\n')


def start_binding():
    """
    Bind the TCP Server Socket and listen for connections.
    """
    soc.bind(host_address)
    soc.listen()
    print(f'\nServer started and is listening on IP {hosts.my_ip} and PORT {server_port}')

    while server_running:
        try:
            client, address = soc.accept()
            data = client.recv(hosts.buffer_size)

            if data.startswith(b'JOIN'):
                username = data.decode(hosts.unicode).split(' ', 1)[1]
                print(f"Client {username} from {address} has joined the Chat.")
                fifoQueue.put(f'\nClient {username} from {address} has joined the Chat.\n')
                hosts.client_list.append(client)
                thread(handle_clients, (client, address, username))

        except Exception as e:
            print(f"An Error occurred: {e}")
            break


def thread(target, args):
    """
    Create and start a new daemon thread.

    Parameters:
    target (function): The target function is to be executed in the thread.
    args (tuple): The arguments to be passed to the target function.
    """
    thread = threading.Thread(target=target, args=args)
    thread.daemon = True
    thread.start()


if __name__ == '__main__':
    """
    The following block of code will only run if this script is executed directly.
    It will set up the server, handle clients, and manage the server's state.
    """
    multicast_receiver_exist = multicast_sender.send_req_to_multicast()

    if not multicast_receiver_exist:
        hosts.server_list.append(hosts.my_ip)
        hosts.leader = hosts.my_ip

    thread(multicast_receiver.start_multicast_rec, ())
    thread(start_binding, ())
    thread(heartbeat.start_heartbeat, ())

    while True:
        try:
            if hosts.leader == hosts.my_ip and hosts.is_network_changed or hosts.crashed_replica:
                if hosts.crashed_leader:
                    hosts.client_list = []
                multicast_sender.send_req_to_multicast()
                hosts.crashed_leader = False
                hosts.is_network_changed = False
                hosts.replica_crashed = ''
                show_participants()

            if hosts.leader != hosts.my_ip and hosts.is_network_changed:
                hosts.is_network_changed = False
                show_participants()

            send_data()

        except KeyboardInterrupt:
            server_running = False
            soc.close()
            print(f'\nServer on IP {hosts.my_ip} with PORT {server_port} is shutting down.')
            break


