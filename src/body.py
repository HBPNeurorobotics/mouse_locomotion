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

from mathutils import Vector as vec

from muscles import *
from oscillators import ParallelOscillator
from sensors import Vestibular


class Part:
    """
    Abstract Class to represent body part
    """

    def __init__(self, config_, simulator, name):
        """
        Class initialization
        :param config_: Dictionary containing part parameters
        :param simulator: String name of the simulator class utility
        :param name: String name of the part
        """

        self.n_iter = 0
        self.config = config_
        self.logger = config_["logger"]
        self.simulator = simulator
        # Create the muscles objects
        self.muscles = []
        self.muscle_type = config_["muscle_type"] + "(muscle_config, self.simulator)"
        self.name = name

    def get_power(self):
        """
        Return the time-step power developed by all the leg muscles
        :return: Float power consumed by each muscle
        """

        power = 0
        for m in self.muscles:
            power += m.get_power()

        return power

    def update(self, brain_output):
        """
        Update control signals and forces
        :param brain_output: List of Float signals from the brain
        """


class Leg(Part):
    """This class represents a generic leg and its current behaviour in the control process"""

    def __init__(self, config_, orien_, simulator, name):
        """
        Class initialization
        :param config_: Dictionary containing part parameters
        :param orien_: String describing leg orientation
        :param simulator: String name of the simulator class utility
        :param name: String name of the part
        """

        Part.__init__(self, config_, simulator, name)
        self.orientation = orien_
        # Create the muscles objects
        for muscle_config in config_["muscles"]:
            self.muscles.append(eval(self.muscle_type))
        self.connection_matrix = config_["connection_matrix"]

    def update(self, brain_output):
        """
        Update control signals and forces
        :param brain_output: List of Float signals from the brain
        """

        for i in range(len(self.muscles)):
            # Assertion
            if len(self.connection_matrix[self.muscles[i].name]) != len(brain_output):
                self.logger.error("The brain outputs number (" + str(len(brain_output)) +
                                  ") should match the number in the connection matrix (" +
                                  str(len(self.connection_matrix[self.muscles[i].name])) + "). Please verify config!")
            # Send linear combination of brain outputs
            else:
                ctrl_sig = 0
                j = 0
                for output in brain_output:
                    ctrl_sig += self.connection_matrix[self.muscles[i].name][j] * output
                    j += 1

                self.muscles[i].update(ctrl_sig=ctrl_sig)
                self.logger.debug(self.name + " " + self.orientation + " iteration " + str(self.n_iter) +
                                  ": Control signal = " + str(ctrl_sig))
        self.n_iter += 1

    def update_osci(self, brain_output):
        for i in range(len(self.muscles)):
            # Assertion
            if len(self.connection_matrix[self.muscles[i].name]) != len(brain_output):
                self.logger.error("The brain outputs number (" + str(len(brain_output)) +
                                  ") should match the number in the connection matrix (" +
                                  str(len(self.connection_matrix[self.muscles[i].name])) + "). Please verify config!")
            # Send linear combination of brain outputs
            else:
                ctrl_sig = 0
                j = 0
                for output in brain_output:
                    ctrl_sig += self.connection_matrix[self.muscles[i].name][j] * output
                    j += 1
                    self.muscles[i].update_frequency(ctrl_sig=ctrl_sig)


class Backleg(Leg):
    """This class represents a generic backleg and its current behaviour in the control process"""

    def __init__(self, config_, orien_, simulator):
        """
        Class initialization
        :param config_: Dictionary containing part parameters
        :param orien_: String describing leg orientation
        :param simulator: String name of the simulator class utility
        """

        config = {"logger": config_.logger,
                  "muscle_type": config_.back_leg_L_muscles[
                      'muscle_type'] if "muscle_type" in config_.back_leg_L_muscles else "DampedSpringMuscle",
                  "connection_matrix": config_.connection_matrix}
        if orien_ == "L":
            config["muscles"] = config_.back_leg_L_muscles["muscles"]
        else:
            config["muscles"] = config_.back_leg_R_muscles["muscles"]
        Leg.__init__(self, config, orien_, simulator, type(self).__name__)


