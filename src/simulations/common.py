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
# File created by: Dimitri Rodarie <d.rodarie@gmail.com>
#                  Gabriel Urbain <gabriel.urbain@ugent.be>
# May 2016.
##

import logging
import rpyc
from simulators import *

ALIASES = ["BLENDERSIM", "BLENDERPLAYER"]
REQUESTS = {"Simulation": "simulation", "Test": "test"}
SIMULATORS = {"BLENDER": "Blender"}
DEFAULT_SIMULATOR = "BLENDER"
rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True


def get_simulator(opt_):
    """
    Return a Simulator instance depending on the simulator name defined in the dictionary opt_
    the default value simulator is DEFAULT_SIMULATOR
    :param opt_: Dictionary containing simulation parameters
    :return: Simulator instance
    """

    if type(opt_) == dict and "simulator" in opt_:
        simulator_ = opt_["simulator"]
        if simulator_ not in SIMULATORS:
            simulator_ = DEFAULT_SIMULATOR
    else:
        simulator_ = DEFAULT_SIMULATOR
    return eval(SIMULATORS[simulator_] + "(opt_)")


def launch_simulator(opt_):
    """
    Launch a simulation based on the opt_ parameters and return its results
    :param opt_: Dictionary containing simulation parameters
    :return: Dictionary containing simulation results
    """

    logging.info("Processing simulation request")
    simulator_ = get_simulator(opt_)
    simulator_.launch_simulation()
    logging.info("Simulation request processed")

    return simulator_.get_results()


def test_simulator(opt_):
    """
    Launch a simulation test based on the opt_ parameters and return its results
    :param opt_: Dictionary containing simulation parameters
    :return: Dictionary containing simulation results
    """

    logging.info("Processing simulation test")
    res = get_simulator(opt_).test_simulator()
    logging.info("Simulation test processed")
    return res
