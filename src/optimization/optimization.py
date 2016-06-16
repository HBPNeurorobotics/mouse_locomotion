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
# File created by: Gabriel Urbain <gabriel.urbain@ugent.be>
#                  Dimitri Rodarie <d.rodarie@gmail.com>
# April 2016
##

from observers import Observer


class Optimization(Observer):
    """
    Optimization abstract class provides tools and abstract functions that will be used in subclasses
    for optimization processes
    """

    def __init__(self, opt, observable, max_iteration, population_size=0, stop_thresh=None):
        """
        Class initialization
        :param opt: Dictionary containing simulation parameters
        :param observable: Observable instance to get update from
        :param max_iteration: Int maximum number of iteration
        :param population_size: Int population size
        :param stop_thresh: Float threshold used to stop the optimization process
        """

        Observer.__init__(self)
        self.opt = opt
        self.observable = observable
        self.interruption = False
        if self.observable:
            self.observable.add_observer(self)
        self.population_size = population_size
        self.best_solutions_list = []
        self.stop_thresh = stop_thresh
        self.max_iteration = max_iteration
        self.res_list = []

    def eval_fct(self, population):
        """
        Evaluation function used to test solution
        :param population: List of specimen to evaluate
        :return: Float population score
        """

        self.res_list = []
        if self.interruption:
            return 0.

    def conv_fct(self, algorithm):
        """
        Convergence function to test solutions evolution
        :param algorithm: Algorithm parameter
        :return: Boolean depending on a convergence criteria
        """

        if self.interruption:
            return True

    def update(self, **kwargs):
        """
        Retrieve results from the simulation and update parameters
        :param kwargs: Dictionary parameter used for update
        """

        if "res" in kwargs.keys():
            if type(kwargs["res"]) == dict:
                self.res_list.append(kwargs["res"].copy())
            else:
                self.res_list.append(kwargs["res"])
        elif "interruption" in kwargs.keys():
            if type(kwargs["interruption"]) == bool and kwargs["interruption"]:
                self.interruption = True

    def start(self, **kwargs):
        """
        Start the optimization process till it reach convergence or threshold
        :param kwargs: Dictionary parameter to pass for the simulation
        """
