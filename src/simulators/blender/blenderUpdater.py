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
import os

import bge
import sys

from simulators.blender.blenderUtils import BlenderUtils
from simulators.updater import Updater


class BlenderUpdater(Updater):
    """
    Class used by Blender to update the brain and the body at each time step during simulation
    """

    def __init__(self):
        """Class initialization"""
        self.scene = bge.logic.getCurrentScene()
        # Set simulation parameters
        # bge.logic.setTimeScale(configuration.sim_speed)

        if sys.argv[len(sys.argv) - 1] == "FROM_START.PY":
            # Catch command-line config when started from another script
            argv = sys.argv
            argv = eval(argv[argv.index("-") + 1])
        else:
            argv = {}

        self.controller = bge.logic.getCurrentController()
        self.exit_actuator = self.controller.actuators['quit_game']
        self.keyboard = bge.logic.keyboard
        Updater.__init__(self, argv)

    def init_root(self):
        """Define the root directory for the program files relative to Blender"""

        self.root = os.path.dirname(os.path.dirname(bge.logic.expandPath("//"))).replace("\\", "/")
        self.src = self.root + "/src"
        sys.path.append(self.src)

    def setup_utility_class(self):
        """Set the utility class to get information from Blender"""

        self.utility_class = BlenderUtils(self.scene)

    def exit_condition(self):
        """
        Test if the simulation exit_condition is True or if the simulation is over or if the model got a penalty
        or if the user pressed the SPACE bar.
        :return: Boolean result of the test
        """

        return Updater.exit_condition(self) or bge.logic.KX_INPUT_ACTIVE == self.keyboard.events[bge.events.SPACEKEY]

    def exit(self):
        """Exit the simulation and create a result file"""

        Updater.exit(self)
        self.controller.activate(self.exit_actuator)
