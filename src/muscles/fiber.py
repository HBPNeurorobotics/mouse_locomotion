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
    def __init__(self, h, pcsa, length, velocity, f_05):
        self.h = h

        # Fiber parameters
        self.f_05 = f_05
        self.length = length
        self.max_length = 0.
        self.velocity = velocity
        self.pcsa = pcsa

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

    def __process_recruitment(self, spike_frequency):
        self.f_env = self.f_min + (self.f_max - self.f_min) / (
            1 - self.u_th) * spike_frequency if spike_frequency > self.u_th else self.f_min
        return self.f_env

    def __process_tf(self, d_f_eff):
        self.tf = self.t_f1 * math.pow(self.length, 2) + self.t_f2 * self.f_env if d_f_eff >= 0. \
            else (self.t_f3 + self.t_f4 * self.activation_frequency) / self.length
        return self.tf

    def __process_intermediate_firing_frequency(self):
        d_f_int = (self.f_env - self.f_int) / self.tf
        self.f_int += self.h * d_f_int
        return self.f_int

    def __process_effective_firing_frequency(self):
        d_f_eff = (self.f_int - self.f_eff) / self.tf
        self.f_eff += self.h * d_f_eff
        return self.f_eff

    def __specific_function(self):
        return 1.

    def __process_nf(self):
        self.nf = self.n_f0 + self.n_f1 * (1 / self.length - 1)
        return self.nf

    def __process_activation_frequency(self):
        nf = self.__process_nf()

        self.activation_frequency = 1 - math.exp(
            - math.pow((self.__specific_function() * self.f_eff / (self.af * nf)), nf))
        return self.activation_frequency

    def __process_force_length(self):
        return math.exp(-math.pow(math.fabs((math.pow(self.length, self.beta) - 1) / self.omega), self.rho))

    def __process_force_velocity(self):
        if self.velocity <= 0:
            return (self.max_velocity - self.velocity) / \
                   (self.max_velocity + self.velocity * (self.c_v0 + self.c_v1 * self.length))
        else:
            return (self.b_v - self.velocity *
                    (self.a_v0 + self.a_v1 * self.length + self.a_v2 * math.pow(self.length, 2))) / \
                   (self.b_v + self.velocity)

    def __process_parallel_elastic(self):
        return self.c1 * self.k1 * math.log(math.exp((self.length / self.max_length - self.l_r1) / self.k1) + 1) + \
               self.eta * self.velocity

    def __process_thick_filament_compression(self):
        return self.c2 * (math.exp(self.k2 * (self.length - self.l_r2)) - 1)

    def __process_series_elastic(self):
        return self.c_t * self.k_t * math.log(math.exp((self.length - self.l_t) / self.k_t) + 1)

    def __process_passive_force(self):
        return self.__process_parallel_elastic() + \
               self.activation_frequency * self.__process_thick_filament_compression()

    def __process_active_force(self):
        return self.__process_force_length() * self.__process_force_velocity() * self.activation_frequency

    def update_force(self, spike_frequency):
        self.__process_recruitment(spike_frequency)
        self.__process_tf((self.f_int - self.f_eff) / self.tf if self.tf != 0 else 0.)
        self.__process_intermediate_firing_frequency()
        self.__process_effective_firing_frequency()
        self.__process_nf()
        self.__process_activation_frequency()

        return self.__process_passive_force() + self.__process_active_force()


class SlowTwitchFiber(Fiber):
    def __init__(self, h, pcsa, length, velocity, f_05):
        Fiber.__init__(self, h, pcsa, length, velocity, f_05)
        # Yielding parameters

        self.c_gamma = 0.35
        self.v_gamma = 0.1
        self.t_gamma = 200  # in ms
        self.yielding = 0.

    def __specific_function(self):
        """
        Process yielding activity of the muscle.
        :return: updated yielding
        """
        d_yielding = (1 - self.c_gamma * (1 - math.exp(-self.velocity / self.v_gamma)) - self.yielding) / self.t_gamma
        self.yielding += d_yielding * self.h
        return self.yielding


class FastTwitchFiber(Fiber):
    def __init__(self, h, pcsa, length, velocity, f_05):
        Fiber.__init__(self, h, pcsa, length, velocity, f_05)
        self.u_r = 0.8
        self.u_th = self.pcsa / self.u_r

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

    def __specific_function(self):
        sag_as = self.as1 if self.f_eff < 0.1 else self.as2
        d_sag = (sag_as - self.sag) / self.ts
        self.sag = sag_as + d_sag * self.h
        return self.sag
