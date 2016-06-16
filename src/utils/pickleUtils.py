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
# April 2016
##

import os
import pickle
import logging


class PickleUtils:
    """
    Utility class to manipulate files using pickle
    """

    def __init__(self):
        """Class initialization"""

    @staticmethod
    def save(filename, element):
        """
        Save a elements into a file
        :param filename: String path to the file
        :param element: Content to store in the file
        """

        with open(filename, 'wb') as f:
            pickle.dump(element, f, protocol=2)

    @staticmethod
    def load(filename):
        """
        Load the result dictionary from file
        :param filename: String path to the file
        :return: Dictionary containing the content of the file
        """

        if os.path.isfile(filename):
            try:
                f = open(filename, 'rb')
                result_dict = pickle.load(f)
                f.close()
                return result_dict
            except Exception as e:
                logging.error("Can't load save file: " + str(e))

        else:
            logging.error("Can't open the file " + str(filename) + ". The file doesn't exist.")
        return {}

    @staticmethod
    def del_file(filename):
        """
        Delete a file if possible
        :param filename: String path to the file
        """

        if os.path.isfile(filename):
            try:
                os.remove(filename)
            except Exception as e:
                logging.error("Can't delete save file: " + str(e))

        else:
            logging.error("Can't find the file " + str(filename) + ". The file doesn't exist.")

    @staticmethod
    def del_all_files(directory, extension):
        """
        Delete a list of files if possible
        :param directory: String path to the directory containing the files
        :param extension: String extension of the files. Should start with a dot.
        """

        for file_ in os.listdir(directory):
            if file_.endswith("." + extension):
                PickleUtils.del_file(file_)
