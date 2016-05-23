import logging
from simulator import *

ALIASES = ["BLENDERSIM", "BLENDER", "BLENDERPLAYER"]
SIMULATORS = {"BLENDER": "Blender"}
DEFAULT_SIMULATOR = "BLENDER"


def launch_simulator(opt_):
    if type(opt_) == dict and "simulator" in opt_:
        simulator_ = opt_["simulator"]
        if simulator_ not in SIMULATORS:
            simulator_ = DEFAULT_SIMULATOR
    else:
        simulator_ = DEFAULT_SIMULATOR
    simulator_ = SIMULATORS[simulator_] + "(opt_)"

    # Perform simulation
    logging.info("Processing simulation request")
    simulator_ = eval(simulator_)
    simulator_.launch_simulation()
    logging.info("Simulation request processed")

    return simulator_.get_results()
