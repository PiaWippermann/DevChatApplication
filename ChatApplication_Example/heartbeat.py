import socket
import sys

from time import sleep
import hosts
import leader_election

server_port = 10001


def start_heartbeat():
    """Implements a heartbeat mechanism to monitor server neighbors for health and handle crashes."""
    while True:
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc.settimeout(0.5)

        hosts.neighbour = leader_election.start_leader_elec(hosts.server_list, hosts.my_ip)
        host_address = (hosts.neighbour, server_port)

        if hosts.neighbour:
            sleep(3)

            try:
                soc.connect(host_address)
                print(f'[HEARTBEAT] Neighbour {hosts.neighbour} response')

            except:
                hosts.server_list.remove(hosts.neighbour)

                if hosts.leader == hosts.neighbour:
                    print(f'[HEARTBEAT] Server Leader {hosts.neighbour} crashed')
                    hosts.crashed_leader = True

                    hosts.leader = hosts.my_ip
                    hosts.is_network_changed = True

                else:
                    print(f'[HEARTBEAT] Server Replica {hosts.neighbour} crashed')
                    hosts.crashed_replica = 'True'

            finally:
                soc.close()
