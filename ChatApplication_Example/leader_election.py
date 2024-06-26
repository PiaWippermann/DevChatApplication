# import of required modules
import socket
import hosts


def form_ring(members):
    """ Implementation of the function to form the ring.

    Given the IP addresses of the members of the ring this list is sorted and returned.
    """
    sorted_binary_ring = sorted([socket.inet_aton(member)
                                for member in members])
    sorted_ip_ring = [socket.inet_ntoa(node) for node in sorted_binary_ring]
    return sorted_ip_ring


def get_neighbour(ring, current_node_ip, direction='left'):
    """ Implementation of the get neighbour function.

    The sorted list given in 'ring' is used to get the neightbour of the given participant.
    The direction can also be passed in this function.
    """
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
    """ Function that can be called to start the leader election algorithm.

    Given the server list the ring is formed and the neighbour of the leader server is returned.
    """
    # form the ring with given servers (members of the ring)
    ring = form_ring(server_list)
    # given the ring and the leader server the right neighbour is returned
    neighbour = get_neighbour(ring, leader_server, 'right')
    return neighbour if neighbour != hosts.my_ip else None
