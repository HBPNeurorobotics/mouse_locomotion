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
# File created by: Gabriel Urbain <gabriel.urbain@ugent.be>. March 2016
# Modified by: Dimitri Rodarie
##

import os
import logging
import socket
import struct
from simulator import *

if os.name == 'posix':
    import fcntl


class Simulation:
    """
    Main class for high level simulation. It receives a set of simulation options as defined
    in the DEF_OPT dict. Methods start_service() and start_registry can be launched independently
    to run service and registry	servers. Other methods require a call to start_manager which
    distribute simulation across the network.
    """

    SIMULATORS = {"BLENDER": "Blender"}
    DEFAULT_SIMULATOR = "BLENDER"

    def __init__(self, opt_=None):
        """Initialize with CLI options"""
        self.opt = opt_
        self.results = "No results yet : No simulation launched"
        if type(self.opt) == dict and "simulator" in self.opt:
            simulator_ = self.opt["simulator"]
            if simulator_ not in self.SIMULATORS:
                simulator_ = self.DEFAULT_SIMULATOR
        else:
            simulator_ = self.DEFAULT_SIMULATOR
        self.simulator = self.SIMULATORS[simulator_] + "(self.opt)"
        if os.name == 'posix':
            self.ipaddr = self.__get_ip_address('eth0')
        else:
            self.ipaddr = socket.gethostbyname(socket.gethostname())
        self.pid = os.getpid()

    @staticmethod
    def __get_ip_address(ifname):
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

    def start(self):
        simulator_ = eval(self.simulator)
        simulator_.launch_simulation()
        self.results = simulator_.get_results()

    def stop(self):
        pass

    def get_results(self):
        return self.results
