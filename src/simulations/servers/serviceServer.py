##
# Mouse Locomotion Simulation
#
# Human Brain Project SP10
#
# This project provides the user with a framework based on 3D simulators allowing:
#  - Edition of a 3D model
#  - Edition of a physical controller model (torque-based or muscle-based)
#  - Edition of a brain controller model (oscillator-based or neural network-based)
#  - Simulation of the model
#  - Optimization and Meta-optimization of the parameters in distributed cloud simulations
#
# File created by: Gabriel Urbain <gabriel.urbain@ugent.be>
#                  Dimitri Rodarie <d.rodarie@gmail.com>
# September 2016
##

import socket
import sys
import threading

import rpyc
from rpyc.utils.registry import UDPRegistryClient, REGISTRY_PORT
from rpyc.utils.server import Server

from simulations import PROTOCOL_CONFIG
from simulations import Registry


class ServiceServer(Server):
    """
    ServiceServer class is a rpyc server implementation to control the number of threads the server will run in parallel
    and to get errors during simulation
    """

    def __init__(self, service, max_threads, ip_register):
        """
        Class initialization
        :param service: Service to serve on client connection
        :param max_threads: Integer for the maximum number of thread that the server can run in parallel
        """

        self.ip_register = Registry.test_register(ip_register)
        Server.__init__(self, service, auto_register=True,
                        protocol_config=PROTOCOL_CONFIG,
                        registrar=UDPRegistryClient(ip=self.ip_register, port=REGISTRY_PORT))
        self.workers = 0
        self.max_threads = max_threads
        self.lock = threading.Lock()

    def _accept_method(self, sock):
        """
        Add a new working thread for a simulation
        :param sock: Socket of the connection with the client
        """
        t = threading.Thread(target=self._serve_clients, args=(sock, self))
        t.setDaemon(True)
        self.lock.acquire()
        self.workers += 1
        self.lock.release()
        t.start()

    def _serve_clients(self, sock, parent):
        """
        Serve the client request
        :param sock: Socket of the connection with the client
        :param parent: Thread to update the number of working thread after simulation
        """

        self._authenticate_and_serve_client(sock)
        parent.lock.acquire()
        parent.workers -= 1
        parent.lock.release()

    def accept(self):
        """Accepts incoming socket connections if the number of working threads is not too high"""

        if self.workers < self.max_threads:
            while self.active:
                try:
                    sock, addrinfo = self.listener.accept()
                except socket.timeout:
                    pass
                except socket.error:
                    ex = sys.exc_info()[1]
                    if rpyc.utils.server.get_exc_errno(ex) == rpyc.utils.server.errno.EINTR:
                        pass
                    else:
                        raise EOFError()
                else:
                    break

            if not self.active:
                return
            sock.setblocking(True)
            self.logger.info("accepted %s:%s", addrinfo[0], addrinfo[1])
            self.clients.add(sock)
            self._accept_method(sock)

    def start(self):
        """
        Starts the server. Use :meth:`close` to stop.
        :raise KeyboardInterrupt exception"""

        self.listener.listen(self.backlog)
        self.active = True
        if self.auto_register:
            t = threading.Thread(target=self._bg_register)
            t.setDaemon(True)
            t.start()
        try:
            while self.active:
                self.accept()
        except EOFError:
            self.close()
        except KeyboardInterrupt as e:
            self.close()
            raise e
