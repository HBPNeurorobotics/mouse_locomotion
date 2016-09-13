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

from .sensor import Sensor
import numpy as np


class Vestibular(Sensor):
    def __init__(self, simulator, mesh="obj_head"):
        Sensor.__init__(self, simulator, mesh)

    def update(self):
        return self.process_input(self.simulator.get_orientation(self.mesh))

    def process_input(self, inputs_):
        self.signal = inputs_
        self.rec.append(self.signal)
        return self.signal

    def get_stability(self):
        res = []
        for result in self.rec:
            res.append((np.rad2deg(result.x + result.y) / 2))
        return abs(sum(res) / len(res))
