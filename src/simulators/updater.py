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
import logging.config
import os
import sys
import time

from config import Config
from musculoskeletals import Body
from result import Result
from utils import FileUtils


class Updater:
    """
    Class used to update the brain and the body at each time step during simulation
    """

    def __init__(self, args):
        """Class initialization"""
        self.root = ""
        self.src = ""

        self.config_name = None
        self.logger = None
        self.save_file = None

        self.genome = False
        self.body = None
        self.config = None
        self.utility_class = None

        self.init_root()
        self.setup(args)
        self.setup_utility_class()
        self.create_model()
        self.advertise()

        self.penalty = False

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
        log_file = argv[
            "logfile"] if "logfile" in argv else os.path.expanduser("~").replace("\\", "/") + "/.log/locomotionSim.log"

        if "filename" in argv:
            self.save_file = argv["filename"]
        else:
            dirname = self.root + "/save"
            filename = "sim_" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f") + ".qsm"
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            self.save_file = dirname + "/" + filename

        self.genome = eval(argv["genome"]) if "genome" in argv else False

        FileUtils.create_file(log_file)

        logging.config.fileConfig(self.root + "/etc/logging.conf",
                                  defaults={'logfilename': log_file, 'simLevel': "DEBUG"})

    def setup_utility_class(self):
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
        self.config = self.body.config

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

    def update(self):
        """
        Update the brain and the body.
        Test the exit condition and stop simulation if it is True.
        """

        brain_signal = self.body.get_brain_output()
        self.penalty = self.body.update(brain_signal)
        self.config.n_iter += 1

        self.logger.debug("Main iteration " + str(self.config.n_iter) + ": stop state = " +
                          str(eval(self.config.exit_condition)))

        if self.exit_condition():
            self.exit()

    def exit_condition(self):
        """
        Test if the simulation exit_condition is True or if the simulation is over or if the model got a penalty.
        :return: Boolean result of the test
        """

        return eval(self.config.exit_condition) \
               or time.time() - self.config.t_init > self.config.timeout \
               or self.penalty

    def exit(self):
        """Exit the simulation and create a result file"""

        self.logger.debug("Interruption: exit = " + str(eval(self.config.exit_condition)) +
                          " sim time = " + str(time.time() - self.config.t_init) + " timeout = " + str(
            self.config.timeout))
        self.config.t_end = time.time()

        # Create a result instance and save
        try:
            results = Result(self.body)
            self.logger.info(results)
            results.save_results()
        except Exception as e:
            self.logger.error("Unable to create a result report. Caused by: " + str(e))
            pass
