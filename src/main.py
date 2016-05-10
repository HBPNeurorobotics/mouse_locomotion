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

import time
import pickle
import bge

from result import Result

# Get BGE handles
controller = bge.logic.getCurrentController()
exit_actuator = bge.logic.getCurrentController().actuators['quit_game']
keyboard = bge.logic.keyboard

# TODO: Do something with the simulation even if there is no logger declared
if hasattr(owner["config"], 'logger'):
    # Time-step update instructions
    owner["body"].update()

    # DEBUG control and display
    owner["config"].n_iter += 1
    owner["config"].logger.debug("Main iteration " + str(owner["config"].n_iter) + ": stop state = " +
        str(eval(owner["config"].exit_condition)))
    owner["config"].logger.debug("Interruption: exit = " + str(eval(owner["config"].exit_condition)) +
        " sim time = " + str(time.time() -  owner["config"].t_init) + " timeout = " + str(
        owner["config"].timeout))

    # Simulation interruption
    if eval(owner["config"].exit_condition) \
            or bge.logic.KX_INPUT_ACTIVE == keyboard.events[bge.events.SPACEKEY] \
            or time.time() - owner["config"].t_init > owner["config"].timeout:

        # Get time of simulation
        owner["config"].t_end = time.time()
        
        # Create a result instance and save
        try:
            results = Result(owner["body"])
            owner["config"].logger.info(results)
            results.save()
        except Exception as e:
            owner["config"].logger.error("Unable to create a result report. Caused by: " + str(e))
            pass

        # exit
        controller.activate(exit_actuator)
