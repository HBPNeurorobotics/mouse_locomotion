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


import logging
import os

from utils import JSonUtils


class Config:
    """Describe the configuration file to pass as an argument to a given simulation"""

    def __init__(self, filename=None):
        """Init default config parameters"""
        self.logger = logging.Logger("INFO")
        data = {} if filename is None else JSonUtils.read_json_file(filename, self.logger)
        if data == {}:
            self.logger.warning("The config is empty. You may have a problem with your config file.")
        # Simulation parameters
        self.name = data["name"] if "name" in data else ""
        self.sim_speed = data["sim_speed"] if "sim_speed" in data else 1.0
        self.logger_name = data["logger_name"] if "logger_name" in data else "INFO"
        self.logger = logging.Logger(self.logger_name)
        self.exit_condition = data["exit_condition"] if "exit_condition" in data else "owner['config'].n_iter > 500"
        self.timeout = data["timeout"] if "timeout" in data else 10
        self.save_path = data["save_path"] if "save_path" in data else "default"
        self.simulator = data["simulator"] if "simulator" in data else "Simulator"
        self.t_init = 0
        self.t_end = 0
        self.n_iter = 0

        # Physical parameters
        self.muscle_type = data["muscle_type"] if "muscle_type" in data else "DampedSpringReducedTorqueMuscle"
        self.back_leg_L_muscles = data["back_leg_L_muscles"] if "back_leg_L_muscles" in data else []
        self.back_leg_R_muscles = data["back_leg_R_muscles"] if "back_leg_R_muscles" in data else []
        self.front_leg_L_muscles = data["front_leg_L_muscles"] if "front_leg_L_muscles" in data else []
        self.front_leg_R_muscles = data["front_leg_R_muscles"] if "front_leg_R_muscles" in data else []
        self.brain = data["brain"] if "brain" in data else dict()
        self.body = data["body"] if "body" in data else dict()
        self.connection_matrix = data["connection_matrix"] if "connection_matrix" in data else dict()
        if self.connection_matrix == dict():
            self.config_connection_matrix()
        self.dist_ref = data["dist_ref"] if "dist_ref" in data else 20
        self.power_ref = data["dist_ref"] if "dist_ref" in data else 1000

    def set_conn_matrix(self, vector):
        """Fills the connection matrix between the brain and the muscles with a vector of values"""

        conn_size = len(self.connection_matrix) * self.brain["n_osc"]
        if len(vector) != conn_size:
            self.logger.error("Vector size (" + str(len(vector)) + ") should match with connection matrix " +
                              "size (" + str(
                conn_size) + "). Please use the self.get_matrix_size method to determine it!")
        else:
            i = 0
            for line in sorted(self.connection_matrix):
                for j in range(len(self.connection_matrix[line])):
                    self.connection_matrix[line][j] = vector[i]
                    i += 1

            self.logger.debug("Connection matrix updated: " + str(self.connection_matrix))

    def set_leg_conn_matrix(self, vector):
        """Fills the connection matrix between the brain and the muscles of the leg with a vector of values"""

        if len(vector) != self.get_conn_matrix_leg_len():
            self.logger.error("Vector size (" + str(len(vector)) + ") should match with connection matrix " +
                              "size (" + str(self.get_conn_matrix_leg_len()) +
                              "). Please use the self.get_matrix_size method to determine it!")
        else:
            i = 0
            for line in sorted(self.connection_matrix):
                if line == "B_biceps.L" or line == "B_biceps.R" \
                    or line == "F_biceps.L" or line == "F_biceps.R" \
                    or line == "B_triceps.L" or line == "B_triceps.R" \
                    or line == "F_triceps.L" or line == "F_triceps.R" \
                    or line == "B_gastro.L" or line == "B_gastro.R" \
                    or line == "F_gastro.L" or line == "F_gastro.R":
                        for j in range(len(self.connection_matrix[line])):
                            self.connection_matrix[line][j] = vector[i]
                            i += 1

            self.logger.debug("Connection matrix updated for leg: " + str(self.connection_matrix))

    def get_conn_matrix_vector(self):
        """Return the matrix in form of a vector"""

        vect = []
        for line in sorted(self.connection_matrix):
            for item in self.connection_matrix[line]:
                vect.append(item)

        return vect

    def str_conn_matrix(self):
        """Print the connection matrix"""

        st = 'Connection Matrix:\n'
        for line in self.connection_matrix:
            st += line + "= [ "
            for j in range(len(self.connection_matrix[line])):
                st += str(self.connection_matrix[line][j]) + " "

            st += "],  "

        return st

    def get_conn_matrix_len(self):
        """Return the total size (lines x columns) of the connection matrix"""

        return len(self.connection_matrix) * self.brain["n_osc"]

    def get_conn_matrix_leg_len(self):
        """Return the size (lines x columns) of the connection matrix for legs"""

        return 12 * self.brain["n_osc"]

    def config_connection_matrix(self):
        # Fill default connection matrix
        if "muscles" in self.body:
            for m in self.body["muscles"]:
                self.connection_matrix[m["name"]] = []
                for i in range(self.brain["n_osc"]):
                    self.connection_matrix[m["name"]].append(0)

        for m in self.front_leg_L_muscles:
            self.connection_matrix[m["name"]] = []
            for i in range(self.brain["n_osc"]):
                if m["name"] == "F_biceps.L" and i == 1:
                    self.connection_matrix[m["name"]].append(1)
                else:
                    self.connection_matrix[m["name"]].append(0)

        for m in self.front_leg_R_muscles:
            self.connection_matrix[m["name"]] = []
            for i in range(self.brain["n_osc"]):
                if m["name"] == "F_biceps.R" and i == 1:
                    self.connection_matrix[m["name"]].append(1)
                else:
                    self.connection_matrix[m["name"]].append(0)

        for m in self.back_leg_L_muscles:
            self.connection_matrix[m["name"]] = []
            for i in range(self.brain["n_osc"]):
                if m["name"] == "B_biceps.L" and i == 2:
                    self.connection_matrix[m["name"]].append(1)
                elif m["name"] == "B_gastro.L" and i == 2:
                    self.connection_matrix[m["name"]].append(1)
                else:
                    self.connection_matrix[m["name"]].append(0)

        for m in self.back_leg_R_muscles:
            self.connection_matrix[m["name"]] = []
            for i in range(self.brain["n_osc"]):
                if m["name"] == "B_biceps.R" and i == 2:
                    self.connection_matrix[m["name"]].append(1)
                elif m["name"] == "B_gastro.R" and i == 2:
                    self.connection_matrix[m["name"]].append(1)
                else:
                    self.connection_matrix[m["name"]].append(0)

    def save_config(self, directory_name=None, filename=None):
        dirname_ = "" if directory_name is None else directory_name
        if dirname_ != "" and not os.path.exists(dirname_):
            os.makedirs(dirname_)

        filename_ = self.name if filename is None else filename
        filename_ = dirname_ + "/" + filename_ + ".json"
        data = self.__dict__
        del data["logger"]
        del data["t_init"]
        del data["t_end"]
        del data["n_iter"]

        JSonUtils.write_json_file(filename_, data)
