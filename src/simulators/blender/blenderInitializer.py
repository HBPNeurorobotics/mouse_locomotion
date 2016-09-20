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
import sys

import bge
from .blenderUtils import BlenderUtils

from ..initializer import Initializer


class BlenderInitializer(Initializer):
    """
    Class used by Blender to initialize the brain and the body that will be used during simulation
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

        Initializer.__init__(self, argv)
        owner["config"] = self.body.config
        owner["body"] = self.body

    def init_root(self):
        """Define the root directory for the program files relative to Blender"""

        self.root = os.path.dirname(os.path.dirname(bge.logic.expandPath("//"))).replace("\\", "/")
        self.src = self.root + "/src"
        sys.path.append(self.src)

    def setup_utility_class(self, config):
        """Set the utility class to get information from Blender"""

        self.utility_class = BlenderUtils(self.scene)


# Call from Blender
global owner
owner = dict()
BlenderInitializer()
