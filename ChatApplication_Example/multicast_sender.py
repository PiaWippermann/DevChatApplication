import socket
import sys
import struct
import pickle

from time import sleep
import hosts


broadcast_port = 10000

server_port = 10001
multicast_address = (hosts.multicast_address, broadcast_port)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.settimeout(1)

ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)


def send_req_to_multicast():
    """Sends data to multicast receivers and waits for a response, synchronizing host variables."""
    sleep(1)

    message = pickle.dumps([hosts.server_list, hosts.leader, hosts.crashed_leader, hosts.crashed_replica,
                            str(hosts.client_list)])
    sock.sendto(message, multicast_address)
    print(f'\n[MULTICAST SENDER {hosts.my_ip}] Sending data to Multicast Receivers {multicast_address}')

    try:
        sock.recvfrom(hosts.buffer_size)

        if hosts.leader == hosts.my_ip:
            print(f'[MULTICAST SENDER {hosts.my_ip}] All Servers have been updated\n')
        return True

    except socket.timeout:
        print(f'[MULTICAST SENDER {hosts.my_ip}] No Multicast Receiver found')
        return False



def send_join_request():
    """Sends a chat room join request and determines the server leader."""

    print(f'\n[MULTICAST SENDER {hosts.my_ip}] Sending join chat request to Multicast Address {multicast_address}')
    message = pickle.dumps(['JOIN', '', '', ''])
    sock.sendto(message, multicast_address)

    # try to get Server Leader
    try:
        data, address = sock.recvfrom(hosts.buffer_size)
        hosts.leader = pickle.loads(data)[0]
        return True

    except socket.timeout:
        print(f'[MULTICAST SENDER {hosts.my_ip}] Multicast Receiver not detected -> Chat Server is offline.')
        return False


