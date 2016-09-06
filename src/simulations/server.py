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
import rpyc

from simulations import Simulation
import logging
import sys
from rpyc.utils.server import ThreadPoolServer

if sys.version_info[:2] < (3, 4):
    from service import SimService
else:
    from simulations import SimService


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

        Simulation.__init__(self, opt)
        self.max_threads = 0
        self.test()

    def start(self):
        """Start a service server"""

        if self.max_threads >= 1:
            try:
                t = ThreadPoolServer(SimService, auto_register=True, protocol_config=rpyc.core.protocol.DEFAULT_CONFIG,
                                     nbThreads=int(self.max_threads))
                logging.info(
                    "Start service server on address: " + str(self.ipaddr) + ":" + str(t.port) + " with PID " + str(
                        self.pid))
                t.start()
            except KeyboardInterrupt:
                t.stop()
                logging.warning("SINGINT caught from user keyboard interrupt")
                sys.exit(1)
        else:
            logging.warning("Server capacities does not allow simulations.")

    def test(self):
        rsp_ = SimService.test_simulators(self.opt)
        cpu_capacity = (self.opt['cpu_use'] - rsp_["common"]["CPU"]) / \
                       (rsp_[self.opt['simulator']]["CPU"] - rsp_["common"]["CPU"])

        memory_capacity = (self.opt['memory_use'] - rsp_["common"]["memory"]) / \
                          (rsp_[self.opt['simulator']]["memory"] - rsp_["common"]["memory"])
        nb_thread = math.floor(min(cpu_capacity, memory_capacity))

        if nb_thread > 0:  # Change the status of the server on the cloud
            self.max_threads = nb_thread
        logging.info("The server " + str(self.ipaddr) + " is now available for a maximum of " +
                     str(nb_thread) + " simulation(s).")
