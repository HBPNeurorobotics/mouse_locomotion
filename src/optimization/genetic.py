from pyevolve import *
import logging
from optimization import Optimization
import simulation.manager as manager


class Genetic(Optimization):
    def __init__(self, opt, genome_size=10, population_size=20, num_max_generation=50, mutation_rate=0.2,
                 cross_over_rate=0.9, genome_min=0, genome_max=1.0, interactive_mode=False, stop_num_av=10,
                 stop_thresh=0.01):
        """Creation and initialization function for the genome and the genetic algorithm. It fixes the
        parameters to use in the algorithm"""
        Optimization.__init__(self, opt, population_size, stop_thresh, num_max_generation)
        # Algo parameters
        self.genome_size = genome_size
        self.mutation_rate = mutation_rate
        self.cross_over_rate = cross_over_rate
        self.genome_min = genome_min
        self.genome_max = genome_max
        self.interactive_mode = interactive_mode
        self.initializator = Initializators.G1DListInitializatorReal
        self.mutator = Mutators.G1DListMutatorRealGaussian
        self.selector = Selectors.GTournamentSelector
        self.stop_num_av = stop_num_av

        # Create a genome instance and parametrize it
        self.genome = G1DList.G1DList(self.genome_size)
        self.genome.evaluator.set(self.__eval_fct)
        self.genome.initializator.set(self.initializator)
        self.genome.mutator.set(self.mutator)
        self.genome.setParams(rangemin=self.genome_min, rangemax=self.genome_max)

        # Create a Genetic Algorithm (ga) instance and parametrize it
        self.ga = GSimpleGA.GSimpleGA(self.genome)
        self.ga.selector.set(self.selector)
        self.ga.setGenerations(self.max_iteration)
        self.ga.setMutationRate(self.mutation_rate)
        self.ga.setPopulationSize(self.population_size)
        self.ga.setCrossoverRate(self.cross_over_rate)
        self.ga.setInteractiveMode(self.interactive_mode)
        self.ga.terminationCriteria.set(self.__conv_fct)

    def __eval_fct(self, genome):
        """Evaluation function of the genetic algorithm. For each set of genome, it compute a
        score and returns it"""

        score = 0.0
        # Create a config for the genome
        self.opt["genome"] = genome.getInternalList()
        logging.info(" ---------------- DEBUT SIM -----------")

        # Simulate
        res_list = manager.run_sim(self.opt)

        # In the result list, we look for the score
        score = 1
        logging.info(" ---------------- FIN SIM -----------")
        # Return the score result
        return score

    def __conv_fct(self, ga):
        """Convergence function of the genetic algorithm. It is called at each iteration step and
        return True of False depending on a convergence criteria"""

        # Get best individus
        pop = ga.getPopulation()
        bi = pop.bestFitness()
        self.best_solutions_list.append(bi.getFitnessScore())

        # Return the convergence
        if len(self.best_solutions_list) > self.stop_num_av:
            av = sum(self.best_solutions_list[-self.stop_num_av:]) / self.stop_num_av
            # print("av: " + str(av)  + " curr: " + str(self.bf_lis[-1]) + ' abs: ' + str(abs(self.bf_lis[-1] - av)))
            if abs(self.best_solutions_list[-1] - av) < self.stop_thresh:
                logging.info("Criterion reached. Best element : " + str(bi.getInternalList()))
                return True

        return False
