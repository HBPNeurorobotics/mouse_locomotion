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
# April 2016
##


class Observer:
    """
    Observer/Observable pattern
    Observer Class is notified by Observable for an update
    """

    def __init__(self):
        """Class initialization"""

    def update(self, **kwargs):
        """
        Update function called by Observable
        :param kwargs: Dictionary parameter for the update
        """
