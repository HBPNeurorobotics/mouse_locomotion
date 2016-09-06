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
#  File created by: Gabriel Urbain <gabriel.urbain@ugent.be>
#                  Dimitri Rodarie <d.rodarie@gmail.com>
# February 2016
##

import logging
import sys

import psutil
from rpyc import Service

if sys.version_info[:2] < (3, 4):
    import common
else:
    from simulations import common


class SimService(Service):
    """
    SimService class listen to server requests and launch simulation depending on the simulator
    WARNING: Every function called by a SimServer should start with "exposed_"
    Usage:
                # Create and start a SimService using a BgServingThread
                conn = rpyc.connect(address, port)
                bgt = rpyc.BgServingThread(conn)
                async_simulation = rpyc.async(conn.root.exposed_simulation)
    """

    # Service ALIASES used to be recognized by the rpyc registry
    ALIASES = common.ALIASES

    def exposed_simulation(self, opt_):
        """Launch a normal simulation and return its results"""

        return common.launch_simulator(opt_)

    @staticmethod
    def test_simulators(opt_):
        """Launch a simulation and return its results and its cpu and memory usage"""

        # Get the machine current cpu usage and memory before launching simulation
        cpu_percent = sum(psutil.cpu_percent(interval=0.5, percpu=True)) / float(psutil.cpu_count())
        memory_percent = psutil.virtual_memory().percent
        res = {"common": {"CPU": cpu_percent, "memory": memory_percent}}
        # Launch the simulation
        if "simulator" in opt_:
            res[opt_["simulator"]] = common.test_simulator(opt_)
        return res

    def exposed_test(self, opt_):
        """Launch a simulation and return its results and its cpu and memory usage"""

        # Get the machine current cpu usage and memory before launching simulation
        res = self.test_simulators(opt_)
        logging.info("Test Server " + type(self).__name__ +
                     ": \nCPU = " + str(res["common"]["CPU"]) +
                     "\nMemory = " + str(res["common"]["memory"]))
        return res
