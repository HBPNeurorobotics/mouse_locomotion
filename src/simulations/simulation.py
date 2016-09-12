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

import os
import logging
import socket
import struct

if os.name == 'posix':
    import fcntl


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

        self.opt = opt_
        if os.name == 'posix':
            self.ipaddr = self.__get_ip_address('eth0')
        else:
            self.ipaddr = socket.gethostbyname(socket.gethostname())
        self.pid = os.getpid()
        self.save_directory = self.opt["root_dir"] + "/save/"

    @staticmethod
    def __get_ip_address(ifname):
        """
        Retrieve machine ip address
        :param ifname: String name of the network device
        :return: String machine ip
        """

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
        """Start the simulation process"""

    def stop(self):
        """Stop the simulation process"""
