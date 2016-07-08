##
# Mouse Locomotion Simulation
#
# Human Brain Project SP10
#
# This project provides the user with a framework based on 3D simulators allowing:
#  - Edition of a 3D model
#  - Edition of a physical controller model (torque-based or muscle-based)
#  - Edition of a brain controller model (oscillator-based or neural network-based)
#  - Simulation of the model
#  - Optimization and Meta-optimization of the parameters in distributed cloud simulations
#
# File created by: Gabriel Urbain <gabriel.urbain@ugent.be>
#                  Dimitri Rodarie <d.rodarie@gmail.com>
# February 2016
##

import logging
import sys
import datetime
from optimizations import Genetic, GeneticMetaOptimization
from utils import PickleUtils

if sys.version_info[:2] < (3, 4):
    from simulation import Simulation
    from manager import Manager
    import common
else:
    from simulations import Manager, common, Simulation


class Process(Simulation):
    """
    The Process class launch different type of simulation including :
    - Simple simulation
    - Genetic optimization on simulations (opt["sim_type"]="CM")
    - Meta-Genetic optimization on simulation (opt["sim_type"]="META_GA")
    Usage:
            # Create and start the simulation Process
            process = Process(opt)
            process.start()

            # Wait for the results and stop Process
            process.stop()
    """

    def __init__(self, opt):
        """
        Class initialization
        :param opt: Dictionary that contains simulation parameters
        """

        Simulation.__init__(self)
        self.opt = opt
        self.sim_type = opt["sim_type"] if "sim_type" in opt else None
        self.save = opt["save"] if "save" in opt else True
        self.save_directory = self.opt["root_dir"] + "/save/"
        self.manager = Manager(opt)
        self.res_list = []

    def start(self):
        """Launch the desired simulation(s) process"""

        # Start manager
        self.manager.start()
        self.res_list = []

        if self.sim_type is None:
            self.run_sim(self.opt)
        elif self.sim_type == "CM":
            self.connection_matrix_opti_sim()
        elif self.sim_type == "META_GA":
            self.meta_ga_sim()
        else:
            self.run_sim(self.opt)
        self.stop()

    def stop(self):
        """
        Stop the current simulations
        """

        # Stop and display results
        self.manager.stop()

        # Delete all the simulation files that might stayed after simulation
        PickleUtils.del_all_files(self.save_directory, "qsm")

    def connection_matrix_opti_sim(self):
        """Run an iterative simulation to optimize the connection matrix parameters"""

        # Create genetic algorithm
        genetic = Genetic(self.opt, self.manager)

        # Run genetic algorithm until convergence or max iteration reached
        genetic.start(**{"freq_stats": 2})

        # Stop and display results
        logging.info("Simulation Finished!")
        logging.info(genetic.ga.bestIndividual())

    def meta_ga_sim(self):
        """Run an meta simulation to benchmark genetic algorithm parameters"""

        # Create meta optimization
        mga = GeneticMetaOptimization(self.opt, self.manager)

        # Run cross-over benchmark
        mga.co_bench()

    def run_sim(self, sim_list):
        """
        Run a simple on shot simulation
        :param sim_list: List of parameter lists to launch simulations
        """

        if "local" in sim_list and sim_list["local"]:
            self.res_list.append(common.launch_simulator(sim_list))
        elif "load_file" in sim_list and sim_list["load_file"]:
            sim_list["genome"] = PickleUtils.load(sim_list["load_file"])
            self.res_list.append(common.launch_simulator(sim_list))
        else:
            # Simulate
            if type(sim_list) != list:
                sim_list = [sim_list]
            self.res_list.append(self.manager.simulate(sim_list))

        # Save the results
        if self.save:
            PickleUtils.save(self.save_directory + "Simulation_" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M") +
                             ".sim", self.res_list)

    def display_results(self):
        """
        Display results retrieved so far.
        :return: String representing the results list
        """

        rs_ls = ""
        for i in self.res_list:
            rs_ls += str(i) + "\n"
        else:
            rs_ls = "No results to show."

        logging.info("Simulation Finished!")
        return rs_ls
