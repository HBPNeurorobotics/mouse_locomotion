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
import os
import subprocess

from result import Result

import pickle


class Simulator:
    def __init__(self, opt):
        self.opt = opt
        self.args = []
        self.dirname = self.opt["root_dir"] + "/save"
        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)

    def launch_simulation(self):
        # Start batch process and quit
        logging.debug("Subprocess call: " + str(self.args))
        subprocess.call(self.args)
        logging.debug("Subprocess end")

    def get_results(self):
        """This function reads the file saved in Blender at the end of the simulation to retrieve results"""

        # Retrieve filename
        results = ""
        if "save_path" not in self.opt:
            results = "Simulator.get_results() : Nothing to show"
            logging.warning(results)
        elif os.path.isfile(self.opt["save_path"]):
            res = Result()
            results = res.get_results(self.opt["save_path"])
        else:
            results = "Simulator.get_results() : Can't open the file " + self.opt[
                "save_path"] + " -> The file doesn't exist."
            logging.error(results)

        return results
