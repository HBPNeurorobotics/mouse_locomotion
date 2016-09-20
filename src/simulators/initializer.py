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
# September 2016
##

import datetime
import time
import os
import sys
import logging.config

from config import Config
from musculoskeletals import Body
from utils import FileUtils


class Initializer:
    """
    Abstract Class used to initialize the brain and the body that will be used during simulation
    """

    def __init__(self, args):
        """Class initialization"""

        self.root = ""
        self.src = ""

        self.config_name = None
        self.log_file = None
        self.logger = None
        self.save_file = None

        self.genome = False
        self.body = None
        self.utility_class = None

        self.init_root()
        self.setup(args)
        self.create_model()
        self.advertise()

    def init_root(self):
        """Define the root directory for the program files"""

        self.root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))).replace("\\", "/")
        self.src = self.root + "/src"
        sys.path.append(self.src)

    def setup(self, argv):
        """
        Setup the parameters for the simulation. Create result folder and logger file.
        :param argv: Dictionary list of the parameters
        """

        self.config_name = argv[
            "config_name"] if "config_name" in argv else self.root + "/configs/default_dog_vert_simulation_config.json"
        self.log_file = argv[
            "logfile"] if "logfile" in argv else os.path.expanduser("~").replace("\\", "/") + "/.log/qSim.log"

        if "filename" in argv:
            self.save_file = argv["filename"]
        else:
            dirname = self.root + "/save"
            filename = "sim_" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f") + ".qsm"
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            self.save_file = dirname + "/" + filename

        self.genome = eval(argv["genome"]) if "genome" in argv else False

        FileUtils.create_file(self.log_file)

        logging.config.fileConfig(self.root + "/etc/logging.conf",
                                  defaults={'logfilename': self.log_file, 'simLevel': "DEBUG"})

    def setup_utility_class(self, config):
        """Set the utility class to get information from the simulator"""

        pass

    def create_model(self):
        """Initialize the models that will be used during simulation"""

        configuration = Config("Simulator", self.config_name)
        self.logger = configuration.logger
        configuration.save_path = self.save_file
        configuration.n_iter = 0
        configuration.t_init = time.time()
        if self.genome:
            configuration.set_conn_matrix(self.genome)

        self.body = Body(configuration, self.utility_class)

    def advertise(self):
        """Advertise simulation has begun"""

        self.logger.info("####################################")
        self.logger.info("##      Locomotion Simulation      #")
        self.logger.info("##   ---------------------------   #")
        self.logger.info("##                                 #")
        self.logger.info("##     Gabriel Urbain - UGent      #")
        self.logger.info("##     Dimitri RODARIE - HBP       #")
        self.logger.info("##              2016               #")
        self.logger.info("####################################\n")
