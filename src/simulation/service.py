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

from simulator import *
from rpyc import Service


class SimService(Service):
    ALIASES = ["BLENDERSIM", "BLENDER", "BLENDERPLAYER"]
    SIMULATORS = {"BLENDER": "Blender"}
    DEFAULT_SIMULATOR = "BLENDER"

    def exposed_simulation(self, opt_):  # this is an exposed method
        if type(opt_) == dict and "simulator" in opt_:
            simulator_ = opt_["simulator"]
            if simulator_ not in self.SIMULATORS:
                simulator_ = self.DEFAULT_SIMULATOR
        else:
            simulator_ = self.DEFAULT_SIMULATOR
        simulator_ = self.SIMULATORS[simulator_] + "(opt_)"

        # Perform simulation
        logging.info("Processing simulation request")
        simulator_ = eval(simulator_)
        simulator_.launch_simulation()
        logging.info("Simulation request processed")

        return simulator_.get_results()
