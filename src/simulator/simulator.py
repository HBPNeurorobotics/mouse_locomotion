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
        self.filename = ""
        self.update_filename()

    def update_filename(self):
        self.filename = "sim_" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".qsm"
        self.filename = self.dirname + "/" + self.filename

    def launch_simulation(self):
        # Start batch process and quit
        logging.debug("Subprocess call: " + str(self.args))
        subprocess.call(self.args)
        logging.debug("Subprocess end")

    def get_results(self):
        """This function reads the file saved in Blender at the end of the simulation to retrieve results"""
        # Retrieve filename
        res = Result()
        results = res.get_results(self.filename)
        return results
