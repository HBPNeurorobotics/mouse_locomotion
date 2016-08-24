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

from utils.fileUtils import FileUtils


class PickleUtils(FileUtils):
    """
    Utility class to manipulate files using pickle
    """

    def __init__(self):
        """Class initialization"""

    @staticmethod
    def write_file(filename, element):
        """
        Save a elements into a file
        :param filename: String path to the file
        :param element: Content to store in the file
        """

        with open(filename, 'wb') as f:
            pickle.dump(element, f, protocol=2)

    @staticmethod
    def read_file(filename):
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


if __name__ == "__main__":

    directory = "/home/rodarie/Documents/mouse_locomotion/save/"
    max_ = 0.
    for file_ in os.listdir(directory):
        if file_.startswith("GeneticMeta"):
            dict_ = PickleUtils.read_file(directory + file_)
            for optimization in range(len(dict_["configs"])):
                max_i = 0.
                for i in range(len(dict_["configs"][optimization])):
                    current_max = max(dict_["scores"][optimization][i])
                    if current_max > max_:
                        max_ = current_max
                    if current_max > max_i:
                        max_i = current_max
                        PickleUtils.write_file(directory + "best_solution_" + str(optimization) + ".gene",
                                               dict_["configs"][optimization][i][
                                                   dict_["scores"][optimization][i].index(current_max)])

                print(max_)

if __name__ == "__main2__":
    directory = "/home/rodarie/Documents/mouse_locomotion/save/"
    max_ = 0.

    for file_ in os.listdir(directory):
        if file_.endswith(".sim"):
            dict_ = PickleUtils.read_file(directory + file_)
            for i in range(len(dict_["configs"])):
                current_max = max(dict_["res"][i])
                if current_max > max_:
                    max_ = current_max
                    PickleUtils.write_file(directory + "best_solution.gene",
                                           dict_["configs"][i][dict_["res"][i].index(current_max)])

            print(max_)
