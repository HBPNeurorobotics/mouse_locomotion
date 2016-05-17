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
from observers import Observer


class Optimization(Observer):
    def __init__(self, opt, observable, population_size, stop_thresh, max_iteration):
        self.opt = opt
        self.observable = observable
        self.observable.add_observer(self)
        self.population_size = population_size
        self.best_solutions_list = []
        self.stop_thresh = stop_thresh
        self.max_iteration = max_iteration
        self.res_list = []

    def __eval_fct(self, specimen):
        self.res_list = []

    def __conv_fct(self, algorithm):
        pass

    def update(self, **kwargs):
        if "res" in kwargs.keys():
            if type(kwargs["res"]) == dict:
                self.res_list.append(kwargs["res"].copy())
            else:
                self.res_list.append(kwargs["res"])
        else:
            self.res_list.append("Wrong format for result")
