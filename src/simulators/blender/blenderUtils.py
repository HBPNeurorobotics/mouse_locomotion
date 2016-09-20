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
# File created by: Gabriel Urbain <gabriel.urbain@ugent.be>
#                  Dimitri Rodarie <d.rodarie@gmail.com>
# May 2016
##

import copy
import bge

from ..simulatorUtils import SimulatorUtils


class BlenderUtils(SimulatorUtils):
    """
    Blender utility class to get information during simulation
    """

    def __init__(self, scene):
        """Class initializer"""

        SimulatorUtils.__init__(self)
        self.scene = scene

    def get_time_scale(self):
        """
        Get simulation time scale
        :return: Float time scale
        """

        return bge.logic.getLogicTicRate()

    def draw_line(self, point1, point2, color):
        """
        Draw a line inside the simulator
        :param point1: Vector point 1
        :param point2: Vector point 2
        :param color: Vector RGB color
        """

        bge.render.drawLine(point1, point2, color)

    def exists_object(self, name):
        """
        Test if the object exist in the simulator
        :param name: String name of the object
        :return: Boolean True if the simulator has the object
        """

        return name in self.scene.objects

    def get_object(self, name):
        """
        Get the simulator object if it exists
        :param name: String name of the object
        :return: Object obj of the simulator
        """

        if self.exists_object(name):
            return self.scene.objects[name]
        return None

    def get_orientation(self, name):
        """
        Get the object orientation inside the simulator
        :param name: String name of the object
        :return: Vector orientation of the object
        """

        obj = self.get_object(name)
        if obj is not None:
            return copy.copy(obj.worldOrientation.to_euler())
        return None

    def get_world_position(self, obj):
        """
        Get the position of an object in the simulator world
        :param obj: Object
        :return: Vector position of the object
        """

        return obj.worldPosition

    def update_world_position(self, obj, origin):
        """
        Update the position of an origin point relative to an object movement
        :param obj: Object simulator object
        :param origin: Vector point to update
        :return: Vector point new position
        """

        return obj.worldTransform * origin

    def get_velocity(self, obj, origin):
        """
        Get an origin point velocity relative to an object movement
        :param obj: Object simulator object
        :param origin: Vector point to test
        :return: Vector velocity of the point
        """

        return obj.getVelocity(origin)

    def apply_impulse(self, obj, impulse, point):
        """
        Apply an impulse force on an object at a certain point
        :param obj: Object simulator object
        :param impulse: Force to apply
        :param point: Vector point origin of the impulse
        """

        obj.applyImpulse(point, impulse)

    def apply_torque(self, obj, torque):
        """
        Apply a torque on an object
        :param obj: Object simulator object
        :param torque: Force to apply
        """

        obj.applyTorque(torque)
