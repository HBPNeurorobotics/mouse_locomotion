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
        self.c = self.config["c"]  # Default membrane potential
        self.spiking_threshold = self.config["threshold"]  # Spiking threshold
        self.spiking_force = self.config["spike"] if "spike" in self.config else 0.  # Spiking signal add for firing
        self.rest_period = self.config["rest"] if "rest" in self.config else 0.  # Rest period after spiking
        self.time = 0.
        self.h = self.config["h"]  # Constant for Euler's approximation method

    def threshold_function(self):
        if self.x > self.spiking_threshold:
            temp = self.x
            self.x = 0.
            self.time += self.h
            return temp + self.spiking_force
        else:
            return 0.

    def update(self, signal):
        """Update control signals"""
        if self.time > 0 and self.time > self.rest_period:
            self.time = 0
        elif self.time > 0:
            self.time += self.h
        else:
            self.x += self.h * (- self.x + self.c + signal) / self.tau
        self.y = self.threshold_function()

    def set_activity(self, x):
        self.x = x
        self.y = self.threshold_function()


class IntegrateAndFireAdaptationNeuron(IntegrateAndFireNeuron):
    def __init__(self, config_):
        IntegrateAndFireNeuron.__init__(self, config_)
        self.v = 0.
        self.b = self.config["b"]  # Adaptation parameter
        self.T = self.config["T"]  # Time constant for adaptation

    def threshold_function(self):
        return max(self.spiking_threshold, self.x)

    def update(self, signal):
        """Update control signals"""
        IntegrateAndFireNeuron.update(self, - signal - self.b * self.v)
        self.v += self.h * (- self.v + self.y) / self.T
