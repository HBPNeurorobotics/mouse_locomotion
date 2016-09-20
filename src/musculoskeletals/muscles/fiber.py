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
# July 2016
##

import math


class Fiber:
    """
    Abstract class that describe fiber muscle activity depending its length, velocity, and the current input of the
    motor neurons.
    """

    def __init__(self, h, f_pcsa, length, velocity, f_05, l_se, l_max, length_0):
        """
        Class initialization. Parameters can be found in Tsianos & al. (2012)
        :param h: Float Euler parameter
        :param f_pcsa: Float Fractional Physiological cross-sectional area of the fiber
        :param length: Float Normalized current length of the fiber
        :param velocity: Float normalized current velocity of the fiber
        :param f_05: Float firing rate frequency at which the fiber produce half of its maximal force
        :param l_se: Float Normalized length of the fiber tendon
        :param l_max: Float Maximal length of the fiber
        :param length_0: Float Maximal length of the fiber
        """

        self.h = h

        # Fiber parameters
        self.f_05 = f_05
        self.length = length
        self.l_se = l_se  # Use only to process series elastic force
        self.max_length = l_max
        self.length_0 = length_0  # Use only in energy process
        self.velocity = velocity
        self.f_pcsa = f_pcsa

        # Frequency recruitment
        self.f_min = 0.5 * self.f_05
        self.f_max = 2.0 * self.f_05
        self.f_env = 0.
        self.u_th = 0.001

        # Firing frequency parameters
        self.t_f1 = 34.3
        self.t_f2 = 22.7
        self.t_f3 = 47.0
        self.t_f4 = 25.2
        self.tf = 0.
        self.f_int = 0.
        self.f_eff = 0.

        # Activation frequency parameters
        self.af = 0.56
        self.n_f0 = 2.1
        self.n_f1 = 5
        self.nf = 0.
        self.activation_frequency = 0.

        # Force-Length parameters
        self.beta = 2.30
        self.omega = 1.12
        self.rho = 1.62

        # Force-Velocity parameters
        self.max_velocity = -7.88
        self.c_v0 = 5.88
        self.c_v1 = 0.
        self.a_v0 = -4.70
        self.a_v1 = 8.41
        self.a_v2 = -5.34
        self.b_v = 0.35

        # Parallel elastic parameters
        self.c1 = 23.
        self.k1 = 0.046
        self.l_r1 = 1.17
        self.eta = 0.01

        # Thick filament compression parameters
        self.c2 = -0.02
        self.k2 = -21.0
        self.l_r2 = 0.70

        # Series elastic element
        self.c_t = 27.8
        self.k_t = 0.0047
        self.l_t = 0.964

        # Initial Energy parameters
        self.e1 = -76.6
        self.e2 = -792
        self.e3 = 124
        self.e4 = 0.72

        # Total Energy parameters
        self.m = 0.25
        self.r = 1.5
        self.a = 0.33
        self.initial_energy = 0.

    def __process_recruitment(self, spike_frequency):
        """
        Update the recruitment of the fiber based on the frequency of the spikes input
        :param spike_frequency: Float frequency of the spiking input
        :return: Float frequency recruitment of the fiber
        """

        self.f_env = self.f_min + (self.f_max - self.f_min) / (
            1 - self.u_th) * spike_frequency if spike_frequency > self.u_th else self.f_min
        return self.f_env

    def __process_tf(self, d_f_eff, length):
        """
        Process tf value used to process intermediate and effective firing frequencies
        :param d_f_eff: Float derived effective firing frequency
        :return: Float tf value
        """

        self.tf = self.t_f1 * pow(length, 2) + self.t_f2 * self.f_env if d_f_eff >= 0. \
            else (self.t_f3 + self.t_f4 * self.activation_frequency) / length
        return self.tf

    def __intermediate_firing_frequency(self):
        """
        Update intermediate firing frequency which will be used to process effective firing frequency
        :return: Float intermediate firing frequency
        """

        if self.f_int == 0.:
            self.f_int = self.f_env
        d_f_int = (self.f_env - self.f_int) / self.tf
        self.f_int += self.h * d_f_int
        return self.f_int

    def __effective_firing_frequency(self):
        """
        Update effective firing frequency which will be used to process muscle activity
        :return:  Float effective firing frequency
        """

        if self.f_eff == 0.:
            self.f_eff = self.f_int
        d_f_eff = (self.f_int - self.f_eff) / self.tf
        self.f_eff += self.h * d_f_eff
        return self.f_eff

    def __specific_function(self):
        """
        Define the specific function of the fiber that is used to process muscle activity
        :return: Float activation parameter
        """

        return 1.

    def __process_nf(self, length):
        """
        Update the shape of the sigmoid relationship (nf) based on fiber length
        :return: Float nf parameter
        """

        self.nf = self.n_f0 + self.n_f1 * (1 / length - 1)
        return self.nf

    def __activation_frequency(self, length):
        """
        Update activation frequency which can be used to process active and passive fiber forces
        :return: Float activation frequency of the fiber
        """

        self.__process_nf(length)
        spec = self.__specific_function()
        param = spec * self.f_eff / (self.af * self.nf)
        self.activation_frequency = 1 - math.exp(-pow(param, self.nf))
        return self.activation_frequency

    def __force_length(self):
        """
        Process the active force based on the current length of the fiber
        :return: Float length based active force of the fiber
        """

        return math.exp(-pow(math.fabs((pow(self.length, self.beta) - 1) / self.omega), self.rho))

    def __force_velocity(self):
        """
        Process the active force based on the current velocity of the fiber
        :return: Float velocity based active force of the fiber
        """

        if self.velocity <= 0:
            return (self.max_velocity - self.velocity) / \
                   (self.max_velocity + self.velocity * (self.c_v0 + self.c_v1 * self.length))
        else:
            return (self.b_v - self.velocity *
                    (self.a_v0 + self.a_v1 * self.length + self.a_v2 * pow(self.length, 2))) / \
                   (self.b_v + self.velocity)

    def __parallel_elastic(self):
        """
        Process the passive force of the parallel elastic part of the fiber
        :return: Float parallel elastic force of the fiber
        """

        return self.c1 * self.k1 * math.log(
            math.exp((self.length / self.max_length - self.l_r1) / self.k1) + 1) + self.eta * self.velocity

    def __thick_filament_compression(self):
        """
        Process the passive force due to the thick filament compression of the fiber
        :return: Float thick filament compression force of the fiber
        """

        return self.c2 * (math.exp(self.k2 * (self.length - self.l_r2)) - 1)

    def __series_elastic(self):
        """
        Process the passive force due to the tendon the fiber
        :return: Float tendon force of the fiber
        """

        return self.c_t * self.k_t * math.log(math.exp((self.l_se - self.l_t) / self.k_t) + 1)

    def get_length_elastic(self, force):

        return self.l_t + self.k_t * math.log(math.exp(force / (self.c_t * self.k_t)) - 1)

    def __passive_force(self):
        """
        Update the passive force of the muscle
        :return: Float passive force deployed by the muscle
        """

        return self.__parallel_elastic() + self.activation_frequency * self.__thick_filament_compression()

    def __active_force(self):
        """
        Update the active force of the muscle
        :return: Float active force deployed by the muscle
        """

        return self.__force_length() * self.__force_velocity() * self.activation_frequency

    def __effective_activation(self, force, length):
        """
        Computes effective activation of the fiber
        :param force: Float force applied on the fiber
        :param length: Float length of the fiber
        :return: Float effective activation frequency
        """

        self.__update_activation_frequency(self.f_max, length)
        return self.activation_frequency

    def __initial_energy(self, force):
        """
        Computes the initial energy consumed by the fiber during contraction
        :param force: Float force applied on the fiber
        :return: Float initial energy
        """

        return self.__cross_bridge_energy(force, self.length, self.velocity) + self.__activation_energy(force)

    def __initial_tetanic_energy(self, velocity):
        """
        Computes the initial tetanic energy consumed by the fiber during contraction
        :param velocity: Float velocity of the fiber
        :return: Float tetanic energy
        """

        return (self.e1 * pow(velocity, 2) + self.e2 * velocity + self.e3) / (self.e4 - velocity)

    def __cross_bridge_energy(self, force, length, velocity):
        """
        Computes cross-bridge energy consumed by the fiber during contraction
        :param force: Float force applied on the fiber
        :param length: Float length of the fiber
        :param velocity: Float velocity of the fiber
        :return: Float cross-bridge energy
        """

        return self.__effective_activation(force, length) * self.__force_length() * self.__tetanic_cross_bridge_energy(
            velocity)

    def __tetanic_cross_bridge_energy(self, velocity):
        """
        Computes tetanic cross-bridge energy consumed by the fiber during contraction
        :param velocity: Float velocity of the fiber
        :return: Float tetanic cross-bridge energy
        """

        if velocity <= 0.:
            return self.__initial_tetanic_energy(velocity) - self.__tetanic_activation_energy()
        f_tet_xb_0 = self.__tetanic_cross_bridge_energy(0.)
        return f_tet_xb_0 + self.velocity * (f_tet_xb_0 - self.__tetanic_cross_bridge_energy(-self.h)) / self.h

    def __activation_energy(self, force):
        """
        Computes the energy consumed to activate the fiber
        :param force: Float force applied on the fiber
        :return: Float activation energy
        """

        return self.a / (1 - self.a) * self.__cross_bridge_energy(force, self.length_0, 0.)

    def __tetanic_activation_energy(self):
        """
        Computes the tetanic energy consumed to activate the fiber
        :return: Float tetanic activation energy
        """

        return self.a * self.__initial_tetanic_energy(0.)

    def __recovery_energy(self, force):
        """
        Computes the energy consumed to recover during fiber contraction
        :param force: Float force applied on the fiber
        :return: Float recovery energy
        """

        return self.__initial_energy(force) * self.r

    def __update_activation_frequency(self, spike_frequency, length):
        """
        Update the activation frequency of a muscle
        :param spike_frequency: Float activation frequency of motor neurons activity
        :param length: Float length of the muscle
        """

        self.__process_recruitment(spike_frequency)
        self.__process_tf((self.f_int - self.f_eff) / self.tf if self.tf != 0 else 0., length)
        self.__intermediate_firing_frequency()
        self.__effective_firing_frequency()
        self.__activation_frequency(self.length)

    def update_force(self, spike_frequency, length, velocity):
        """
        Update the force of the muscle
        :return: Float force deployed by the muscle
        """

        self.length = length
        self.velocity = velocity
        self.__update_activation_frequency(spike_frequency, self.length)

        return self.__passive_force() + self.__active_force()

    def update_energy(self, force):
        """
        Update fiber energy consumption
        :param force: Float Force developed by the fiber
        :return: Float fiber energy consumption
        """

        return (self.__initial_energy(force) +
                self.__recovery_energy(force)) * self.m

    def print_updates(self):
        """Debug function to print the update on a fiber"""

        print("F_env: " + str(self.f_env) + "\n" +
              "F_int: " + str(self.f_int) + "\n" +
              "F_eff: " + str(self.f_eff) + "\n" +
              "F_act: " + str(self.activation_frequency) + "\n" +
              "Active force: " + str(self.__active_force()) + "\n" +
              "Passive force: " + str(self.__passive_force()) + "\n")


