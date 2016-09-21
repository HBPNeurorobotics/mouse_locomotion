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
# July 2016
##

from .muscle import Muscle


class DampedSpringMuscle(Muscle):
    """
    This class implements a simple muscle composed by a spring and a damping in parallel
    """

    def __init__(self, params_, simulator):
        """
        Class initialization. Requires controller as well as two object and the local point of application \
        of the spring forces
        :param params_: Dictionary containing parameter for the muscle
        :param simulator: SimulatorUtils class to access utility functions
        """

        Muscle.__init__(self, params_, simulator)

        # Model constants and variables
        self.k = self.params["k"] if "k" in self.params else 100  # scalar in N/m
        self.c = self.params["c"] if "c" in self.params else 10  # scalar in N.s/m
        self.k_cont = self.params["kc"] if "kc" in self.params else 0  # no dimension

        if self.active:
            v = self.velocity_2 - self.velocity_1  # velocity vector
            self.v_norm = v.dot(self.length.normalized()) * self.length.normalized()  # normal velocity vector
            self.l0 = self.params["kl0"] * self.length.length  # scalar in m
            self.l_cont = self.l0  # scalar in m

    def get_power(self):
        """
        Return the time-step power developped by the muscle on the two extremity objects
        :return: Float power consumed by the muscle
        """

        power = 0.0
        if self.ctrl_sig != 0.0:  # and float((self.force * self.l.normalized())) < 0.0:
            power_1 = - self.force * self.velocity_1
            power_2 = self.force * self.velocity_2
            power = power_2 + power_1

            self.logger.debug("v_1 = " + str(self.velocity_1.length) + " m/s; v_2 = " + str(self.velocity_2.length) +
                              " m/s; F = " + str(self.force.length) + " N")
            self.logger.debug("power obj1 = " + str(power_1) + " ; power obj2 = " + str(power_2) +
                              " ; power tot = " + str(power))
        return power

    def update(self, **kwargs):
        """
        Update and apply forces on the objects connected to the spring. The spring can be controlled in length by \
        fixing manually l0
        :param kwargs: Dictionary containing muscle updates
        """
        Muscle.update(self, **kwargs)

        # If muscle has not been deactivated
        if self.active:

            # get control length
            if self.ctrl_sig is None:
                self.l_cont = self.l0  # by default, control length is the spring reference length
            else:
                self.l_cont = self.l0 * (1 + self.k_cont * self.ctrl_sig)

            # Damping must be in spring axis direction
            v = self.velocity_2 - self.velocity_1
            self.v_norm = v.dot(self.length.normalized()) * self.length.normalized()

            # compute spring force
            force_s = - (self.k * (self.length.length - self.l_cont)) * self.length.normalized()

            # compute damping force
            force_d = - self.c * self.v_norm

            # compute total force
            self.force = force_s + force_d
            impulse = self.force / self.simulator.get_time_scale()

            # apply impulse on an object point only in traction
            if float((self.force * self.length.normalized())) < 0.0:
                self.simulator.apply_impulse(self.obj1, -impulse, self.app_point_1_world)
                self.simulator.apply_impulse(self.obj2, impulse, self.app_point_2_world)

            self.logger.debug("Muscle " + self.name + ":" + str(self.n_iter) + ": Ft = " + str(
                self.force) + " - " + str(self.force * self.length.normalized()) + "N")
            self.logger.debug("  Fs = " + str(force_s) + " ;  Fd = " + str(force_d))
            self.logger.debug("  l = " + str(self.length) + " ; l0 = " + str(self.l0))
            self.logger.debug("  L P1 = " + str(self.app_point_1) + " ; L P2 = " + str(self.app_point_2))
            self.logger.debug("  G P1 = " + str(self.app_point_1_world) + " ; G P2 = " + str(self.app_point_2_world))

        else:
            self.logger.warning("Muscle " + self.name + " has been deactivated.")


class DampedSpringReducedTorqueMuscle(DampedSpringMuscle):
    """This class implements a simple muscle composed by a spring and a damper in parallel.\
    Forces and torques applied in the center of gravity are computed separately and a reduction\
    factor is added to torque to stabilise the process"""

    def __init__(self, params_, simulator):
        """
        Class initialization. Requires scene, controller as well as two object and the local point of application \
        of the spring forces
        :param params_: Dictionary containing parameter for the muscle
        :param simulator: SimulatorUtils class to access utility functions
        """

        DampedSpringMuscle.__init__(self, params_, simulator)
        # Model constants and variables
        self.damp_torque_fact = self.params["kt"] if "kt" in self.params else 0.1  # no dimension

    def update(self, **kwargs):
        """
        Update and apply forces on the objects connected to the spring. The spring can be controlled in length by \
        fixing manually l0
        :param kwargs: Dictionary containing muscle updates
        """

        DampedSpringMuscle.update(self, **kwargs)

        # If muscle has not been deactivated
        if self.active:
            # Center of gravity and lever arm
            cg_1 = self.simulator.get_world_position(self.obj1)
            cg_2 = self.simulator.get_world_position(self.obj2)
            lever_1_vect = self.app_point_1_world - cg_1
            lever_2_vect = self.app_point_2_world - cg_2

            # compute total torques
            torque_1 = self.damp_torque_fact * lever_1_vect.cross(-self.force)
            torque_2 = self.damp_torque_fact * lever_2_vect.cross(self.force)

            # apply impulse on an object point only in traction
            if float((self.force * self.length.normalized())) < 0.0:
                self.simulator.apply_torque(self.obj1, torque_1)
                self.simulator.apply_torque(self.obj2, torque_2)

            self.logger.debug("  G O1 = " + str(cg_1) + " ; G O2 = " + str(cg_1))
            self.logger.debug("  G OP 1 = " + str(lever_1_vect) + " ; G CG 2 = " + str(lever_2_vect))
            self.logger.debug("  T1 = " + str(torque_1) + " ; T2 = " + str(torque_2))
