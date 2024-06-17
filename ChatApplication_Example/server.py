import socket
import sys
import threading
import queue

import hosts
import multicast_receiver
import multicast_sender
import heartbeat

"""
create Port for server
creating TCP Socket for Server
get the own IP from hosts
and create a First in First out queue for messages
"""
server_port = 10001
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host_address = (hosts.my_ip, server_port)
fifoQueue = queue.Queue()

server_running = True

def show_participants():
    """giving information about the current situation"""
    print(
        f'\nActive Servers: {hosts.server_list} --> The Leader Server is: {hosts.leader}')
    print(f'\nActive Clients: {hosts.client_list}')
    print(f'\nServers Neighbour ==> {hosts.neighbour}\n')



def thread(target, args):
    """create and start threads"""
    thread = threading.Thread(target=target, args=args)
    thread.daemon = True
    thread.start()



def send_data():
    """send all messages waiting in the Queue to all Clients"""
    message = ''
    while not fifoQueue.empty():
        message += f'{fifoQueue.get()}'
        message += '\n' if not fifoQueue.empty() else ''

    if message:
        for member in hosts.client_list:
            member.send(message.encode(hosts.unicode))



def handle_clients(client, address, username):
    """handle all received messages from connected Clients"""
    while True:
        try:
            data = client.recv(hosts.buffer_size)
            if not data:
                print(f'{address} ({username}) disconnected')
                fifoQueue.put(f'\n{address} ({username}) disconnected\n')
                break

            username, message = data.decode(hosts.unicode).split(': ', 1)
            fifoQueue.put(f'{username} said: {message}')
            print(f'New Message from {username}: {message}')

        except Exception as e:
            print(e)
            break

    if client in hosts.client_list:
        hosts.client_list.remove(client)
    client.close()




def start_binding():
    """bind the TCP Server Socket and listen for connections"""
    soc.bind(host_address)
    soc.listen()
    print(f'\nStarting and listening on IP {hosts.my_ip} and on PORT {server_port}')

    while server_running:
        try:
            client, address = soc.accept()
            data = client.recv(hosts.buffer_size)

            if data.startswith(b'JOIN'):
                username = data.decode(hosts.unicode).split(' ', 1)[1]
                print(f"{username} {address} has joined the chat.")
                fifoQueue.put(f'\n{username} {address} has joined the chat\n')
                hosts.client_list.append(client)
                thread(handle_clients, (client, address, username))

        except Exception as e:
            print(e)
            break



if __name__ == '__main__':

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
            print(
                f'\nClosing Server on IP {hosts.my_ip} with PORT {server_port}')
            break


