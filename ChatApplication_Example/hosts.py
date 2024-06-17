import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(("8.8.8.8", 80))
my_ip = socket.gethostbyname(socket.gethostname())

buffer_size = 4096
unicode = 'utf-8'
multicast_address = '224.0.0.0'
leader = ''
neighbour = ''

server_list = []
client_list = []

is_network_changed = False
crashed_leader = ''
crashed_replica = ''
