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
import sys
from optimization import Genetic

if sys.version_info[:2] < (3, 4):
    from manager import Manager
else:
    from simulation import Manager


class Process(Manager):
    def __init__(self, opt):
        Manager.__init__(self, opt)

    def start(self):
        if "sim_type" not in self.opt:
            self.run_sim(self.opt)
        elif self.opt["sim_type"] == "BRAIN":
            self.brain_opti_sim()
        elif self.opt["sim_type"] == "MUSCLE":
            self.brain_opti_sim()
        else:
            self.run_sim(self.opt)

    def brain_opti_sim(self):
        """Run an iterative simulation to optimize the muscles parameters"""
        # Create genetic algorithm
        genetic = Genetic(self.opt, self)

        # Run genetic algorithm until convergence or max iteration reached
        genetic.ga.evolve(freq_stats=10)

        # Stop and display results
        logging.info("Simulation Finished!")
        time.sleep(1)
        logging.info(genetic.ga.bestIndividual())

    def muscle_opti_sim(self):
        """Run an iterative simulation to optimize the muscles parameters"""

        logging.error("This simulation is not implemented yet! Exiting...")

    def run_sim(self, sim_list):
        """Run a simple on shot simulation"""

        # Start manager
        Manager.start(self)
        # Simulate
        if type(sim_list) != list:
            sim_list = [sim_list]
        res_list = self.simulate(sim_list)

        # Stop and display results
        self.stop()
        time.sleep(1)
        rs_ls = ""
        for i in res_list:
            rs_ls += str(i) + "\n"
        logging.info("Results:\n" + str(rs_ls))
        logging.info("Simulation Finished!")
