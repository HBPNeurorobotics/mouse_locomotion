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

    def get_results(self):
        """This function reads the file saved in Blender at the end of the simulation to retrieve results"""

        # Retrieve filename
        if "save_path" not in self.opt:
            results = "WARNING Simulator.get_results() : Nothing to show"
        elif os.path.isfile(self.opt["save_path"]):
            try:
                f = open(self.opt["save_path"], 'rb')
                results = pickle.load(f)
                f.close()
            except Exception as e:
                results = "Can't load save file : " + str(e)
                logging.error(results)
        else:
            results = "ERROR Simulator.get_results() : Can't open the file " + self.opt[
                "save_path"] + ".\nThe file doesn't exist."
        return results
