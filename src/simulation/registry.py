from simulation import Simulation
from rpyc.utils.registry import REGISTRY_PORT, DEFAULT_PRUNING_TIMEOUT, UDPRegistryServer
from rpyc.lib import setup_logger
import logging


class Registry(UDPRegistryServer, Simulation):
    """
    SimManager class provides a registry server to monitor the network state via UDP requests.
    Usage:
            # Create and start SimRegister thread
            r = SimRegister()
            r.start()
    """

    def __init__(self, opt):
        UDPRegistryServer.__init__(self, host='0.0.0.0', port=REGISTRY_PORT, pruning_timeout=DEFAULT_PRUNING_TIMEOUT)
        Simulation.__init__(self, opt)

    def start(self):
        """Start a registry server"""
        Simulation.start(self)
        logging.info("Start registry server on address: " + str(self.ipaddr) + ":" + str(REGISTRY_PORT))
        setup_logger(False, None)
        UDPRegistryServer.start(self)
