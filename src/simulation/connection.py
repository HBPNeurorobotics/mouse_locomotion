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
import logging

from simulation import Simulation
from rpyc import Service


class SimConnection(Service):
    ALIASES = ["BLENDERSIM", "BLENDER", "BLENDERPLAYER"]

    def exposed_simulation(self, opt_):  # this is an exposed method

        # Perform simulation
        logging.info("Processing simulation request")
        s = Simulation(opt_)
        s.start()
        logging.info("Simulation request processed")

        return s.get_results()
