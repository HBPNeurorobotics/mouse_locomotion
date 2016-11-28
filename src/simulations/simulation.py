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
# February 2016
##

import logging
import netifaces
import os
import socket


class Simulation:
    """
    Abstract class for high level simulation. It receives a set of simulation options as defined
    in the DEF_OPT dict.
    """

    def __init__(self, opt_=None):
        """
        Initialize with CLI options
        :param opt_: Dictionary containing simulation parameters
        """

        logging.info("Create a " + self.__class__.__name__ + " instance.\n")
        self.opt = opt_

        # Get a connected device IP
        self.device = None
        if self.opt is not None:
            self.device = self.opt['device'] if 'device' in self.opt else None
        self.ipaddr = self.get_ip_address(self.device) if os.name == 'posix' else socket.gethostbyname(
            socket.gethostname())

        self.pid = os.getpid()
        self.save_directory = self.opt["root_dir"] + "/save/"
        self.port = 0

    @staticmethod
    def get_ip_address(ifname=None):
        """
        Retrieve machine ip address
        :param ifname: String name of the network device
        :return: String machine ip
        """

        devices = filter(lambda x: 2 in netifaces.ifaddresses(x)
                                   and 10 in netifaces.ifaddresses(x)
                                   and 'broadcast' in netifaces.ifaddresses(x)[2][0],
                         netifaces.interfaces())
        if len(devices) > 0:
            device = devices[0]
            if ifname is not None and ifname in devices:
                device = devices[ifname]
            elif ifname is not None:
                logging.warning("The device " + str(ifname) + " is not connected.")
            ip_name = netifaces.ifaddresses(device)[2][0]['addr']
        else:
            logging.warning("No device connected to a network. Work in localhost")
            ip_name = "0.0.0.0"
        return ip_name

    def start(self):
        """Start the simulation process"""
        port = (":" + str(self.port)) if self.port != 0 else ""
        logging.info(
            "Start " + self.__class__.__name__ + " on address: " +
            str(self.ipaddr if self.ipaddr != "0.0.0.0" else "localhost") +
            port + " with PID " + str(self.pid))

    def stop(self):
        """Stop the simulation process"""
        logging.info(self.__class__.__name__ + " has terminated properly.")