class SlowTwitchFiber(Fiber):
    """
    Describe slow twitch muscle fibers and their activity. Corresponds approximately to Type I muscle fibers
    """

    def __init__(self, h, f_pcsa, length, velocity, f_05, l_se, l_max, length_0):
        """
        Class initialization. Parameters can be found in Tsianos & al. (2012)
        :param h: Float Euler parameter
        :param f_pcsa: Float Fractional Physiological cross-sectional area of the fiber
        :param length: Float Normalized current length of the fiber
        :param velocity: Float normalized current velocity of the fiber
        :param f_05: Float firing rate frequency at which the fiber produce half of its maximal force
        :param l_se: Float Normalized length of the fiber tendon
        :param l_max: Float Maximal length of the fiber
        :param length_0: Float Maximal length of the fiber
        """

        Fiber.__init__(self, h, f_pcsa, length, velocity, f_05, l_se, l_max, length_0)
        # Yielding parameters

        self.c_gamma = 0.35
        self.v_gamma = 0.1
        self.t_gamma = 200  # in ms
        self.yielding = 0.

    def __specific_function(self):
        """
        Process yielding activity of the muscle.
        :return: Float updated yielding
        """

        d_yielding = (1 - self.c_gamma * (1 - math.exp(-self.velocity / self.v_gamma)) - self.yielding) / self.t_gamma
        self.yielding += d_yielding * self.h
        return self.yielding


