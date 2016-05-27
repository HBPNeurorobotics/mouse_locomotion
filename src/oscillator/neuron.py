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


class Neuron:
    def __init__(self):
        self.x = 0.
        self.y = 0.

    def reset(self):
        self.x = 0.
        self.y = 0.

    def update(self, signal):
        self.x += signal
        self.y = self.x
