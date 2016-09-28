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
# File created by: Gabriel Urbain <gabriel.urbain@ugent.be>
#                  Dimitri Rodarie <d.rodarie@gmail.com>
# June 2016
##

import json
import os
import logging

from utils.fileUtils import FileUtils


class JsonUtils(FileUtils):
    """
    Utility class to manipulate json files
    """

    def __init__(self):
        """Class initialization"""
        FileUtils.__init__(self)

    @staticmethod
    def read_file(filename):
        """
        Read json file if exists and return its content as a dictionary
        :param filename: String path to the json file
        :return: Dictionary of the json content
        """

        if os.path.isfile(filename):
            try:
                with open(filename, 'r') as data_file:
                    return json.load(data_file)
            except Exception as e:
                logging.error("Can't load saved file: " + str(e))

        else:
            logging.error("Can't open the file " + str(filename) + ". The file doesn't exist.")
        return {}

    @staticmethod
    def write_file(filename, data):
        """
        Write down data on a json file
        :param filename: String path to the json file
        :param data: Dictionary containing the data to store
        """

        with open(filename, 'w') as f:
            json.dump(data, f)
