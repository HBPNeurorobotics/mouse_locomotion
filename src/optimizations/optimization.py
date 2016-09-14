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
# April 2016
##
import datetime

from observers import Observer, Observable
from utils import PickleUtils


class Optimization(Observer, Observable):
    """
    Optimization abstract class provides tools and abstract functions that will be used in subclasses
    for optimization processes
    It gets notifications from the simulation thread and can notify its changes for further process
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
        Observable.__init__(self)
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
        self.sim_list = []

        # Saving parameters
        self.to_save = opt["save"] if "save" in opt else True
        self.save_directory = self.opt["root_dir"] + "/save/"
        self.extension = ".sim"
        # Saving content
        self.results = []
        self.configs = []
        self.current_gen = 0

    def update_population(self, population):
        """Update the current population to test"""
        self.current_gen += 1

    def update_scores(self, scores, population):
        """Update the current scores"""

        self.results.append(scores)

        return sum(scores)

    def evaluate(self, population):
        return self.res_list

    def eval_fct(self, population):
        """
        Evaluation function used to test solution
        :param population: List of specimen to evaluate
        :return: Float population score
        """

        self.res_list = []
        if self.interruption:
            return 0.
        self.update_population(population)
        self.observable.simulate(self.sim_list)
        scores = self.evaluate(population)
        return self.update_scores(scores, population)

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
            self.res_list = kwargs["res"].copy() if type(kwargs["res"]) == dict else kwargs["res"]
        elif "interruption" in kwargs.keys():
            if type(kwargs["interruption"]) == bool and kwargs["interruption"]:
                self.interruption = True

    def start(self, **kwargs):
        """
        Start the optimization process till it reach convergence or threshold
        :param kwargs: Dictionary parameter to pass for the simulation
        """

        pass

    def stop(self):
        """Stop the optimization and save the results"""

        self.notify()
        if self.to_save:
            self.save(filename=self.__class__.__name__, result={
                "res": self.results,
                "configs": self.configs,
                "current_generation": self.current_gen
            })

    def notify(self, notification=None):
        """
        Notify observers with the current state of the optimization
        :param notification: Dictionary that contains notification to add to
        the default notification
        """

        # Default notification
        kwargs = {
            "interruption": self.interruption,
            "res": self.results,
            "configs": self.configs,
            "current_gen": self.current_gen
        }

        # Specific notification
        if notification is not None:
            kwargs.update(notification)
        self.notify_observers(**kwargs)

    def save(self, filename="Optimization", result=None):
        """
        Save the current results into a file
        :param filename: String name begin for the file
        :param result: Content to save in the file
        """

        PickleUtils.write_file(
            self.save_directory + filename + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M") + self.extension,
            self.res_list if result is None else result)

    def save_best_sol(self):
        """Save the current best solutions into a file"""

        self.save(result=self.best_solutions_list)
