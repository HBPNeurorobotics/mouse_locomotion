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

from ..simulator import Simulator


class Blender(Simulator):
    """
    Blender Class provides functions to call different blender simulations
    Usage:
                # Instantiate Blender Class
                blender = Blender(opt, type_="BLENDER")

                # Start blender simulation
                blender.launch_simulation()

    """

    ALIASES = {"BLENDER": "blender", "BLENDERPLAYER": "blenderplayer"}

    def __init__(self, opt, type_="BLENDERPLAYER"):
        """
        Class initialization
        :param opt: Dictionary containing simulation parameters
        :param type_: String type of simulation
        """

        Simulator.__init__(self, opt)
        self.type = type_
        self.fullscreen = opt["fullscreen"] if "fullscreen" in opt else False

    def launch_simulation(self):
        """Launch a Blender simulation depending on the type variable.
        List of the types are in the ALIASES dictionary."""

        if self.type in self.ALIASES:
            self.args = [self.simulator_path + self.ALIASES[self.type]]
            eval("self.start_" + self.ALIASES[self.type] + "()")
        else:
            self.create_pop()
        Simulator.launch_simulation(self.args)

    def start_blenderplayer(self):
        """Call blenderplayer via command line subprocess"""

        # Add arguments to command line
        self.args.extend([
            "-w", "1080", "600", "2000", "200",
            "-g", "show_framerate", "=", "1",
            "-g", "show_profile", "=", "1",
            "-g", "show_properties", "=", "1",
            "-g", "ignore_deprecation_warnings", "=", "0",
            "-d",
        ])

        self.update_filename()
        if self.fullscreen:
            self.args.extend(["-f"])
        self.args.extend([self.model])
        self.args.extend(["-"])
        params = {'config_name': self.config,
                  'logfile': str(self.logfile),
                  'filename': self.filename}
        if self.genome is not None:
            params["genome"] = str(self.genome)
        self.args.extend([str(params)])
        self.args.extend(["FROM_START.PY"])

    def start_blender(self):
        """Call blender via command line subprocess and start the game engine simulation"""

        # Add arguments to command line
        self.args.extend([self.model])
        self.args.extend(["--python", "ge.py"])
        self.args.extend(["--start_player()"])

    def create_pop(self):
        """Call blender via command line subprocess and create a population out of a model"""

        self.args = [self.simulator_path + "blender"]

        # Add arguments to command line
        self.args.extend(["-b"])
        self.args.extend([self.model])
        self.args.extend(["--python", "model.py"])
        self.args.extend(["--create_pop()"])
