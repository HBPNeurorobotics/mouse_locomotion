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
import sys
from rpyc import Service

if sys.version_info[:2] < (3, 4):
    import common
else:
    from simulation import common


class SimService(Service):
    ALIASES = common.ALIASES

    def exposed_simulation(self, opt_):  # this is an exposed method
        return common.launch_simulator(opt_)
