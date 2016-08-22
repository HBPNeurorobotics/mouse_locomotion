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
# April 2016
##

import logging
from utils import PickleUtils


class Result:
    """This class is called at the end of a Blender simulation. It collects the simulation results from Blender, and
    from the different classes of this project. It also provides method to save, display and load the results (usefull
    inside an optimization algorithm). It takes a Config class as a initialization argument to determine which
    parameters shall be saved"""

    def __init__(self, body_=None):
        """
        Initialize the class with a body instance
        :param body_: Body class to save
        """

        if body_:
            self.void = False
            self.body = body_
            self.config = self.body.config
            self.logger = self.config.logger

        else:
            self.void = True
            self.body = None
            self.config = None
            self.logger = logging

        self.result_dict = dict()
        
        return

    def fill_report(self):
        """Compute key values to report the simulation results"""

        # Time features
        self.result_dict["t_end"] = self.config.t_end
        self.result_dict["t_init"] = self.config.t_init
        self.result_dict["t_sim"] = self.result_dict["t_end"] - self.result_dict["t_init"]
        self.result_dict["t_out"] = self.config.timeout

        try:
            test = eval(self.config.exit_condition)
        except Exception:
            test = False

        if self.result_dict["t_sim"] > self.result_dict["t_out"]:
            self.result_dict["stop"] = "Timeout"
        elif test:
            self.result_dict["stop"] = "Config exit condition"
        else:
            self.result_dict["stop"] = "User interruption"

        # Simulator features
        self.result_dict["simulator"] = "Blender"
        self.result_dict["sim_speed"] = self.config.sim_speed

        # Optimization features
        self.result_dict["score"] = self.body.get_loss_fct()

        # Config  features
        self.result_dict["config_name"] = self.config.name
        self.result_dict["config_opt"] = None  # TODO: fill here!
        # self.result_dict["config_muscles"] = self.config.muscle_type

    def save_results(self):
        """Save the results dictionary"""

        # Compute report if initialized with body and config
        if self.body:
            self.fill_report()

        # Save when not empty
        if self.result_dict:
            PickleUtils.write_file(self.config.save_path, self.result_dict)
            self.void = True

        else:
            self.logger.error("This result dictionary is currently empty. First load some results before saving.")

    def get_results(self, filename=None, to_delete=True):
        """
        Return the results dictionary
        :param to_delete: Boolean depending if the file will be deleted
        :param filename: String path to the file
        :return: Dictionary containing the content of the file
        """

        if filename:
            self.result_dict = PickleUtils.read_file(filename)
            if to_delete:
                PickleUtils.del_file(filename)
        return self.result_dict

    def __str__(self):
        """
        Overload the string method to print a clear report
        :return: String describing the results
        """

        # Compute report if initialized with body and config
        if self.body:
            self.fill_report()

        # Fill the printed report
        res = "No results"
        if self.result_dict:
            res = "\nSimulation report\n"
            res += "-----------------\n\n"
            res += "## Simulator ##\n"
            res += "\tName: " + self.result_dict["simulator"] + "\n"
            res += "\tAcceleration factor: " + str(self.result_dict["sim_speed"]) + "\n\n"
            res += "## Exit ##\n"
            res += "\tType: " + self.result_dict["stop"] + "\n"
            res += "\tTime of simulation: {0:.2f} s ".format(self.result_dict["t_sim"])
            res += "(start: {0:.2f}".format(self.result_dict["t_init"])
            res += " and stop: {0:.2f}".format(self.result_dict["t_end"]) + ")\n\n"
            res += "## Optimization ##\n"
            res += "\tConfig name: " + self.result_dict["config_name"] + "\n"
            res += "\tMuscle name: " + self.result_dict["config_muscles"] + "\n"
            res += "\tGenome vector: " + str(self.result_dict["config_opt"]) + "\n"
            res += "\tLoss function score: {0:.4f}".format(self.result_dict["score"]) + "\n\n"

        return res
