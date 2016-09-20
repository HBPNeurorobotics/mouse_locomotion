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

import bge

from ..updater import Updater


class BlenderUpdater(Updater):
    """
    Class used by Blender to update the brain and the body at each time step during simulation
    """

    def __init__(self):
        """Class initialization"""

        self.controller = bge.logic.getCurrentController()
        self.exit_actuator = self.controller.actuators['quit_game']
        self.keyboard = bge.logic.keyboard
        Updater.__init__(self, owner["config"], owner["body"])

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


updater = BlenderUpdater()
updater.update()
