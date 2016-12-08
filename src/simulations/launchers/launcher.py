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
import sys
from os import makedirs, getpid, unlink
from os.path import dirname, exists, isfile

from plumbum.cli import Application, Flag, SwitchAttr
from simulations.launchers import DEF_OPT, ROOT


class Launcher(Application):
    """
    Abstract class to launch simulations. It parses the parameter from the user and launch a simulation afterwards
    """

    root = ROOT
    verbose = Flag(["-v", "--verbosemode"], default=False,
                   help="Set verbose mode")
    logfile = SwitchAttr(["--logfile"], str, default=DEF_OPT["logfile"],
                         help="The log file to use")
    device = SwitchAttr(["-d", "--device"], str, default=None,
                        help="Network device name")
    register_ip = SwitchAttr(["-i", "--ip"], str, default=None,
                             help="IP for the registry")
    thread_name = "Locomotion_Simulation_Thread"

    def __init__(self, executable):
        Application.__init__(self, executable)
        self.lock_file = dirname(self.logfile) + "/" + self.thread_name + ".pid"

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

    def __del__(self):
        if isfile(self.lock_file) and file(self.lock_file, 'r').read() == str(getpid()):
            unlink(self.lock_file)

    def main(self, *args):
        """
        Launch a Simulation after configuring logging
        :param args: see cli.Application
        """

        # Configure logging
        if not exists(dirname(self.logfile)):
            makedirs(dirname(self.logfile))
        if not exists(self.logfile):
            f = open(self.logfile, 'w')
            f.close()

        logging.config.fileConfig(ROOT + "/etc/logging.conf", defaults={'logfilename': self.logfile, 'simLevel': (
            "DEBUG" if self.verbose else "INFO")})

        if isfile(self.lock_file):
            logging.error("Either there is already another " + self.thread_name + " on this machine" +
                          " or a previous " + self.lock_file + " file was not removed. Abort.")
            sys.exit(1)
        file(self.lock_file, 'w').write(str(getpid()))
