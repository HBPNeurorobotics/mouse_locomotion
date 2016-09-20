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
# September 2016
##

import time

from result import Result


class Updater:
    """
    Class used to update the brain and the body at each time step during simulation
    """

    def __init__(self, config, body):
        """Class initialization"""

        self.config = config
        self.body = body

        self.penalty = False

    def update(self):
        """
        Update the brain and the body.
        Test the exit condition and stop simulation if it is True.
        """

        brain_signal = self.body.get_brain_output()
        self.penalty = self.body.update(brain_signal)
        self.config.n_iter += 1

        self.config.logger.debug("Main iteration " + str(self.config.n_iter) + ": stop state = " +
                                 str(eval(self.config.exit_condition)))

        if self.exit_condition():
            self.exit()

    def exit_condition(self):
        """
        Test if the simulation exit_condition is True or if the simulation is over or if the model got a penalty.
        :return: Boolean result of the test
        """

        return eval(self.config.exit_condition()) \
               or time.time() - self.config.t_init > self.config.timeout \
               or self.penalty

    def exit(self):
        """Exit the simulation and create a result file"""

        self.config.logger.debug("Interruption: exit = " + str(eval(self.config.exit_condition)) +
                                 " sim time = " + str(time.time() - self.config.t_init) + " timeout = " + str(
            self.config.timeout))
        self.config.t_end = time.time()

        # Create a result instance and save
        try:
            results = Result(self.body)
            self.config.logger.info(results)
            results.save_results()
        except Exception as e:
            self.config.logger.error("Unable to create a result report. Caused by: " + str(e))
            pass
