##
# Mouse Locomotion Simulation
# 
# This project provides the user with a framework based on Blender allowing:
#  - Creation and edition of a 3D model
#  - Design of a artificial neural network controller
#  - Offline optimization of the body parameters
#  - Online optimization of the brain controller
# 
# Copyright Gabriel Urbain <gabriel.urbain@ugent.be>. February 2016
# Data Science Lab - Ghent University. Human Brain Project SP10
##

import time
import pickle
import bge

# Get BGE handles
controller = bge.logic.getCurrentController()
exit_actuator = bge.logic.getCurrentController().actuators['quit_game']
keyboard = bge.logic.keyboard


def save():
    global pickle
    """Save te simulation results"""
    owner["config"].logger = None
    f = open(owner["config"].save_path, 'wb')
    pickle.dump([owner["config"].__dict__, time.time()], f, protocol=2)
    f.close()


if not owner["config"].logger is None:
    # Time-step update instructions
    owner["cheesy"].update()

    # DEBUG control and display
    owner["n_iter"] += 1
    owner["config"].logger.debug("Main iteration " + str(owner["n_iter"]) + ": stop state = " +
                                 str(eval(owner["config"].exit_condition)))
    owner["config"].logger.debug("[Interruption: exit = " + str(eval(owner["config"].exit_condition)) +
                                 " sim time = " + str(time.time() - owner["t_init"]) + " timeout = " + str(
        owner["config"].timeout))

    # Simulation interruption
    if eval(owner["config"].exit_condition) \
            or bge.logic.KX_INPUT_ACTIVE == keyboard.events[bge.events.SPACEKEY] \
            or time.time() - owner["t_init"] > owner["config"].timeout:
        # save config
        save()

        # exit
        controller.activate(exit_actuator)
