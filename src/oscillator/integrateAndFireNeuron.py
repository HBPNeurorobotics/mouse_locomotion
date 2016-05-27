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
# File created by: Dimitri Rodarie <d.rodarie@gmail.com>. May 2016
# Modified by: Gabriel Urbain <gabriel.urbain@ugent.be>.
##

from neuron import Neuron


class IntegrateAndFireNeuron(Neuron):
    """This class represents the Integrate and Fire Neuron model"""

    def __init__(self, config_):
        """Class initialization"""
        Neuron.__init__(self)
        self.config = config_
        self.tau = self.config["tau"]  # Time constant tau = RC
        self.T = self.config["T"]  # Time constant for adaptation
        self.b = self.config["b"]  # Adaptation parameter
        self.c = self.config["c"]  # Default membrane potential
        self.v = 0.
        self.spiking_threshold = self.config["threshold"]  # Spiking threshold
        self.g = lambda x: max(self.spiking_threshold, x)
        self.h = self.config["h"]  # Constant for Euler's approximation method

    def update(self, signal):
        """Update control signals"""
        self.x += self.h * (- self.x + self.c - signal - self.b * self.v) / self.tau
        self.v += self.h * (- self.v + self.y) / self.T
        self.y = self.g(self.x)

    def set_activity(self, x):
        self.x = x
        self.y = self.g(self.x)
