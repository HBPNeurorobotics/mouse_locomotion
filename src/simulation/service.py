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
import sys

import psutil
from rpyc import Service

if sys.version_info[:2] < (3, 4):
    import common
else:
    from simulation import common


class SimService(Service):
    ALIASES = common.ALIASES

    def exposed_simulation(self, opt_):  # this is an exposed method
        return common.launch_simulator(opt_)

    def exposed_test(self, opt_):
        cpu_percent = sum(psutil.cpu_percent(interval=0.5, percpu=True)) / float(psutil.cpu_count())
        memory_percent = psutil.virtual_memory().percent
        res = {"common": {"CPU": cpu_percent, "memory": memory_percent}}
        logging.info("Test Server " + type(self).__name__ +
                     ": \nCPU = " + str(cpu_percent) +
                     "\nMemory = " + str(memory_percent))
        if "simulator" in opt_:
            res[opt_["simulator"]] = common.test_simulator(opt_)
        return res
