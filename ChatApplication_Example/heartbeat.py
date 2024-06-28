# import of required modules
import socket

# import of custom modules
from time import sleep
import hosts
import leader_election

# init the server port
server_port = 10001


def start_heartbeat():
    """ Implementation of the heart beat function to ensure fault tolerance.

    Leader server periodically sends a message to all other servers to show it is available.
    """
    while True:
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc.settimeout(0.5)

        # start the leader election imported from the leader_election module
        hosts.neighbour = leader_election.start_leader_elec(
            hosts.server_list, hosts.my_ip)
        host_address = (hosts.neighbour, server_port)
        print(f'Heartbeat: Server List {hosts.server_list}')



        if hosts.neighbour:
            sleep(3)

            try:
                soc.connect(host_address)
                print(f'Heartbeat: Neighbour {hosts.neighbour} response')

            except:
                hosts.server_list.remove(hosts.neighbour)

                if hosts.leader == hosts.neighbour:
                    print(
                        f'Heartbeat: Server Leader {hosts.neighbour} crashed')
                    hosts.crashed_leader = True

                    hosts.leader = hosts.my_ip
                    hosts.is_network_changed = True

                else:
                    print(
                        f'Heartbeat: Server Replica {hosts.neighbour} crashed')
                    hosts.crashed_replica = 'True'

            finally:
                soc.close()
