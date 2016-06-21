#!/usr/bin/python2

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

import copy
import logging
import time
from config import Config
from optimization import Optimization
from pyevolve import *


class Genetic(Optimization):
    """
    Genetic algorithm using pyevolve package. Perform evolution process on a list of parameters and retrieve the best
    solution after reaching convergence or a specific threshold
    Usage:
                # Instantiate Genetic
                genetic = Genetic(self.opt, self)

                # Run genetic algorithm
                genetic.start()
    """

    def __init__(self, opt, observable, num_max_generation=40, population_size=30, genome_size=None, mutation_rate=0.2,
                 cross_over_rate=0.65, genome_min=-2, genome_max=2.0, interactive_mode=False, stop_num_av=10,
                 stop_thresh=0.01):
        """
        Creation and initialization function for the genome and the genetic algorithm. It fixes the
        parameters to use in the algorithm
        :param opt: Dictionary containing simulation parameters
        :param observable: Observable instance to get update from
        :param num_max_generation: Int maximum number of generation
        :param population_size: Int population size
        :param genome_size: Int genome size
        :param mutation_rate: Float mutation rate
        :param cross_over_rate: Float cross over rate
        :param genome_min: Float min genome value
        :param genome_max: Float max genome value
        :param interactive_mode: Bool interactive mode
        :param stop_num_av: Int size of best solution list
        :param stop_thresh: Float threshold used to stop the genetic process
        """

        Optimization.__init__(self, opt, observable, num_max_generation, population_size, stop_thresh)

        # Algorithm parameters
        self.genome_size = Config(opt["config_name"]).get_conn_matrix_len() if genome_size is None else genome_size
        self.mutation_rate = mutation_rate
        self.cross_over_rate = cross_over_rate
        self.genome_min = genome_min
        self.genome_max = genome_max
        self.interactive_mode = interactive_mode
        self.initializator = Initializators.G1DListInitializatorReal
        self.mutator = Mutators.G1DListMutatorRealGaussian
        self.selector = Selectors.GRankSelector
        self.stop_num_av = stop_num_av

        # Create a genome instance and parametrize it
        self.genome = G1DList.G1DList(self.genome_size)
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
        self.ga.terminationCriteria.set(self.conv_fct)
        self.ga.setEvaluator(self.eval_fct)
        self.ga.setMinimax(Consts.minimaxType["maximize"])

        self.results = []
        self.configs = []

    def eval_fct(self, population):
        """
        Evaluation function of the genetic algorithm. For each population, it computes the
        score of every genomes and directly write it
        :param population: List of specimen to evaluate
        :return: Float score for the population
        """

        super_score = Optimization.eval_fct(self, population)

        if super_score is not None:
            return super_score
        scores = []

        # Create a config for the genome
        sim_list = []
        gen_list = []
        for ind in population.internalPop:
            self.opt["genome"] = ind.getInternalList()
            gen_list.append(ind.getInternalList())
            sim_list.append(copy.copy(self.opt))

        self.observable.simulate(sim_list)

        # Wait for simulation results
        while len(self.res_list) < len(sim_list) and not self.interruption:
            time.sleep(0.1)

        for res in self.res_list:
            scores.append(res["score"] if "score" in res else 0.)

        logging.info("Population gen " + str(self.ga.getCurrentGeneration() + 1) + " scores: " + str(scores))
        if len(scores) > 0:
            logging.info("Population gen " + str(self.ga.getCurrentGeneration() + 1) + " mean score: " + str(
                sum(scores) / len(scores)))
        # self.ga.printStats()

        # Update the score of each specimen
        i = 0
        for ind in population.internalPop:
            ind.setRawScore(scores[i] if i < len(scores) else 0.)
            i += 1

        # Return the population score result
        self.results.append(scores)
        self.configs.append(gen_list)
        return sum(scores)

    def conv_fct(self, ga):
        """
        Convergence function of the genetic algorithm. It is called at each iteration step
        :param ga: GSimpleGA instance to test
        :return: Boolean depending on a convergence criteria
        """

        if Optimization.conv_fct(self, ga):
            return True

        # Get the best specimens
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

    def start(self, **kwargs):
        """
        Start the genetic process
        :param kwargs: Dictionary parameter to pass for the simulation
        """

        self.best_solutions_list.append(
            self.ga.evolve(freq_stats=kwargs["freq_stats"] if "freq_stats" in kwargs.keys() else 10).getInternalList())
        self.notify()
        if self.to_save:
            self.save()

    def notify(self, notification=None):
        """
        Notify observers with the current state of the optimization
        :param notification: Dictionary that contains notification to add to
        the default notification
        """

        # Default notification
        kwargs = {
            "res": self.results,
            "configs": self.configs,
            "current_gen": self.ga.getCurrentGeneration()
        }

        # Specific notification
        if notification is not None:
            kwargs.update(notification)
        Optimization.notify(self, kwargs)
