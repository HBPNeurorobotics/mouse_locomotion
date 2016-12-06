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


import logging.config
import os.path

from plumbum import cli
from simulations.launchers import DEF_OPT, ROOT


class Launcher(cli.Application):
    """
    Abstract class to launch simulations. It parses the parameter from the user and launch a simulation afterwards
    """

    root = ROOT
    verbose = cli.Flag(["-v", "--verbosemode"], default=False,
                       help="Set verbose mode")
    logfile = cli.SwitchAttr(["--logfile"], str, default=DEF_OPT["logfile"],
                             help="The log file to use")
    device = cli.SwitchAttr(["-d", "--device"], str, default=None,
                            help="Network device name")
    register_ip = cli.SwitchAttr(["-i", "--ip"], str, default=None,
                                 help="IP for the registry")

    def build_opt(self):
        """
        Build a dictionary with all the parameters required for the simulation
        :return: Dictionary of the parameters
        """

        return {"root_dir": self.root,
                "verbose": self.verbose,
                "logfile": self.logfile,
                "device": self.device,
                "register_ip": self.register_ip}

    def main(self, *args):
        """
        Launch a Simulation after configuring logging
        :param args: see cli.Application
        """

        # Configure logging
        if not os.path.exists(os.path.dirname(self.logfile)):
            os.makedirs(os.path.dirname(self.logfile))
        if not os.path.exists(self.logfile):
            f = open(self.logfile, 'w')
            f.close()

        logging.config.fileConfig(ROOT + "/etc/logging.conf", defaults={'logfilename': self.logfile, 'simLevel': (
            "DEBUG" if self.verbose else "INFO")})
