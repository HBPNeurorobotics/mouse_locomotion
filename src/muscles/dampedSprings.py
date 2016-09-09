from muscles import Muscle
from mathutils import Vector as vec


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
        self.k = self.params["k"]  # scalar in N/m??
        self.c = self.params["c"]  # scalar in N.s/m??
        self.k_cont = self.params["kc"]  # no dimension
        self.ctrl_sig = None
        if self.active:
            self.l = self.app_point_2_world - self.app_point_1_world  # global coordinate vector between app points in m
            self.v_1 = self.obj1.getVelocity(self.app_point_1)  # vector in m/s??
            self.v_2 = self.obj2.getVelocity(self.app_point_2)  # vector in m/s??
            v = self.v_2 - self.v_1  # vector in m/s??
            self.v_norm = v.dot(self.l.normalized()) * self.l.normalized()  # normal velocity vector in m/s??
            self.l0 = self.params["kl0"] * self.l.length  # scalar in m??
            self.l_cont = self.l0  # scalar in m??
            self.force = vec((0, 0, 0))  # vector in N??

    def get_power(self):
        """
        Return the time-step power developped by the muscle on the two extremity objects
        :return: Float power consumed by the muscle
        """

        power = 0.0
        if self.ctrl_sig != 0.0:  # and float((self.force * self.l.normalized())) < 0.0:
            power_1 = - self.force * self.v_1
            power_2 = self.force * self.v_2
            power = power_2 + power_1

            self.logger.debug("v_1 = " + str(self.v_1.length) + " m/s; v_2 = " + str(self.v_2.length) +
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

        if "ctrl_sig" in kwargs:
            self.ctrl_sig = kwargs["ctrl_sig"]
        else:
            self.ctrl_sig = None

        # If muscle has not been deactivated
        if self.active:

            # get control length
            if self.ctrl_sig is None:
                self.l_cont = self.l0  # by default, control length is the spring reference length
            else:
                self.l_cont = self.l0 * (1 + self.k_cont * self.ctrl_sig)

            # get length and velocity
            self.app_point_1_world = self.obj1.worldTransform * self.app_point_1
            self.app_point_2_world = self.obj2.worldTransform * self.app_point_2
            self.l = self.app_point_2_world - self.app_point_1_world

            # Damping must be in spring axis direction
            self.v_1 = self.obj1.getVelocity(self.app_point_1)
            self.v_2 = self.obj2.getVelocity(self.app_point_2)
            v = self.v_2 - self.v_1
            self.v_norm = v.dot(self.l.normalized()) * self.l.normalized()
            # print("l: " + str(self.l) + " norm: " + str(self.l.normalized()) + " v = " +  str(v) +
            # "vdot" + str(v.dot(self.l.normalized())) +" vnorm: " + str(self.v_norm))

            # compute spring force
            force_s = - (self.k * (self.l.length - self.l_cont)) * self.l.normalized()

            # compute damping force
            force_d = - self.c * self.v_norm

            # compute total force
            self.force = force_s + force_d
            impulse = self.force / self.simulator.get_time_scale()

            # apply impulse on an object point only in traction
            f_type = "Push"
            if float((self.force * self.l.normalized())) < 0.0:
                f_type = "Pull"
                self.obj1.applyImpulse(self.app_point_1_world, - impulse)
                self.obj2.applyImpulse(self.app_point_2_world, impulse)

            # DEBUG data
            self.draw_muscle()
            self.n_iter += 1

            # self.logger.debug("Muscle " + self.name + ":" + str(self.n_iter) + ": Ft = " + str(
            #    self.force) + " - " + str(self.force * self.l.normalized()) + "N")
            # self.logger.debug("  Type = " + f_type)
            # self.logger.debug("  Fs = " + str(force_s) + " ;  Fd = " + str(force_d))
            # self.logger.debug("  l = " + str(self.l) + " ; l0 = " + str(self.l0))
            # self.logger.debug("  L P1 = " + str(self.app_point_1) + " ; L P2 = " + str(self.app_point_2))
            # self.logger.debug("  G P1 = " + str(self.app_point_1_world) + " ; G P2 = " + str(self.app_point_2_world))

        else:
            self.logger.warning("Muscle " + self.name + " has been deactivated.")


class DampedSpringReducedTorqueMuscle(Muscle):
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

        Muscle.__init__(self, params_, simulator)
        # Model constants and variables
        if "k" in self.params:
            self.k = self.params["k"]  # scalar in N/m
        else:
            self.k_cont = 100
        if "c" in self.params:
            self.c = self.params["c"]  # scalar in N.s/m
        else:
            self.k_cont = 10
        if "kc" in self.params:
            self.k_cont = self.params["kc"]  # no dimension
        else:
            self.k_cont = 0
        if "kt" in self.params:
            self.damp_torque_fact = self.params["kt"]  # no dimension
        else:
            self.damp_torque_fact = 0.1

        if self.active:
            self.l = self.app_point_2_world - self.app_point_1_world  # global coordinate vector between app points in m
            v = self.obj2.getVelocity(self.app_point_2) - self.obj1.getVelocity(self.app_point_1)
            self.v_norm = v.dot(self.l.normalized()) * self.l.normalized()  # normal velocity vector in m/s
            self.l0 = self.params["kl0"] * self.l.length  # scalar in m
            self.l_cont = self.l0  # scalar in m

    def update(self, **kwargs):
        """
        Update and apply forces on the objects connected to the spring. The spring can be controlled in length by \
        fixing manually l0
        :param kwargs: Dictionary containing muscle updates
        """

        if "ctrl_sig" in kwargs:
            ctrl_sig = kwargs["ctrl_sig"]
        else:
            ctrl_sig = None

        # If muscle has not been deactivated
        if self.active:
            # get control length
            if ctrl_sig is None:
                self.l_cont = self.l0  # by default, control length is the spring reference length
            else:
                self.l_cont = self.l0 * (1 + self.k_cont * ctrl_sig)

            # get length and velocity
            self.app_point_1_world = self.obj1.worldTransform * self.app_point_1
            self.app_point_2_world = self.obj2.worldTransform * self.app_point_2
            self.l = self.app_point_2_world - self.app_point_1_world

            # Center of gravity and lever arm
            cg_1 = self.obj1.worldPosition
            cg_2 = self.obj2.worldPosition
            lever_1_vect = self.app_point_1_world - cg_1
            lever_2_vect = self.app_point_2_world - cg_2

            # Damping must be in spring axis direction.
            v = self.obj2.getVelocity(self.app_point_2) - self.obj1.getVelocity(self.app_point_1)
            self.v_norm = v.dot(self.l.normalized()) * self.l.normalized()
            # print("l: " + str(self.l) + " norm: " + str(self.l.normalized()) + " v = " +  str(v) +
            # "vdot" + str(v.dot(self.l.normalized())) +" vnorm: " + str(self.v_norm))

            # compute spring force
            force_s = - (self.k * (self.l.length - self.l_cont)) * self.l.normalized()

            # compute damping force
            force_d = - self.c * self.v_norm

            # compute total force
            force = force_s + force_d

            # compute total torques
            torque_1 = self.damp_torque_fact * lever_1_vect.cross(-force)
            torque_2 = self.damp_torque_fact * lever_2_vect.cross(force)

            # apply impulse on an object point only in traction
            f_type = "Push"
            if float((force * self.l.normalized())) < 0.0:
                f_type = "Pull"
                self.obj1.applyForce(- force)
                self.obj2.applyForce(force)
                self.obj1.applyTorque(torque_1)
                self.obj2.applyTorque(torque_2)

            # DEBUG data
            self.draw_muscle()
            self.n_iter += 1

            self.logger.debug("Muscle " + self.name + ":" + str(self.n_iter) + ": Ft = " + str(
                force) + " - " + str(force * self.l.normalized()) + "N")
            self.logger.debug("  Type = " + f_type)
            self.logger.debug("  Fs = " + str(force_s) + " ;  Fd = " + str(force_d))
            self.logger.debug("  l = " + str(self.l) + " ; l0 = " + str(self.l0))
            self.logger.debug("  L P1 = " + str(self.app_point_1) + " ; L P2 = " + str(self.app_point_2))
            self.logger.debug("  G P1 = " + str(self.app_point_1_world) + " ; G P2 = " + str(self.app_point_2_world))
            self.logger.debug("  G O1 = " + str(cg_1) + " ; G O2 = " + str(cg_1))
            self.logger.debug("  G OP 1 = " + str(lever_1_vect) + " ; G CG 2 = " + str(lever_2_vect))
            self.logger.debug("  T1 = " + str(torque_1) + " ; T2 = " + str(torque_2))
        else:
            self.logger.warning("Muscle " + self.name + " has been deactivated.")
