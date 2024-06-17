import socket
import sys
import struct
import pickle

import hosts

broadcast_port = 10000
multicast_ip = hosts.multicast_address
server_address = ('', broadcast_port)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)



def start_multicast_rec():
    """This Python function sets up a multicast receiver using a UDP socket.
       It listens for incoming data packets and responds based on the content of the data,
       handling chat client joins and network topology changes."""

    sock.bind(server_address)

    group = socket.inet_aton(multicast_ip)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f'\n[MULTICAST RECEIVER {hosts.my_ip}] Starting UDP Socket and listening on Port {broadcast_port}')

    while True:
        try:
            data, address = sock.recvfrom(hosts.buffer_size)
            print(f'\n[MULTICAST RECEIVER {hosts.my_ip}] Received data from {address}\n')

            if hosts.leader == hosts.my_ip and pickle.loads(data)[0] == 'JOIN':

                message = pickle.dumps([hosts.leader, ''])
                sock.sendto(message, address)
                print(f'[MULTICAST RECEIVER {hosts.my_ip}] Client {address} wants to join the Chat Room\n')

            if len(pickle.loads(data)[0]) == 0:
                hosts.server_list.append(
                    address[0]) if address[0] not in hosts.server_list else hosts.server_list
                sock.sendto('ack'.encode(hosts.unicode), address)
                hosts.is_network_changed = True

            elif pickle.loads(data)[1] and hosts.leader != hosts.my_ip or pickle.loads(data)[3]:
                hosts.server_list = pickle.loads(data)[0]
                hosts.leader = pickle.loads(data)[1]
                hosts.client_list = pickle.loads(data)[4]
                print(f'[MULTICAST RECEIVER {hosts.my_ip}] All Data have been updated')

                sock.sendto('ack'.encode(hosts.unicode), address)
                hosts.is_network_changed = True

        except KeyboardInterrupt:
            print(f'[MULTICAST RECEIVER {hosts.my_ip}] Closing UDP Socket')