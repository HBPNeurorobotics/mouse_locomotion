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

import logging

from rpyc.lib import setup_logger
from rpyc.utils.registry import REGISTRY_PORT, DEFAULT_PRUNING_TIMEOUT, UDPRegistryServer, UDPRegistryClient

from .simulation import Simulation


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

        Simulation.__init__(self, opt)
        self.port = REGISTRY_PORT
        UDPRegistryServer.__init__(self, host=self.ipaddr, port=self.port, pruning_timeout=DEFAULT_PRUNING_TIMEOUT)

    def start(self):
        """Start a registry server"""

        Simulation.start(self)
        setup_logger(False, None)
        UDPRegistryServer.start(self)
        self.stop()

    @staticmethod
    def test_register(ip_register=None):
        """
        Test if there is a register connected on the network
        :param ip_register: String ip of the register
        :return: String ip of a register found on the network
        :raise: AttributeError if no register was found
        """

        logging.info("Test for registry presence on the network.")
        ip = Simulation.get_ip_address() if ip_register is None else ip_register
        if not Registry.__ping_register(ip) and ip != "0.0.0.0":
            logging.warning("No registry find on the defined IP. Testing on localhost")
            if Registry.__ping_register("0.0.0.0"):
                ip = "0.0.0.0"
            else:
                raise AttributeError("No register found on the network. Check your configuration. Abort.")
        logging.info("Registry test finished: A register was found on " +
                     (ip if ip != "0.0.0.0" else "localhost") + "\n")
        return ip

    @staticmethod
    def __ping_register(ip_register):
        """
        Try to register to a registry on ip_register:port
        :param ip_register: String ip of the register
        :return: Boolean True if the register process worked.
        """

        register = UDPRegistryClient(ip=ip_register, port=REGISTRY_PORT)
        did_register = register.register("Test", 0, interface="0.0.0.0")
        # If registration did not worked out, retry to register with localhost.
        if did_register:
            register.unregister(0)
        return did_register
