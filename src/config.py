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
import os
from utils import JsonUtils


class Config:
    """Describe the configuration file to pass as an argument to a given simulation"""

    def __init__(self, simulator, filename=None):
        """
        Init default config parameters
        :param filename: String path to the config file
        """

        data = {} if filename is None else JsonUtils.read_file(filename)
        if data == {}:
            self.logger.warning("The config is empty. You may have a problem with your config file.")
        # Simulation parameters
        self.name = data["name"] if "name" in data else ""
        self.sim_speed = data["sim_speed"] if "sim_speed" in data else 1.0
        self.logger_name = data["logger_name"] if "logger_name" in data else "INFO"
        self.logger = logging.Logger(self.logger_name)
        self.exit_condition = data["exit_condition"] if "exit_condition" in data else "owner['config'].n_iter > 500"
        self.timeout = data["timeout"] if "timeout" in data else 10
        self.simulator = simulator
        self.t_init = 0
        self.t_end = 0
        self.n_iter = 0

        # Physical parameters
        self.body = data["body"] if "body" in data else dict()
        self.legs = data["legs"] if "legs" in data else []
        self.brain = data["brain"] if "brain" in data else dict()
        self.connection_matrix = data["connection_matrix"] if "connection_matrix" in data else dict()
        if self.connection_matrix == dict():
            self.config_connection_matrix()
        self.dist_ref = data["dist_ref"] if "dist_ref" in data else 20
        self.power_ref = data["dist_ref"] if "dist_ref" in data else 1000

    def get_leg_config(self, name):
        if name in self.legs:
            dict_ = {"logger": self.logger, "connection_matrix": self.connection_matrix}
            dict_.update(self.legs[name])
            if "muscle_type" not in dict_:
                dict_["muscle_type"] = "DampedSpringMuscle"
            return dict_

    def set_conn_matrix(self, vector):
        """
        Fills the connection matrix between the brain and the muscles with a vector of values
        :param vector: List of Float values to set the connection matrix for the legs muscles
        """

        if len(vector) != self.get_conn_matrix_len():
            self.logger.error("Vector size (" + str(len(vector)) + ") should match with connection matrix " +
                              "size (" + str(self.get_conn_matrix_len()) +
                              "). Please use the self.get_matrix_len method to determine it!")
        else:
            for line in sorted(self.connection_matrix):
                for j in range(len(self.connection_matrix[line])):
                    self.connection_matrix[line][j] = vector[j]

            self.logger.debug("Connection matrix updated: " + str(self.connection_matrix))

    def get_conn_matrix_vector(self):
        """
        Return the matrix in form of a vector
        :return: List of List of Float connection matrix
        """

        vect = []
        for line in sorted(self.connection_matrix):
            for item in self.connection_matrix[line]:
                vect.append(item)

        return vect

    def str_conn_matrix(self):
        """
        Print the connection matrix
        :return: String representing the matrix
        """

        st = 'Connection Matrix:\n'
        for line in self.connection_matrix:
            st += line + "= [ "
            for j in range(len(self.connection_matrix[line])):
                st += str(self.connection_matrix[line][j]) + " "

            st += "],  "

        return st

    def get_conn_matrix_len(self):
        """
        Return the total size (lines x columns) of the connection matrix
        :return: Int connection matrix length
        """

        return len(self.connection_matrix) * self.brain["n_osc"]

    def config_connection_matrix(self):
        """Fill default connection matrix"""
        for leg in self.legs.values():
            for m in leg["muscles"]:
                if "brain_sig" and "name" in m:
                    self.connection_matrix[m["name"]] = [0] * self.brain["n_osc"]
                    self.connection_matrix[m["name"]][m["brain_sig"] - 1] = 1.

    def save_config(self, directory_name=None, filename=None):
        """Save the current config into a json file"""

        dirname_ = "" if directory_name is None else directory_name
        if dirname_ != "" and not os.path.exists(dirname_):
            os.makedirs(dirname_)

        filename_ = self.name if filename is None else filename
        filename_ = dirname_ + "/" + filename_ + ".json"
        data = self.__dict__
        # Delete useless parameters
        del data["logger"]
        del data["t_init"]
        del data["t_end"]
        del data["n_iter"]

        JsonUtils.write_file(filename_, data)
