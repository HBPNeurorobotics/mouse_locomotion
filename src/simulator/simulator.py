#!/usr/bin/python2

##
# Mouse Locomotion Simulation
#
# Human Brain Project SP10
#
# This project provides the user with a framework based on Blender allowing:
#  - Edition of a 3D model
#  - Edition of a physical controller model (torque-based or muscle-based)
#  - Edition of a brain controller model (oscillator-based or neural network-based)
#  - Simulation of the model
#  - Optimization of the parameters in distributed cloud simulations
#
# File created by: Gabriel Urbain <gabriel.urbain@ugent.be>. February 2016
# Modified by: Dimitri Rodarie
##
import datetime
import time
import logging
import os
import subprocess
from multiprocessing import Process

import psutil

from result import Result


class Simulator:
    def __init__(self, opt):
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
        self.filename = "sim_" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".qsm"
        self.filename = self.dirname + "/" + self.filename

    @staticmethod
    def launch_simulation(args):
        # Start batch process and quit
        logging.debug("Subprocess call: " + str(args))
        subprocess.call(args)
        logging.debug("Subprocess end")

    def get_results(self):
        """This function reads the file saved by the simulator at the end of the simulation to retrieve results"""
        # Retrieve filename
        res = Result()
        results = res.get_results(self.filename)
        return results

    def test_simulator(self):
        test = Process(target=self.launch_simulation)
        test.daemon = True
        cpu_consumption = []
        memory_consumption = []
        try:
            test.start()
            proc = psutil.Process(test.pid)
            processes = [psutil.Process(os.getpid()), proc]
            time.sleep(1)
            for child in proc.children(recursive=True):
                processes.append(child)
            while proc.status() != psutil.STATUS_ZOMBIE and proc.status() != psutil.STATUS_DEAD:
                cpu_consumption.append(sum(map(lambda x: x.cpu_percent(interval=0.1), processes)) / psutil.cpu_count())
                memory_consumption.append(sum(map(lambda x: x.memory_percent(), processes)))
                time.sleep(0.1)
            test.join()
        except psutil.NoSuchProcess as ex:
            # Simulation interrupted before the end of the parent process.
            # Remove useless values due to the interruption
            if cpu_consumption[-1] == 0.:
                del cpu_consumption[-1]
            if memory_consumption[-1] == 0.:
                del memory_consumption[-1]
        except Exception as e:
            logging.error("Error during the simlator test : " + str(e))
        logging.info("Test Simulator " + self.__class__.__name__ +
                     ": \nCPU = " + str(cpu_consumption) +
                     "\nMemory = " + str(memory_consumption))

        res = Result()
        return {"CPU": 0. if len(cpu_consumption) <= 0 else sum(cpu_consumption) / float(len(cpu_consumption)),
                "memory": 0. if len(memory_consumption) <= 0 else sum(memory_consumption) / float(
                    len(memory_consumption)), "result": res.get_results(self.filename)}
