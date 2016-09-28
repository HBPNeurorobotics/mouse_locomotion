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
# August 2016
##
import logging

import numpy
import os
from utils.fileUtils import FileUtils


class NumpyUtils(FileUtils):
    """
        Utility class to manipulate files using numpy
    """

    def __init__(self):
        """Class initialization"""
        FileUtils.__init__(self)

    @staticmethod
    def write_file(filename, element):
        """
        Save a elements into a file
        :param filename: String path to the file
        :param element: Content to store in the file
        """

        numpy.save(filename, element)

    @staticmethod
    def read_file(filename):
        """
        Load the result dictionary from file
        :param filename: String path to the file
        :return: Dictionary containing the content of the file
        """
        if not filename.endswith(".npy"):
            filename += ".npy"
        if os.path.isfile(filename):
            try:
                f = open(filename, 'rb')
                result_dict = numpy.load(filename)
                f.close()
                return result_dict
            except Exception as e:
                logging.error("Can't load saved file: " + str(e))

        else:
            logging.error("Can't open the file " + str(filename) + ". The file doesn't exist.")
        return {}
