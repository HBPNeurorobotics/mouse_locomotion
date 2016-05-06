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
from rpyc import Service
from rpyc.utils.registry import REGISTRY_PORT
from rpyc.utils.server import ThreadedServer


class SimService(Service, Simulation):
    """
    SimService class provides a services server to listen to external requests and start a Simulator
    simulation remotely and asynchronously.
    Usage:
            # Create and start SimService thread
            s = ThreadedServer(SimService, port=18861, auto_register=True)
            s.start()
    """

    ALIASES = ["BLENDERSIM", "BLENDER", "BLENDERPLAYER"]

    def __init__(self, opt):
        Simulation.__init__(self, opt)

    def start(self):
        """Start a service server"""
        logging.info("Start service server on address: " + str(self.ipaddr) + ":" + str(REGISTRY_PORT))
        try:
            t = ThreadedServer(SimService, port=18861, auto_register=True)
            t.start()
        except KeyboardInterrupt:
            t.stop()
            logging.warning("SINGINT caught from user keyboard interrupt")
            sys.exit(1)

    def on_connect(self):
        self.a = 4
        pass

    def on_disconnect(self):
        pass

    def exposed_simulation(self, opt_):  # this is an exposed method

        # Perform simulation
        logging.info("Processing simulation request")
        s = Simulation(opt_)
        s.start()
        logging.info("Simulation request processed")

        return s.get_results()
