import socket

# Initialization of the socket to determine the own IP address
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    sock.connect(("8.8.8.8", 80))
    my_ip = sock.getsockname()[0]
finally:
    sock.close()

# Configuration variables
buffer_size = 4096
unicode = 'utf-8'
multicast_address = '224.0.0.0'

# Initialization of variables
leader = ''
neighbour = ''
server_list = []
client_list = []
is_network_changed = False
crashed_leader = ''
crashed_replica = ''
