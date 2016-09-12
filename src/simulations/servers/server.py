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
# February 2016
##

import math
import threading
import socket

import rpyc

from simulations import PROTOCOL_CONFIG
from simulations.simulation import Simulation
import logging
import sys
from rpyc.utils.server import Server

from utils import PickleUtils
from .service import SimService


class SimServer(Simulation):
    """
    SimServer class provides a services server to listen to external requests and start a Simulator
    simulation remotely and asynchronously.
    Usage:
            # Create and start SimServer thread
            s = SimServer(opt)
            s.start()
    """

    def __init__(self, opt):
        """
        Class initialization
        :param opt: Dictionary containing simulation parameters
        """

        logging.info("Start a server instance.")
        Simulation.__init__(self, opt)
        self.simulator = self.opt["simulator"]
        self.max_threads = 0
        self.test()

    def start(self):
        """Start a service server"""

        if self.max_threads >= 1:
            try:
                t = ServiceServer(int(self.max_threads))
                logging.info(
                    "Start Service Server on address: " + str(self.ipaddr) + ":" + str(t.port) + " with PID " + str(
                        self.pid))
                t.start()
            except KeyboardInterrupt:
                logging.warning("SINGINT caught from user keyboard interrupt")
        self.stop()

    def test(self):
        """Test the server capacities to know how many parallel simulations it can run"""

        logging.info("Test the server capacities.")
        rsp_ = SimService.test_simulators(self.opt)
        if "interruption" not in rsp_[self.simulator]:
            cpu_capacity = (self.opt['cpu_use'] - rsp_["common"]["CPU"]) / \
                           (rsp_[self.simulator]["CPU"] - rsp_["common"]["CPU"])

            memory_capacity = (self.opt['memory_use'] - rsp_["common"]["memory"]) / \
                              (rsp_[self.simulator]["memory"] - rsp_["common"]["memory"])
            self.max_threads = math.floor(min(cpu_capacity, memory_capacity))
            logging.info("Server test finished")
            if self.max_threads >= 1:  # Change the status of the server on the cloud
                logging.info("The server can run a maximum of " +
                             str(self.max_threads) + " parallel simulation(s) on " + self.simulator)
            else:
                logging.warning("Server capacities does not allow simulations.")
        else:
            logging.info("User interruption during simulation test.")
            self.max_threads = 0.

    def stop(self):
        """Close the Simulation Server and delete file results"""

        Simulation.stop(self)
        # Delete all the simulation files that might stayed after simulation
        PickleUtils.del_all_files(self.save_directory, "qsm")
        logging.info("The Server is now closed.")


class ServiceServer(Server):
    """
    ServiceServer class is a rpyc server implementation to control the number of threads the server will run in parallel
    and to get errors during simulation
    """

    def __init__(self, max_threads):
        """
        Class initialization
        :param max_threads: Integer for the maximum number of thread that the server can run in parallel
        """
        Server.__init__(self, SimService, auto_register=True, protocol_config=PROTOCOL_CONFIG)
        self.workers = 0
        self.max_threads = max_threads
        self.lock = threading.Lock()

    def _accept_method(self, sock):
        """
        Add a new working thread for a simulation
        :param sock: Socket of the connection with the client
        """
        t = threading.Thread(target=self._serve_client, args=(sock, self))
        t.setDaemon(True)
        self.lock.acquire()
        self.workers += 1
        self.lock.release()
        t.start()

    def _serve_client(self, sock, parent):
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
        self.logger.info("server started on [%s]:%s", self.host, self.port)
        self.active = True
        if self.auto_register:
            t = threading.Thread(target=self._bg_register)
            t.setDaemon(True)
            t.start()
        try:
            while self.active:
                self.accept()
        except EOFError:
            self.logger.info("Server has terminated")
            self.close()
        except KeyboardInterrupt as e:
            self.logger.info("Server has terminated")
            self.close()
            raise e
