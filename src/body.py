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


import math
import logging
from mathutils import Vector as vec
import sys

from brain import Brain
from muscle import *


class Leg:
    """This class represents a generic leg and its current behaviour in the control process"""

    def __init__(self, scene_, config_):
        """Class initialization"""

        self.n_iter = 0
        self.scene = scene_
        self.config = config_
        self.logger = config_.logger

        # Create the muscles objects
        self.muscles = []
        self.connection_matrix = self.config.connection_matrix
        self.muscle_type = self.config.muscle_type + "(self.scene, muscle_config)"

    def get_power(self):
        """Return the time-step power developped by all the leg muscles"""

        power = 0
        for m in self.muscles:
            power += m.get_power()

        return power

    def update(self, ctrl_sig_):
        """Update control signals and forces"""

        self.n_iter += 1
        self.logger.debug("Leg iteration: " + str(self.n_iter))


class Backleg(Leg):
    """This class represents a generic backleg and its current behaviour in the control process"""

    def __init__(self, scene_, config_, orien_):
        """Class initialization"""

        Leg.__init__(self, scene_, config_)
        self.orien = orien_

        # Create the muscles objects following config
        if self.orien == "L":
            for muscle_config in self.config.back_leg_L_muscles:
                self.muscles.append(eval(self.muscle_type))
        else:  # R
            for muscle_config in self.config.back_leg_R_muscles:
                self.muscles.append(eval(self.muscle_type))

    def update(self, brain_output):
        """Update control signals and forces"""

        # Update each muscle separately
        for i in range(len(self.muscles)):
            # Assertion
            if len(self.connection_matrix[self.muscles[i].name]) != len(brain_output):
                self.logger.error("The brain outputs number (" + len(brain_output) + 
                    ") should match the number in the connection matrix (" +
                    len(self.connection_matrix[self.muscles[i].name]) + "). Please verify config!") 
            # Send linear combination of brain outputs
            else:
                ctrl_sig = 0
                j = 0
                for output in brain_output:
                    ctrl_sig += self.connection_matrix[self.muscles[i].name][j] * output
                    j += 1
                    
                self.muscles[i].update(ctrl_sig=ctrl_sig)

                self.n_iter += 1
                self.logger.debug("Backleg " + self.orien + " iteration " + str(self.n_iter) + ": Control signal = " +
                    str(ctrl_sig))


class Foreleg(Leg):
    """This class represents a generic foreleg and its current behaviour in the control process"""

    def __init__(self, scene_, config_, orien_):
        """Class initialization"""

        Leg.__init__(self, scene_, config_)
        self.orien = orien_

        # Create the muscles objects following config
        if self.orien == "L":
            for muscle_config in self.config.front_leg_L_muscles:
                self.muscles.append(eval(self.muscle_type))
        else:  # R
            for muscle_config in self.config.front_leg_R_muscles:
                self.muscles.append(eval(self.muscle_type))

    def update(self, brain_output):
        """Update control signals and forces"""

        # Update each muscle separately
        for i in range(len(self.muscles)):
            # Assertion
            if len(self.connection_matrix[self.muscles[i].name]) != len(brain_output):
                self.logger.error("The brain outputs number (" + len(brain_output) + 
                    ") should match the number in the connection matrix (" +
                    len(self.connection_matrix[self.muscles[i].name]) + "). Please verify config!") 
            # Send linear combination of brain outputs
            else:
                ctrl_sig = 0
                j = 0
                for output in brain_output:
                    ctrl_sig += self.connection_matrix[self.muscles[i].name][j] * output
                    j += 1

                self.muscles[i].update(ctrl_sig=ctrl_sig)

                self.n_iter += 1
                self.logger.debug("Foreleg " + self.orien + " iteration " + str(self.n_iter) + ": Control signal = " +
                  str(ctrl_sig))


class Body:
    """This class represents the mouse body and its current behaviour in the control process"""

    def __init__(self, scene_, config_):
        """Class initialization"""

        self.n_iter = 0
        self.scene = scene_
        self.config = config_
        self.logger = config_.logger
        self.muscle_type = self.config.muscle_type + "(self.scene, muscle_config)"
        self.name = self.config.body["name"]

        # Get body object
        if not self.config.body["obj"] in self.scene.objects:
            self.logger.error("Body " + self.name + " doesn't exit. Check your configuration file!")
            self.active = False
        else:
            self.body_obj = self.scene.objects[self.config.body["obj"]]

        # Create and init variables for loss function
        self.origin = self.body_obj.worldTransform * vec((0, 0, 0))
        self.position = self.origin
        self.dist = vec(self.position - self.origin).length
        self.powers = []
        self.av_power = 0.0
        self.loss_fct = 0.0

        # Create 4 legs
        self.l_fo_leg = Foreleg(scene_, config_, "L")
        self.r_fo_leg = Foreleg(scene_, config_, "R")
        self.l_ba_leg = Backleg(scene_, config_, "L")
        self.r_ba_leg = Backleg(scene_, config_, "R")

        # Create the brain object
        self.brain = Brain(scene_, config_)

        # Create the muscles objects following config
        self.muscles = []
        for muscle_config in self.config.body["muscles"]:
            self.muscles.append(eval(self.muscle_type))

    def compute_traveled_dist(self):
        """Return a float representing the distance between origin and the current position"""

        # Get current position
        self.position = self.body_obj.worldTransform * vec((0, 0, 0))

        # Get distance
        self.dist = vec(self.position - self.origin).length

        return

    def compute_power(self):
        """Compute time-step power at each iteration"""

        power = 0.0

        # Get power from legs
        power += self.l_ba_leg.get_power()
        power += self.r_ba_leg.get_power()
        power += self.l_fo_leg.get_power()
        power += self.r_fo_leg.get_power()

        # Get power from body muscles
        for m in self.muscles:
            power += m.get_power()

        # Append to powers list
        self.powers.append(power)

        return

    def get_loss_fct(self):
        """Compute the body loss function. This should be called only at the end of the simulation
        in order to avoid useless computation at each iteration"""

        self.compute_traveled_dist()
        self.av_power = sum(self.powers) / float(len(self.powers))

        self.loss_fct = math.tanh(self.dist / self.config.dist_ref) * \
            math.tanh(self.config.power_ref / self.av_power)

        return self.loss_fct

    def update(self):
        """Update control signals and forces"""

        # Update brain
        self.brain.update()
        brain_output = [float(self.brain.state[0]), float(self.brain.state[1]), float(self.brain.state[2]),
                    float(self.brain.state[3])]

        # Update the four leg
        self.l_ba_leg.update(brain_output)
        self.r_ba_leg.update(brain_output)
        self.l_fo_leg.update(brain_output)
        self.r_fo_leg.update(brain_output)

        # Update other muscles
        for muscle in self.muscles:
            muscle.update()

        # Update powers list
        self.compute_power()

        self.n_iter += 1
        self.logger.debug("Body " + self.name + " iteration " + str(self.n_iter))
        self.logger.debug("Average power: " + "{0:0.2f}".format(self.av_power))
