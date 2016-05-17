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
import logging
import sys
from rpyc.utils.server import ThreadedServer

if sys.version_info[:2] < (3, 4):
    from service import SimService
else:
    from simulation import SimService


class SimServer(Simulation):
    """
    SimService class provides a services server to listen to external requests and start a Simulator
    simulation remotely and asynchronously.
    Usage:
            # Create and start SimService thread
            s = ThreadedServer(SimService, auto_register=True)
            s.start()
    """

    def __init__(self, opt):
        Simulation.__init__(self, opt)

    def start(self):
        """Start a service server"""
        try:
            t = ThreadedServer(SimService, auto_register=True)
            logging.info("Start service server on address: " + str(self.ipaddr) + ":" + str(t.port))
            t.start()
        except KeyboardInterrupt:
            t.stop()
            logging.warning("SINGINT caught from user keyboard interrupt")
            sys.exit(1)
