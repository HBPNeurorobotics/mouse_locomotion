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


from plumbum.cli import Flag, SwitchAttr
from simulations import SimServer
from simulations.launchers import DEF_OPT

from .launcher import Launcher


class ServerLauncher(Launcher):
    """
    Class to launch server simulations.
    Usage:
            ServerLauncher.run()
    """

    # Simulators parameters
    model = SwitchAttr(["-m", "--model"], str, default=DEF_OPT["model"],
                       help="Model to simulation")
    max_cpu_percentage = SwitchAttr(["-cpu", "--cpu_use"], str, default=None,
                                    help="Max CPU usage for the simulation server")
    max_memory_percentage = SwitchAttr(["-mem", "--mem_use"], str, default=None,
                                       help="Max memory usage for the simulation server")
    simulator = SwitchAttr(["-e", "--environment"], str, default=DEF_OPT["simulator"],
                           help="Simulator name : BLENDER")
    path = SwitchAttr(["-p", "--binpath"], str, default=DEF_OPT["simulator_path"],
                      help="Path of Simulator binaries. Relative path start with no /. " +
                               "To use PATH variable, check - p 'PATH'")
    config = SwitchAttr(["-c", "--config"], str, default=DEF_OPT["config_name"],
                        help="The config class to be used for simulation")
    fullscreen = Flag(["-f", "--fullscreen"], default=DEF_OPT["fullscreen"],
                      help="Enable fullscreen mode")

    def __init__(self, executable):
        self.thread_name = "Locomotion_Server_Thread"
        Launcher.__init__(self, executable)

    def build_opt(self):
        """
        Build a dictionary with all the parameters required for the simulation
        :return: Dictionary of the parameters
        """

        opt = Launcher.build_opt(self).copy()
        opt["simulator"] = self.simulator
        if self.path[0] == "/":
            opt["simulator_path"] = (self.path + "/")
        elif self.path == "PATH":
            opt["simulator_path"] = ""
        else:
            opt["simulator_path"] = self.root + "/" + self.path + "/"
        opt["model"] = self.root + "/mdl/" + self.model
        opt["config_name"] = self.root + "/configs/" + self.config + ".json"
        opt["fullscreen"] = self.fullscreen
        opt["cpu_use"] = self.max_cpu_percentage if self.max_cpu_percentage is not None else 50
        opt["memory_use"] = self.max_memory_percentage if self.max_memory_percentage is not None else 90
        return opt

    def main(self, *args):
        """
        Launch a SimServer simulation
        :param args: see cli.Application
        """

        Launcher.main(self)
        s = SimServer(self.build_opt().copy())
        s.start()
