import logging

import rpyc
from simulator import *

ALIASES = ["BLENDERSIM", "BLENDERPLAYER"]
REQUESTS = {"Simulation": "simulation", "Test": "test"}
SIMULATORS = {"BLENDER": "Blender"}
DEFAULT_SIMULATOR = "BLENDER"
rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True


def get_simulator(opt_):
    if type(opt_) == dict and "simulator" in opt_:
        simulator_ = opt_["simulator"]
        if simulator_ not in SIMULATORS:
            simulator_ = DEFAULT_SIMULATOR
    else:
        simulator_ = DEFAULT_SIMULATOR
    return eval(SIMULATORS[simulator_] + "(opt_)")


def launch_simulator(opt_):
    # Perform simulation
    logging.info("Processing simulation request")
    simulator_ = get_simulator(opt_)
    simulator_.launch_simulation()
    logging.info("Simulation request processed")

    return simulator_.get_results()


def test_simulator(opt_):
    # Perform test simulation
    logging.info("Processing simulation test")
    res = get_simulator(opt_).test_simulator()
    logging.info("Simulation test processed")
    return res
