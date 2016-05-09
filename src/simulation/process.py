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
import time

from simulation import Simulation
from optimization import Genetic
import sys

if sys.version_info[:2] < (3, 4):
    import manager as manager
else:
    from simulation import manager


class Process(Simulation):
    def __init__(self, opt):
        Simulation.__init__(self, opt)

    def start(self):
        if "sim_type" not in self.opt:
            manager.run_sim(self.opt)
        elif self.opt["sim_type"] == "BRAIN":
            self.brain_opti_sim()
        elif self.opt["sim_type"] == "MUSCLE":
            self.brain_opti_sim()
        else:
            manager.run_sim(self.opt)

    def brain_opti_sim(self):
        """Run an iterative simulation to optimize the muscles parameters"""
        # Create genetic algorithm
        genetic = Genetic(self.opt)

        # Run genetic algorithm until convergence or max iteration reached
        genetic.ga.evolve(freq_stats=10)

        # Stop and display results
        logging.info("Simulation Finished!")
        time.sleep(1)
        logging.info(genetic.ga.bestIndividual())

    def muscle_opti_sim(self):
        """Run an iterative simulation to optimize the muscles parameters"""

        logging.error("This simulation is not implemented yet! Exiting...")
