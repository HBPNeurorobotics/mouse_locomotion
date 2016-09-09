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

from simulation import Simulation
from rpyc.utils.registry import REGISTRY_PORT, DEFAULT_PRUNING_TIMEOUT, UDPRegistryServer
from rpyc.lib import setup_logger
import logging


class Registry(UDPRegistryServer, Simulation):
    """
    Registry class provides a registry server to monitor the network state via UDP requests.
    Usage:
            # Create and start Registry thread
            r = Registry(opt)
            r.start()
    """

    def __init__(self, opt):
        """
        Class initialization
        :param opt: Dictionary containing simulation parameters
        """

        UDPRegistryServer.__init__(self, host='0.0.0.0', port=REGISTRY_PORT, pruning_timeout=DEFAULT_PRUNING_TIMEOUT)
        Simulation.__init__(self, opt)

    def start(self):
        """Start a registry server"""

        logging.info("Start registry server on address: " + str(self.ipaddr) + ":" + str(REGISTRY_PORT) + " with PID " +
                     str(self.pid))
        setup_logger(False, None)
        UDPRegistryServer.start(self)
