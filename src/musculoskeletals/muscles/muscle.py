# coding=utf-8
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

import logging
from mathutils import Vector as vec


class Muscle:
    """
    Abstract Muscle class used to control simulated models
    """

    def __init__(self, params_, simulator):
        """
        Class initialization
        :param params_: Dictionary containing parameter for the muscle
        :param simulator: SimulatorUtils class to access utility functions
        """

        self.n_iter = 0
        self.params = params_
        self.simulator = simulator
        self.name = self.params["name"]
        self.active = True

        self.logger = logging.getLogger(params_["logger"])

        # Check if object exists
        self.obj1 = self.simulator.get_object(self.params["obj_1"])
        if self.obj1 is None:
            self.logger.error("Muscle " + self.name + " deactivated: first extremity object doesn't exit." +
                              " Check your configuration file!")
            self.active = False

        self.obj2 = self.simulator.get_object(self.params["obj_2"])
        if self.obj2 is None:
            self.logger.error("Muscle " + self.name + " deactivated: second extremity object doesn't exit." +
                              " Check your configuration file!")
            self.active = False

        # Points of application in local coordinates
        if self.params["anch_1"] is None:
            self.logger.error("You have not defined the first application point of muscle " + self.name +
                              "! Center is taken by default. This may results in erroneous simulation")
            self.params["anch_1"] = [0.0, 0.0, 0.0]
        if self.params["anch_2"] is None:
            self.logger.error("You have not defined the second application point of muscle " + self.name +
                              "! Center is taken by default. This may results in erroneous simulation")
            self.params["anch_2"] = [0.0, 0.0, 0.0]
        self.app_point_1 = vec((self.params["anch_1"]))
        self.app_point_2 = vec((self.params["anch_2"]))

        self.app_point_1_world = None
        self.app_point_2_world = None
        self.length = 0.
        self.velocity_1 = 0.
        self.velocity_2 = 0.
        self.force = vec((0, 0, 0))
        self.ctrl_sig = None

        if self.active:
            self.update_position()
            self.update_velocity()

    def get_power(self):
        """
        Return the power developed by the muscle on the two extremity objects
        :return: Float power consumed by the muscle
        """

        return 0.

    def draw_muscle(self, color_=[256, 0, 0]):
        """
        Draw a line to represent the muscle in the blender simulation
        :param color_: Color of the muscle inside the simulator
        """

        self.simulator.draw_line(self.app_point_1_world, self.app_point_2_world, color_)

    def update_position(self):
        """Update the positions of a muscle and its length"""

        self.app_point_1_world = self.simulator.update_position(self.obj1, self.app_point_1)
        self.app_point_2_world = self.simulator.update_position(self.obj2, self.app_point_2)
        self.length = self.app_point_2_world - self.app_point_1_world

    def update_velocity(self):
        """Update the velocity of the attached points of the muscle"""

        self.velocity_1 = self.simulator.get_velocity(self.obj1, self.app_point_1)
        self.velocity_2 = self.simulator.get_velocity(self.obj2, self.app_point_2)

    def update(self, **kwargs):
        """
        Update the muscle forces given geometry and control signal
        :param kwargs: Dictionary containing muscle updates
        """

        self.n_iter += 1
        self.update_position()
        self.update_velocity()

        if "ctrl_sig" in kwargs:
            self.ctrl_sig = kwargs["ctrl_sig"]
        else:
            self.ctrl_sig = None

        self.draw_muscle()
        return self.force