class FastTwitchFiber(Fiber):
    """
    Describe fast twitch muscle fibers and their activity. Corresponds approximately to Type II muscle fibers
    """

    def __init__(self, h, pcsa, length, velocity, f_05, l_se, l_max, length_0):
        """
        Class initialization. Parameters can be found in Tsianos & al. (2012)
        :param h: Float Euler parameter
        :param pcsa: Float Physiological cross-sectional area of the fiber
        :param length: Float Normalized current length of the fiber
        :param velocity: Float normalized current velocity of the fiber
        :param f_05: Float firing rate frequency at which the fiber produce half of its maximal force
        :param l_se: Float Normalized length of the fiber tendon
        :param l_max: Float Maximal length of the fiber
        :param length_0: Float Maximal length of the fiber
        """

        Fiber.__init__(self, h, pcsa, length, velocity, f_05, l_se, l_max, length_0)
        self.u_r = 0.8
        self.u_th = self.f_pcsa * self.u_r

        # Sag parameters
        self.as1 = 1.76
        self.as2 = 0.96
        self.ts = 43
        self.sag = 0.

        # Firing frequency parameters
        self.t_f1 = 20.6
        self.t_f2 = 13.6
        self.t_f3 = 28.2
        self.t_f4 = 15.1

        # Activation frequency parameters
        self.n_f1 = 3.3

        # Force-Length parameters
        self.beta = 1.55
        self.omega = 0.75
        self.rho = 2.12

        # Force-Velocity parameters
        self.max_velocity = -9.15
        self.c_v0 = -5.70
        self.c_v1 = 9.18
        self.a_v0 = -1.53
        self.a_v1 = 0.
        self.a_v2 = 0.
        self.b_v = 0.69

        # Initial Energy parameters
        self.e1 = 145
        self.e2 = -3322
        self.e3 = 1530
        self.e4 = 1.45

        # Total Energy parameters
        self.r = 1.

    def __specific_function(self):
        """
        Process sag activity of the muscle.
        :return: Float updated sag
        """

        sag_as = self.as1 if self.f_eff < 0.1 else self.as2
        d_sag = (sag_as - self.sag) / self.ts
        self.sag = sag_as + d_sag * self.h
        return self.sag
