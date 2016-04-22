#!/usr/bin/python2

##
# Mouse Locomotion Simulation
# 
# This project provides the user with a framework based on Blender allowing:
#  - Creation and edition of a 3D model
#  - Design of a artificial neural network controller
#  - Offline optimization of the body parameters
#  - Online optimization of the brain controller
# 
# Copyright Gabriel Urbain <gabriel.urbain@ugent.be>. March 2016
# Data Science Lab - Ghent University. Human Brain Project SP10
##
import datetime
import fcntl
import logging
import os
import socket
import struct
import subprocess
import sys
import time

import net
import pickle
from rpyc.utils.registry import REGISTRY_PORT
from rpyc.utils.server import ThreadedServer


class Simulation:
    """
    Main class for high level simulation. It receives a set of simulation options as defined
    in the DEF_OPT dict. Methods start_service() and start_registry can be launched independently
    to run service and registry	servers. Other methods require a call to start_manager which
    distribute simulation accross the network.
    """

    def __init__(self, opt_=None):
        """Initialize with CLI options"""
        self.opt = opt_
        self.ipaddr = self.__get_ip_address('eth0')
        self.pid = os.getpid()

    def __get_ip_address(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            ip_name = socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', ifname[:15])
            )[20:24])
        except Exception as e:
            logging.warning("No ethernet connection!")
            ip_name = "localhost"

        return ip_name

    def start_service(self):
        """Start a service server"""

        logging.info("Start service server on address: " + str(self.ipaddr) + ":18861")
        self.t = ThreadedServer(net.SimService, port=18861, auto_register=True)
        self.t.start()

    def start_registry(self):
        """Start a registery server"""

        logging.info("Start registry server on address: " + str(self.ipaddr) + ":" + str(REGISTRY_PORT))
        self.r = net.SimRegistry()
        self.r.start()

    def start_manager(self):
        """Start a simulation manager"""

        self.t_sim_init = time.time()
        logging.info("Start sim manager server with PID " + str(self.pid))
        self.sm = net.SimManager()
        self.sm.start()
        time.sleep(1)

    def stop_manager(self):
        """Stop the simulation manager"""

        self.sm.stop()
        time.sleep(1)
        self.sim_time = time.time() - self.t_sim_init

    def run_sim(self):
        """Run a simple one shot simulation"""

        # Start manager
        self.start_manager()

        # Simulate
        sim_list = [self.opt]
        res_list = self.sm.simulate(sim_list)

        # Stop and disply results
        self.stop_manager()
        time.sleep(1)
        rs_ls = ""
        for i in res_list:
            rs_ls += str(i) + " "
        logging.info("Results: " + str(rs_ls))
        logging.info("Simulation Finished!")

    def brain_opti_sim(self):
        """Run an iterative simulation to optimize the muscles parameters"""

        # Set-up simulator options
        stop_loop = False
        n_iter = 0

        # Start manager
        self.start_manager()

        # Offline optimization loop
        while not stop_loop:

            # Create a population

            # Append the population to the sim list
            sim_list = [self.opt]

            # Run the simulation
            res_list = self.sm.simulate(sim_list)

            # Exit condition is triggered in main.py

            # Check cost function and modify config if needed
            if n_iter >= 0:
                stop_loop = True
            n_iter += 1

        # Stop and display results
        sys.stdout.write("Resultats: ")
        for i in res_list:
            sys.stdout.write(str(i) + " ")
        logging.info("Simulation Finished!")

    def muscle_opti_sim(self):
        """Run an iterative simulation to optimize the muscles parameters"""

        logging.error("This simulation is not implemented yet! Exiting...")


class BlenderSim:
    """
    Main class for low level simulation. It receives a set of simulation options as defined
    in the DEF_OPT dict. It can only start a simulation via a batch subprocess on localhost.
    """

    def __init__(self, opt_):
        """Initialize with  options"""

        self.opt = opt_
        self.dirname = self.opt["root_dir"] + "/save"
        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)

    def start_blenderplayer(self):
        """Call blenderplayer via command line subprocess"""

        # Fetch blender game engine standalone path
        args = [self.opt["blender_path"] + "blenderplayer"]

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

        # Start batch process and quit
        logging.debug("Subprocess call: " + str(args))
        subprocess.call(args)

    def start_blender_with_player(self):
        """Call blender via command line subprocess and start the game engine simulation"""

        # Fetch blender game engine standalone path
        args = [self.opt["blender_path"] + "blender"]

        # Add arguments to command line
        args.extend([self.opt["blender_model"]])
        args.extend(["--python", "ge.py"])
        args.extend(["--start_player()"])

        # Start batch process and quit
        logging.debug("Subprocess call: " + str(args))
        subprocess.call(args)

    def create_pop(self):
        """Call blender via command line subprocess and create a population out of a model"""

        # Fetch blender game engine standalone path
        args = [self.opt["blender_path"] + "blender"]

        # Add arguments to command line
        args.extend(["-b"])
        args.extend([self.opt["blender_model"]])
        args.extend(["--python", "model.py"])
        args.extend(["--create_pop()"])

        # Start batch process and quit
        logging.debug("Subprocess call: " + str(args))
        subprocess.call(args)

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
