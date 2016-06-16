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

import datetime
import logging
import time
import sys
from optimization import Genetic, GeneticMetaOptimization
from result import Result
from utils import PickleUtils

if sys.version_info[:2] < (3, 4):
    from manager import Manager
    import common
else:
    from simulation import Manager, common


class Process(Manager):
    def __init__(self, opt):
        Manager.__init__(self, opt)
        self.sim_type = opt["sim_type"] if "sim_type" in opt else None
        self.save = opt["save"] if "save" in opt else True
        self.save_directory = self.opt["root_dir"] + "/save/"

    def start(self):
        if self.sim_type is None:
            self.run_sim(self.opt)
        elif self.sim_type == "CM":
            self.connection_matrix_opti_sim()
        elif self.sim_type == "META_GA":
            self.meta_ga_sim()
        else:
            self.run_sim(self.opt)
        PickleUtils.del_all_files(self.save_directory, "qsm", logging)

    def connection_matrix_opti_sim(self):
        """Run an iterative simulation to optimize the connection matrix parameters"""

        # Create genetic algorithm
        genetic = Genetic(self.opt, self)

        # Run genetic algorithm until convergence or max iteration reached
        genetic.ga.evolve(freq_stats=2)

        # Stop and display results
        logging.info("Simulation Finished!")
        logging.info(genetic.ga.bestIndividual())

        # Save best individu parameters
        if self.save:
            PickleUtils.save(
                self.save_directory + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".gabi",
                genetic.ga.bestIndividual().getInternalList())

    def meta_ga_sim(self):
        """Run an meta simulation to benchmark genetic algorithm parameters"""

        # Create meta optimization
        mga = GeneticMetaOptimization(opt=self.opt, obs=self)

        # Run cross-over benchmark
        mga.co_bench(step_=0.1)

        # Save, display and plot results
        PickleUtils.save(self.save_directory + "default.mor", mga.result)
        mga.display()
        mga.plot(self.save_directory + "default.pdf")
        PickleUtils.del_all_files(self.save_directory, "qsm", logging)

    def run_sim(self, sim_list):
        """Run a simple on shot simulation"""

        if "local" in sim_list and sim_list["local"]:
            res_list = [common.launch_simulator(sim_list)]
        elif "load_file" in sim_list and sim_list["load_file"]:
            res = Result()
            sim_list["genome"] = res.get_results(sim_list["load_file"])
            res_list = [common.launch_simulator(sim_list)]

        else:
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
        if type(res_list) == list:
            for i in res_list:
                rs_ls += str(i) + "\n"
        else:
            rs_ls = "No results to show."
        logging.info("Simulation Finished!")
