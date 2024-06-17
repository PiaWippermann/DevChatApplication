import socket
import hosts


def form_ring(members):
    """Sorts and forms a ring of IP addresses from a list of members."""
    sorted_binary_ring = sorted([socket.inet_aton(member)
                                for member in members])
    sorted_ip_ring = [socket.inet_ntoa(node) for node in sorted_binary_ring]
    return sorted_ip_ring


def get_neighbour(ring, current_node_ip, direction='left'):
    """Finds the neighboring node in a ring from the current node's perspective."""
    current_node_index = ring.index(
        current_node_ip) if current_node_ip in ring else -1
    if current_node_index != -1:
        if direction == 'left':
            if current_node_index + 1 == len(ring):
                return ring[0]
            else:
                return ring[current_node_index + 1]
        else:
            if current_node_index == 0:
                return ring[-1]
            else:
                return ring[current_node_index - 1]
    else:
        return None


def start_leader_elec(server_list, leader_server):
    """Initiates leader election in a network ring."""
    ring = form_ring(server_list)
    neighbour = get_neighbour(ring, leader_server, 'right')
    return neighbour if neighbour != hosts.my_ip else None