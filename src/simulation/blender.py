import os
import datetime
import logging
import subprocess
import pickle
from simulation import Simulation


class Blender(Simulation):
    """
    Main class for low level simulation. It receives a set of simulation options as defined
    in the DEF_OPT dict. It can only start a simulation via a batch subprocess on localhost.
    """
    ALIASES = {"BLENDER": "blender", "BLENDERPLAYER": "blenderplayer"}

    def __init__(self, opt_, type_):
        """Initialize with  options"""
        Simulation.__init__(self, opt_)
        self.type = type_
        self.dirname = self.opt["root_dir"] + "/save"
        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)

    def start(self):
        Simulation.start(self)
        if self.type in self.ALIASES:
            args = [self.opt["blender_path"] + self.ALIASES[self.type]]
            eval("self.start_" + self.ALIASES[self.type] + "(args)")
            # Start batch process and quit
            logging.debug("Subprocess call: " + str(args))
            print(str(args))
            subprocess.call(args)
        else:
            self.create_pop()

    def start_blenderplayer(self, args):
        """Call blenderplayer via command line subprocess"""

        # Fetch blender game engine standalone path

        # Add arguments to command line
        args.extend([
            "-w", "1080", "600", "2000", "200",
            "-g", "show_framerate", "=", "1",
            "-g", "show_profile", "=", "1",
            "-g", "show_properties", "=", "1",
            "-g", "ignore_deprecation_warnings", "=", "0",
            "-d",
        ])

        filename = "sim_" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".qsm"
        self.opt["save_path"] = self.dirname + "/" + filename

        if self.opt["fullscreen"]:
            args.extend(["-f"])
        args.extend([self.opt["blender_model"]])
        args.extend(["-"])
        params = {'config_name': self.opt["config_name"] + "()",
                  'logfile': str(self.opt["logfile"]),
                  'filename': str(self.opt["save_path"])}
        args.extend([str(params)])
        args.extend(["FROM_START.PY"])

    def start_blender(self, args):
        """Call blender via command line subprocess and start the game engine simulation"""

        # Add arguments to command line
        args.extend([self.opt["blender_model"]])
        args.extend(["--python", "ge.py"])
        args.extend(["--start_player()"])

    def create_pop(self):
        """Call blender via command line subprocess and create a population out of a model"""
        args = [self.opt["blender_path"] + "blender"]
        # Add arguments to command line
        args.extend(["-b"])
        args.extend([self.opt["blender_model"]])
        args.extend(["--python", "model.py"])
        args.extend(["--create_pop()"])

    def get_results(self):
        """This function reads the file saved in Blender at the end of the simulation to retrieve results"""

        # Retrieve filename
        if not "save_path" in self.opt:
            results = "WARNING BlenderSim.get_results() : Nothing to show"
        elif os.path.isfile(self.opt["save_path"]):
            try:
                f = open(self.opt["save_path"], 'rb')
                results = pickle.load(f)
                f.close()
            except Exception as e:
                results = "Can't load save file : " + str(e)
                logging.error(results)
        else:
            results = "ERROR BlenderSim.get_results() : Can't open the file " + self.opt[
                "save_path"] + ".\nThe file doesn't exist."
        return results
