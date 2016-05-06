from simulation import Simulation
from optimization import Genetic
from simulation import manager
import logging
import time


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
