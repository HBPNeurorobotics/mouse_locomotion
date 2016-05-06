#!/usr/bin/python2

##
# Mouse Locomotion Simulation
#
# Human Brain Project SP10
#
# This project provides the user with a framework based on Blender allowing:
#  - Edition of a 3D model
#  - Edition of a physical controller model (torque-based or muscle-based)
#  - Edition of a brain controller model (oscillator-based or neural network-based)
#  - Simulation of the model
#  - Optimization of the parameters in distributed cloud simulations
#
# File created by: Gabriel Urbain <gabriel.urbain@ugent.be>. February 2016
# Modified by: Dimitri Rodarie
##

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
        logging.info("Start registry server on address: " + str(self.ipaddr) + ":" + str(REGISTRY_PORT))
        setup_logger(False, None)
        UDPRegistryServer.start(self)
