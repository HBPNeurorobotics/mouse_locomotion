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

import math
import logging
from simulations.simulation import Simulation
from utils import PickleUtils
from .service import SimService
from .serviceServer import ServiceServer


class SimServer(Simulation):
    """
    SimServer class provides a services server to listen to external requests and start a Simulator
    simulation remotely and asynchronously.
    Usage:
            # Create and start SimServer thread
            s = SimServer(opt)
            s.start()
    """

    def __init__(self, opt):
        """
        Class initialization
        :param opt: Dictionary containing simulation parameters
        """

        Simulation.__init__(self, opt)
        self.simulator = self.opt["simulator"]
        self.max_threads = 0
        self.test()

    def start(self):
        """Start a service server"""

        if self.max_threads >= 1:
            try:
                t = ServiceServer(SimService, int(self.max_threads))
                self.port = t.port
                Simulation.start(self)
                t.start()
            except KeyboardInterrupt:
                logging.warning("Keyboard interruption from user. Closing the Server.")
        self.stop()

    def test(self):
        """Test the server capacities to know how many parallel simulations it can run"""

        logging.info("Test of the server capacities.")
        rsp_ = SimService.test_simulators(self.opt)
        if "interruption" not in rsp_[self.simulator]:
            cpu_capacity = (self.opt['cpu_use'] - rsp_["common"]["CPU"]) / \
                           (rsp_[self.simulator]["CPU"] - rsp_["common"]["CPU"])

            memory_capacity = (self.opt['memory_use'] - rsp_["common"]["memory"]) / \
                              (rsp_[self.simulator]["memory"] - rsp_["common"]["memory"])
            self.max_threads = math.floor(min(cpu_capacity, memory_capacity))
            if self.max_threads >= 1:  # Change the status of the server on the cloud
                logging.info("Server tests finished: The server can run a maximum of " +
                             str(self.max_threads) + " parallel simulation(s) on " + self.simulator)
            else:
                logging.info("Server tests finished: Server capacities does not allow simulations.")
        else:
            logging.info("User interruption during simulation test.")
            self.max_threads = 0.

    def stop(self):
        """Close the Simulation Server and delete file results"""

        Simulation.stop(self)
        # Delete all the simulation files that might stayed after simulation
        PickleUtils.del_all_files(self.save_directory, "qsm")
