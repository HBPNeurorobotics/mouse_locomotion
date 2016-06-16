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
# February 2016
##

import numpy as np


class Matsuoka:
    """This class represents the mouse brain and its current behaviour in the control process"""

    def __init__(self, config_):
        """Class initialization"""

        self.config = config_
        self.h = self.config.brain["h"]  # Constant for Euler's approximation method
        self.tau = self.config.brain["tau"]  # Time constant tau = RC
        self.T = self.config.brain["T"]  # Time constant for adaptation
        self.a = self.config.brain["a"]
        self.b = self.config.brain["b"]  # Adaptation parameter
        self.c = self.config.brain["c"]  # Default membrane potential
        self.aa = self.config.brain["aa"]
        self.A = self.aa * np.array([[0, -1, 1, -1], [-1, 0, -1, 1], [-1, 1, 0, -1], [1, -1, -1, 0]])  # Gate matrix
        self.n_osc = self.config.brain["n_osc"]  # Number of oscillators
        self.x = np.zeros((self.n_osc, 1)) + np.array([[0.1], [0.1], [0.2], [0.2]])
        self.v = np.zeros((self.n_osc, 1)) + np.array([[0.1], [0.1], [0.2], [0.2]])
        self.y = np.zeros((self.n_osc, 1)) + np.array([[0.1], [0.1], [0.2], [0.2]])
        self.g = lambda x: max(0., x)  # Spiking threshold equals 0
        self.Record = 0
        self.time = []
        self.time_interval = self.config.brain["time_interval"]
        self.iter_num = int(self.time_interval / self.h)

    def update(self):
        """Update control signals and forces"""

        for i in range(self.iter_num):
            self.x += self.h * (- self.x + self.c - self.A.dot(self.y) - self.b * self.v) / self.tau
            self.v += self.h * (- self.v + self.y) / self.T
            for i in range(self.n_osc):
                self.y[i] = self.g(self.x[i])


class Brain:
    """This class represents the mouse brain and its current behaviour in the control process"""

    def __init__(self, config_):
        """Class initialization"""

        self.n_iter = 0
        self.config = config_
        self.logger = config_.logger
        self.name = self.config.brain["name"]
        self.n_osc = self.config.brain["n_osc"]
        self.osc = Matsuoka(self.config)
        self.state = np.zeros((self.n_osc, 1))

    def update(self):
        """Update control signals and forces"""

        # Write control signals into y
        self.osc.update()
        self.state = self.osc.y

        self.n_iter += 1
        self.logger.debug("Brain " + self.name + " iteration " + str(self.n_iter) + ": State vector: " +
                          str(np.transpose(self.state)))
