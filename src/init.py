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

import datetime
import logging.config
import os
import sys
import time

import bge

root = os.path.dirname(os.path.dirname(bge.logic.expandPath("//"))).replace("\\", "/")
src = root + "/src/"
sys.path.append(src)

from musculoskeletals import Body
from config import Config
from simulators.updaters import BlenderUtils


# Get BGE handles
scene = bge.logic.getCurrentScene()

GENOME = False
if sys.argv[len(sys.argv) - 1] == "FROM_START.PY":
    # Catch command-line config when started from another script
    argv = sys.argv
    argv = eval(argv[argv.index("-") + 1])
    CONFIG_NAME = argv["config_name"]
    LOG_FILE = argv["logfile"]
    SAVE_NAME = argv["filename"]
    if "genome" in argv:
        GENOME = eval(argv["genome"])
else:
    # Default config when started directly from Blender
    CONFIG_NAME = root + "/configs/default_dog_vert_simulation_config.json"
    LOG_FILE = os.path.expanduser("~").replace("\\", "/") + "/.log/qSim.log"
    dirname = root + "/save"
    filename = "sim_" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f") + ".qsm"
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    SAVE_NAME = dirname + "/" + filename

# Create python controller
global owner
owner = dict()

# Create Logger and configuration
if not os.path.exists(os.path.dirname(LOG_FILE)):
    os.makedirs(os.path.dirname(LOG_FILE))
if not os.path.exists(LOG_FILE):
    f = open(LOG_FILE, 'w')
    f.close()

# Init configuration
logging.config.fileConfig(root + "/etc/logging.conf",
                          defaults={'logfilename': LOG_FILE, 'simLevel': "DEBUG"})
configuration = Config("Blender", CONFIG_NAME)
logger = configuration.logger
configuration.save_path = SAVE_NAME
configuration.n_iter = 0
configuration.t_init = time.time()
if GENOME:
    configuration.set_conn_matrix(GENOME)

# Init owner variables
owner["config"] = configuration
owner["body"] = Body(configuration, BlenderUtils(scene))

# Advertise simulation has begun
logger.info("####################################")
logger.info("##   Mouse Locomotion Simulation   #")
logger.info("##   ---------------------------   #")
logger.info("##                                 #")
logger.info("##     Gabriel Urbain - UGent      #")
logger.info("##     Dimitri RODARIE - HBP       #")
logger.info("##              2016               #")
logger.info("####################################\n")

# Set simulation parameters
# bge.logic.setTimeScale(configuration.sim_speed)
