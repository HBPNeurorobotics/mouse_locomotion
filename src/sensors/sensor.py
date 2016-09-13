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
# June 2016
##


class Sensor:
    def __init__(self, simulator, mesh):
        self.simulator = simulator
        self.mesh = mesh
        self.signal = 0.
        self.rec = []

    def update(self):
        pass

    def process_input(self, inputs_):
        self.signal = sum(inputs_)
        self.rec.append(self.signal)
        return self.signal
