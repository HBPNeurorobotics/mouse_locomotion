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
# December 2016
##


from simulations import Registry

from .launcher import Launcher


class RegistryLauncher(Launcher):
    """
    Class to launch Registry simulations.
    Usage:
            RegistryLauncher.run()
    """

    def main(self, *args):
        """
        Launch a Registry simulation
        :param args: see cli.Application
        """

        Launcher.main(self, *args)
        s = Registry(self.build_opt())
        s.start()
