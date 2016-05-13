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

from simulator import Simulator


class Blender(Simulator):
    ALIASES = {"BLENDER": "blender", "BLENDERPLAYER": "blenderplayer"}

    def __init__(self, opt, type_="BLENDERPLAYER"):
        Simulator.__init__(self, opt)
        self.type = type_

    def launch_simulation(self):
        if self.type in self.ALIASES:
            self.args = [self.opt["simulator_path"] + self.ALIASES[self.type]]
            eval("self.start_" + self.ALIASES[self.type] + "()")
            # Start batch process and quit
            logging.debug("Subprocess call: " + str(self.args))
        else:
            self.create_pop()
        Simulator.launch_simulation(self)

    def start_blenderplayer(self):
        """Call blenderplayer via command line subprocess"""

        # Fetch blender game engine standalone path

        # Add arguments to command line
        self.args.extend([
            "-w", "1080", "600", "2000", "200",
            "-g", "show_framerate", "=", "1",
            "-g", "show_profile", "=", "1",
            "-g", "show_properties", "=", "1",
            "-g", "ignore_deprecation_warnings", "=", "0",
            "-d",
        ])

        self.update_filename()
        if self.opt["fullscreen"]:
            self.args.extend(["-f"])
        self.args.extend([self.opt["model"]])
        self.args.extend(["-"])
        params = {'config_name': self.opt["config_name"] + "()",
                  'logfile': str(self.opt["logfile"]),
                  'filename': self.filename}
        self.args.extend([str(params)])
        self.args.extend(["FROM_START.PY"])

    def start_blender(self):
        """Call blender via command line subprocess and start the game engine simulation"""

        # Add arguments to command line
        self.args.extend([self.opt["model"]])
        self.args.extend(["--python", "ge.py"])
        self.args.extend(["--start_player()"])

    def create_pop(self):
        """Call blender via command line subprocess and create a population out of a model"""
        self.args = [self.opt["simulator_path"] + "blender"]
        # Add arguments to command line
        self.args.extend(["-b"])
        self.args.extend([self.opt["model"]])
        self.args.extend(["--python", "model.py"])
        self.args.extend(["--create_pop()"])