class Foreleg(Leg):
    """This class represents a generic foreleg and its current behaviour in the control process"""

    def __init__(self, config_, orien_, simulator):
        """
        Class initialization
        :param config_: Dictionary containing part parameters
        :param orien_: String describing leg orientation
        :param simulator: String name of the simulator class utility
        """

        config = {"logger": config_.logger,
                  "muscle_type": config_.front_leg_L_muscles[
                      'muscle_type'] if "muscle_type" in config_.front_leg_L_muscles else "DampedSpringMuscle",
                  "connection_matrix": config_.connection_matrix}
        if orien_ == "L":
            config["muscles"] = config_.front_leg_L_muscles["muscles"]
        else:
            config["muscles"] = config_.front_leg_R_muscles["muscles"]
        Leg.__init__(self, config, orien_, simulator, type(self).__name__)


class Body(Part):
    """This class represents the mouse body and its current behaviour in the control process"""

    def __init__(self, config_, simulator):
        """
        Class initialization
        :param config_: Dictionary containing part parameters
        :param simulator: String name of the simulator class utility
        """

        Part.__init__(self,
                      {"logger": config_.logger,
                       "muscle_type": config_.body[
                           'muscle_type'] if "muscle_type" in config_.body else "DampedSpringMuscle"},
                      simulator,
                      config_.body["name"])
        self.config = config_
        # Get body object
        self.body_obj = self.simulator.get_object(config_.body["obj"])
        if self.body_obj is None:
            self.logger.error("Body " + self.name + " doesn't exit. Check your configuration file!")
            self.active = False

        # Create and init variables for loss function
        self.origin = self.body_obj.worldPosition
        self.powers = []
        self.av_power = 0.0
        self.loss_fct = 0.0
        self.penalty = False
        self.count = 0

        # Create 4 legs
        self.l_fo_leg = Foreleg(config_, "L", simulator)
        self.r_fo_leg = Foreleg(config_, "R", simulator)
        self.l_ba_leg = Backleg(config_, "L", simulator)
        self.r_ba_leg = Backleg(config_, "R", simulator)

        # Create the sensors objects
        self.sensors = [Vestibular(self.simulator)]

        # Create the brain object
        self.brain = ParallelOscillator(config_.brain)

        # Create the muscles objects following config
        for muscle_config in config_.body["muscles"]:
            self.muscles.append(eval(self.muscle_type))

    def compute_traveled_dist(self):
        """Return a float representing the distance between origin and the current position"""
        return vec(self.body_obj.worldTransform * self.origin - self.origin).x

    def compute_average_power(self):
        return sum(self.powers) / float(len(self.powers))

    def compute_average_stability(self):
        for sensor in self.sensors:
            if sensor.__class__ == Vestibular:
                return sensor.get_stability()
        return 0.

    def update_sensors(self):
        for sensor in self.sensors:
            sensor.update()

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

    def monitor_fall(self):
        """Add a fall penalty if head stay under the stand-up level for more than 20 iterations"""

        # Do it here
        head_pos = self.simulator.get_object("obj_head").worldPosition.z
        foot_pos = self.simulator.get_object("obj_wrist.L").worldPosition.z
        if head_pos < -1.8 or foot_pos > head_pos:
            if self.count > 20:
                self.penalty = True
            self.count += 1
        else:
            self.count = 0

    def get_brain_output(self):
        """
        Retrieve Brain signal to propagate to the muscles
        :return: List of Float of signals from the brain
        """

        self.brain.update()
        return [float(self.brain.state[0]), float(self.brain.state[1]), float(self.brain.state[2]),
                float(self.brain.state[3])]

    def update(self, brain_output):
        """
        Update control signals and forces
        :param brain_output: List of Float signals from the
        :return Boolean penalty depending on the model fall
        """

        # Update the four legs
        self.l_ba_leg.update(brain_output)
        self.r_ba_leg.update(brain_output)
        self.l_fo_leg.update(brain_output)
        self.r_fo_leg.update(brain_output)

        # Update other muscles
        for muscle_ in self.muscles:
            muscle_.update()

        # Update the sensory feedback
        self.update_sensors()

        # Update powers list
        self.compute_power()

        # Monitor fall
        self.monitor_fall()

        self.n_iter += 1
        self.logger.debug("Body " + self.name + " iteration " + str(self.n_iter))
        self.logger.debug("Average power: " + "{0:0.2f}".format(self.av_power))
        return self.penalty
