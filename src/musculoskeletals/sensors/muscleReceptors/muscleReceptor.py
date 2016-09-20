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

from ..sensor import Sensor


class MuscleReceptor(Sensor):
    def __init__(self, simulator, mesh):
        Sensor.__init__(self, simulator, mesh)

    def update(self):
        pass

    def process_input(self, inputs_):
        return sum(inputs_)
