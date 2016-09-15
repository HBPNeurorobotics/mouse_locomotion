#!/usr/bin/python2

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

import datetime
import time
import logging
import os
import subprocess
import sys
from multiprocessing import Process
from result import Result

if sys.version_info <= (3, 0):
    import psutil  # TODO: Find another lib


class Simulator:
    """
    Abstract Simulator class provides tools and abstract functions to implement different simulators
    to process simulations
    """

    def __init__(self, opt):
        """
        Class initialization
        :param opt: Dictionary containing simulation parameters
        """

        self.args = []
        self.dirname = opt["root_dir"] + "/save"
        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)
        self.filename = ""
        self.update_filename()
        self.simulator_path = opt["simulator_path"]
        self.model = opt["model"]
        self.config = opt["config_name"]
        self.logfile = opt["logfile"]
        self.genome = opt["genome"] if "genome" in opt else None

    def update_filename(self):
        """Update the save file name to the current datetime"""

        self.filename = "sim_" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f") + ".qsm"
        self.filename = self.dirname + "/" + self.filename

    @staticmethod
    def launch_simulation(args):
        """Launch a simulation subprocess"""

        logging.debug("Subprocess call: " + str(args))
        try:
            subprocess.call(args)
        except KeyboardInterrupt:
            logging.warning("Keyboard interruption during simulation")
        logging.debug("Subprocess end")

    def get_results(self):
        """
        This function reads the file saved by the simulator at the end of the simulation to retrieve results
        :return: Dictionary containing simulation results
        """

        # Retrieve filename
        res = Result()
        results = res.get_results(self.filename)
        return results

    def test_simulator(self):
        """
        Test a normal simulation and retrieve its results and its cpu and memory consumption
        :return: Dictionary containing simulation results and mean cpu and memory consumption
        """

        test = Process(target=self.launch_simulation)
        test.daemon = True
        cpu_consumption = []
        memory_consumption = []
        results = {}
        try:
            # Launch the simulation in a subprocess so we can know its cpu and memory usage
            test.start()
            proc = psutil.Process(test.pid)

            while proc.status() != psutil.STATUS_ZOMBIE and proc.status() != psutil.STATUS_DEAD:
                cpu_consumption.append(sum(psutil.cpu_percent(interval=0.5, percpu=True)) / psutil.cpu_count())
                memory_consumption.append(psutil.virtual_memory().percent)
                time.sleep(0.1)
            test.join()
        except psutil.NoSuchProcess as ex:
            logging.debug("Test simulation stopped correctly.")
        except KeyboardInterrupt as k:
            logging.error("Keyboard interruption during test simulation")
            results["interruption"] = True
        except Exception as e:
            logging.error("Error during the simlator test : " + str(e))
        results["CPU"] = 0. if len(cpu_consumption) <= 0 else max(cpu_consumption)
        results["memory"] = 0. if len(memory_consumption) <= 0 else max(memory_consumption)
        logging.info("Test Simulator " + self.__class__.__name__ +
                     ": \nCPU = " + str(cpu_consumption) +
                     "\nMemory = " + str(memory_consumption))
        return results
