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


from plumbum.cli import SwitchAttr, Flag
from simulations import Manager
from simulations.launchers import DEF_OPT

from .launcher import Launcher
from .serverLauncher import ServerLauncher


class ClientLauncher(ServerLauncher):
    """
    Class to launch Client simulations.
    Usage:
            ClientLauncher.run()
    """

    # Simulation parameters
    sim_type = SwitchAttr(["-t", "--type"], str, default=DEF_OPT["sim_type"],
                          help="Specify the type of simulation: RUN, META_GA or CM")
    sim_timeout = SwitchAttr(["-T", "--timeout"], str, default=DEF_OPT["timeout"],
                             help="Maximum duration for the simulation")
    local = Flag(["-l"], default=DEF_OPT["local"],
                 help="Start a single local simulation. Used to bypass simulation distributed architecture")

    # Save and load config
    save = Flag(["-S"], default=False,
                help="Save the best individual at the end of sim")
    load_file = SwitchAttr(["-L"], str, default=False,
                           help="Start a single local simulation using result file")

    def __init__(self, executable):
        self.thread_name = "Locomotion_Client_Thread"
        Launcher.__init__(self, executable)

    def build_opt(self):
        """
        Build a dictionary with all the parameters required for the simulation
        :return: Dictionary of the parameters
        """

        opt = ServerLauncher.build_opt(self).copy()
        opt["sim_type"] = self.sim_type
        opt["local"] = self.local
        opt["load_file"] = self.load_file
        opt["save"] = self.save
        opt["timeout"] = self.sim_timeout
        return opt

    def main(self, *args):
        """
        Launch a Manager simulation
        :param args: see cli.Application
        """

        Launcher.main(self)
        s = Manager(self.build_opt().copy())
        s.start()
