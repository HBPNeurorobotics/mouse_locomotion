##        self.fiber = fiber
# Mouse Locomotion Simulation        self.fiber = fiber
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

from .muscleReceptor import MuscleReceptor


class GolgiTendon(MuscleReceptor):
    def __init__(self, muscle):
        MuscleReceptor.__init__(self, None, muscle)

    def update(self):
        return self.process_input(self.mesh.get_stretch())
