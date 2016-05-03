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


import logging

class Config:
    """Describe the configuration file to pass as an argument to a given simulation"""

    def __init__(self):
        """Init default config parameters"""

        # Simulation parameters
        self.name = ""
        self.sim_speed = 1.0
        self.logger_name = "INFO"
        self.logger = logging.Logger(self.logger_name)
        self.exit_condition = "owner['n_iter'] > 500"
        self.timeout = 10
        self.save_path = "default"

        # Physical parameters
        self.muscle_type = "DampedSpringReducedTorqueMuscle"
        self.back_leg_L_muscles = []
        self.back_leg_R_muscles = []
        self.front_leg_L_muscles = []
        self.front_leg_R_muscles = []
        self.brain = dict()
        self.body = dict()
        self.dist_ref = 20
        self.power_ref = 1000

    def get_params_list(self):
        """Return a list including all the parameters that can be changed to tune the controller model"""

        liste = []
        for m in self.back_leg_L_muscles:
            liste += [m["anch_1"][0], m["anch_1"][1], m["anch_1"][2], m["anch_2"][0], m["anch_2"][1], m["anch_2"][2],
                      m["k"], m["c"], m["kc"], m["kl0"]]

        for m in self.front_leg_L_muscles:
            liste += [m["anch_1"][0], m["anch_1"][1], m["anch_1"][2], m["anch_2"][0], m["anch_2"][1], m["anch_2"][2],
                      m["k"], m["c"], m["kc"], m["kl0"]]

        for m in self.back_leg_R_muscles:
            liste += [m["anch_1"][0], m["anch_1"][1], m["anch_1"][2], m["anch_2"][0], m["anch_2"][1], m["anch_2"][2],
                      m["k"], m["c"], m["kc"], m["kl0"]]

        for m in self.front_leg_R_muscles:
            liste += [m["anch_1"][0], m["anch_1"][1], m["anch_1"][2], m["anch_2"][0], m["anch_2"][1], m["anch_2"][2],
                      m["k"], m["c"], m["kc"], m["kl0"]]

        for m in self.body["muscles"]:
            liste += [m["anch_1"][0], m["anch_1"][1], m["anch_1"][2], m["anch_2"][0], m["anch_2"][1], m["anch_2"][2],
                      m["k"], m["c"], m["kc"], m["kl0"]]

        liste += [self.brain["n_osc"], self.brain["h"], self.brain["tau"], self.brain["T"], self.brain["a"],
                  self.brain["b"], self.brain["c"], self.brain["aa"], self.brain["time_interval"]]

        return liste


class DogDefConfig(Config):
    """Default configuration file for dog.blend"""

    def __init__(self):
        """Init Dog Default Config parameters"""

        # Simulation parameters

        Config.__init__(self)
        self.muscle_type = "DampedSpringMuscle"
        self.name = "default_dog_simulation_config"
        self.exit_condition = "bge.logic.getCurrentScene().objects['obj_body'].worldPosition.z < -1.8"

        # Back legs
        BL_biceps = {"name": "B_biceps.L", "logger": "INFO", "obj_1": "obj_body", "obj_2": "obj_shin.L",
                     "anch_1": [0.95, -1, -0.54], "anch_2": [-0.055, 0, 0.6], "k": 500,
                     "c": 50, "kc": -15, "kl0": 1, "brain_sig": 2}
        BR_biceps = {"name": "B_biceps.R", "logger": "INFO", "obj_1": "obj_body", "obj_2": "obj_shin.R",
                     "anch_1": [0.95, 1, -0.54], "anch_2": [-0.055, 0, 0.6], "k": 500,
                     "c": 50, "kc": -15, "kl0": 1, "brain_sig": 2}
        BL_triceps = {"name": "B_triceps.L", "logger": "INFO", "obj_1": "obj_body", "obj_2": "obj_shin.L",
                      "anch_1": [0.686, -1, 0.094], "anch_2": [-0.126, 0, 0.84], "k": 1500,
                      "c": 150, "kc": -40, "kl0": 0.8, "brain_sig": 0}
        BR_triceps = {"name": "B_triceps.R", "logger": "INFO", "obj_1": "obj_body", "obj_2": "obj_shin.R",
                      "anch_1": [0.686, 1, 0.094], "anch_2": [-0.126, 0, 0.84], "k": 1500,
                      "c": 150, "kc": -40, "kl0": 0.8, "brain_sig": 0}
        BL_gastro = {"name": "B_gastro.L", "logger": "INFO", "obj_1": "obj_shin.L", "obj_2": "obj_shin_lower.L",
                     "anch_1": [-0.126, 0, 0.84], "anch_2": [0.125, 0, -0.08], "k": 10,
                     "c": 2, "kc": 0, "kl0": 1, "brain_sig": None}
        BR_gastro = {"name": "B_gastro.R", "logger": "INFO", "obj_1": "obj_shin.R", "obj_2": "obj_shin_lower.R",
                     "anch_1": [-0.126, 0, 0.84], "anch_2": [0.125, 0, -0.08], "k": 10,
                     "c": 2, "kc": 0, "kl0": 1, "brain_sig": None}
        self.back_leg_L_muscles = [BL_biceps, BL_triceps, BL_gastro]
        self.back_leg_R_muscles = [BR_biceps, BR_triceps, BL_gastro]

        # Front Legs
        FL_biceps = {"name": "F_biceps.L", "logger": "INFO", "obj_1": "obj_body", "obj_2": "obj_upper_arm.L",
                     "anch_1": [-0.93, -1, 0.48], "anch_2": [-0.01, 0, 0.33], "k": 400,
                     "c": 40, "kc": -5, "kl0": 1, "brain_sig": 1}
        FR_biceps = {"name": "F_biceps.R", "logger": "INFO", "obj_1": "obj_body", "obj_2": "obj_upper_arm.R",
                     "anch_1": [-0.93, 1, 0.48], "anch_2": [-0.01, 0, 0.33], "k": 400,
                     "c": 40, "kc": -5, "kl0": 1, "brain_sig": 1}
        FL_triceps = {"name": "F_triceps.L", "logger": "INFO", "obj_1": "obj_body", "obj_2": "obj_upper_arm.L",
                      "anch_1": [-0.61, -1, 0.5], "anch_2": [0.13, 0, 0.978], "k": 1000,
                      "c": 100, "kc": 30, "kl0": 0.4, "brain_sig": 0}
        FR_triceps = {"name": "F_triceps.R", "logger": "INFO", "obj_1": "obj_body", "obj_2": "obj_upper_arm.R",
                      "anch_1": [-0.61, 1, 0.5], "anch_2": [0.13, 0, 0.978], "k": 1000,
                      "c": 100, "kc": 30, "kl0": 0.4, "brain_sig": 0}
        FL_gastro = {"name": "F_gastro.L", "logger": "INFO", "obj_1": "obj_upper_arm.L", "obj_2": "obj_wrist.L",
                     "anch_1": [0.175, 0, 0.752], "anch_2": [0.085, 0, 0], "k": 10,
                     "c": 2, "kc": 0, "kl0": 1, "brain_sig": None}
        FR_gastro = {"name": "F_gastro.R", "logger": "INFO", "obj_1": "obj_upper_arm.R", "obj_2": "obj_wrist.R",
                     "anch_1": [0.175, 0, 0.752], "anch_2": [0.085, 0, 0], "k": 10,
                     "c": 2, "kc": 0, "kl0": 1, "brain_sig": None}
        self.front_leg_L_muscles = [FL_biceps, FL_triceps, FL_gastro]
        self.front_leg_R_muscles = [FR_biceps, FR_triceps, FR_gastro]

        # Brain
        self.brain = {"name": "default_dog_matsuoka_brain", "n_osc": 4, "h": 1e-3, "tau": 1e-2,
                      "T": 5e-2, "a": 10.5, "b": 20.5, "c": 0.08, "aa": 3, "time_interval": 1e-3}

        # Body
        neck1 = {"name": "muscle_neck1", "logger": "INFO", "obj_1": "obj_body", "obj_2": "obj_head",
                 "anch_1": [-0.95, 0, 0.47], "anch_2": [-0.06, 0, -0.71], "k": 2000,
                 "c": 100, "kc": 0, "kl0": 0.8}
        neck2 = {"name": "muscle_neck2", "logger": "INFO", "obj_1": "obj_body", "obj_2": "obj_head",
                 "anch_1": [-0.59, 0, 1.4], "anch_2": [0.117, 0, -0.26], "k": 2000,
                 "c": 100, "kc": 0, "kl0": 0.8}
        body_muscles = [neck1, neck2]
        self.body = {"name": "Doggy", "obj" : "obj_body", "muscles": body_muscles}


class DogVertDefConfig(Config):
    """Default configuration file for dog_vert.blend"""

    def __init__(self):
        """Init Dog Default Config parameters"""

        # Simulation parameters
        Config.__init__(self)
        self.muscle_type = "DampedSpringMuscle"
        self.name = "default_dog_vert_simulation_config"
        self.exit_condition = "owner['n_iter'] > 2500"  # "bge.logic.getCurrentScene().objects['obj_body.B'].worldPosition.z < -1.8"

        # Back legs
        BL_biceps = {"name": "B_biceps.L", "logger": "INFO", "obj_1": "obj_body.B", "obj_2": "obj_shin.L",
                     "anch_1": [0.91, -1, -0.3], "anch_2": [0.066, 0, 0.3], "k": 500,
                     "c": 50, "kc": -40, "kl0": 1, "brain_sig": 2}
        BR_biceps = {"name": "B_biceps.R", "logger": "INFO", "obj_1": "obj_body.B", "obj_2": "obj_shin.R",
                     "anch_1": [0.91, 1, -0.3], "anch_2": [0.066, 0, 0.3], "k": 500,
                     "c": 50, "kc": -40, "kl0": 1, "brain_sig": 2}
        BL_triceps = {"name": "B_triceps.L", "logger": "INFO", "obj_1": "obj_body.B", "obj_2": "obj_shin.L",
                      "anch_1": [0.72, -1, 0.23], "anch_2": [-0.102, 0, 0.55], "k": 1000,
                      "c": 50, "kc": -40, "kl0": 0.6, "brain_sig": None}
        BR_triceps = {"name": "B_triceps.R", "logger": "INFO", "obj_1": "obj_body.B", "obj_2": "obj_shin.R",
                      "anch_1": [0.72, 1, 0.23], "anch_2": [-0.102, 0, 0.55], "k": 1000,
                      "c": 50, "kc": -40, "kl0": 0.6, "brain_sig": None}
        BL_gastro = {"name": "B_gastro.L", "logger": "INFO", "obj_1": "obj_thigh.L", "obj_2": "obj_shin_lower.L",
                     "anch_1": [-0.053, 0, -0.77], "anch_2": [0.09, 0, 0.14], "k": 200,
                     "c": 20, "kc": -10, "kl0": 1, "brain_sig": 2}
        BR_gastro = {"name": "B_gastro.R", "logger": "INFO", "obj_1": "obj_thigh.R", "obj_2": "obj_shin_lower.R",
                     "anch_1": [-0.053, 0, -0.77], "anch_2": [0.09, 0, 0.14], "k": 200,
                     "c": 20, "kc": -10, "kl0": 1, "brain_sig": 2}
        self.back_leg_L_muscles = [BL_biceps, BL_triceps, BL_gastro]
        self.back_leg_R_muscles = [BR_biceps, BR_triceps, BR_gastro]

        # Front Legs
        FL_biceps = {"name": "F_biceps.L", "logger": "INFO", "obj_1": "obj_body", "obj_2": "obj_upper_arm.L",
                     "anch_1": [-0.93, -1, 0.48], "anch_2": [-0.01, 0, 0.33], "k": 400,
                     "c": 40, "kc": -7, "kl0": 1, "brain_sig": 1}
        FR_biceps = {"name": "F_biceps.R", "logger": "INFO", "obj_1": "obj_body", "obj_2": "obj_upper_arm.R",
                     "anch_1": [-0.93, 1, 0.48], "anch_2": [-0.01, 0, 0.33], "k": 400,
                     "c": 40, "kc": -7, "kl0": 1, "brain_sig": 1}
        FL_triceps = {"name": "F_triceps.L", "logger": "INFO", "obj_1": "obj_body", "obj_2": "obj_upper_arm.L",
                      "anch_1": [-0.61, -1, 0.5], "anch_2": [0.13, 0, 0.978], "k": 1000,
                      "c": 100, "kc": 30, "kl0": 0.4, "brain_sig": None}
        FR_triceps = {"name": "F_triceps.R", "logger": "INFO", "obj_1": "obj_body", "obj_2": "obj_upper_arm.R",
                      "anch_1": [-0.61, 1, 0.5], "anch_2": [0.13, 0, 0.978], "k": 1000,
                      "c": 100, "kc": 30, "kl0": 0.4, "brain_sig": None}
        FL_gastro = {"name": "F_gastro.L", "logger": "INFO", "obj_1": "obj_upper_arm.L", "obj_2": "obj_wrist.L",
                     "anch_1": [0.175, 0, 0.752], "anch_2": [0.085, 0, 0], "k": 10,
                     "c": 2, "kc": 0, "kl0": 1, "brain_sig": None}
        FR_gastro = {"name": "F_gastro.R", "logger": "INFO", "obj_1": "obj_upper_arm.R", "obj_2": "obj_wrist.R",
                     "anch_1": [0.175, 0, 0.752], "anch_2": [0.085, 0, 0], "k": 10,
                     "c": 2, "kc": 0, "kl0": 1, "brain_sig": None}
        self.front_leg_L_muscles = [FL_biceps, FL_triceps, FL_gastro]
        self.front_leg_R_muscles = [FR_biceps, FR_triceps, FR_gastro]

        # Brain
        self.brain = {"name": "default_dog_matsuoka_brain", "n_osc": 4, "h": 1e-3, "tau": 1e-2,
                      "T": 5e-2, "a": 10.5, "b": 20.5, "c": 0.08, "aa": 3, "time_interval": 1e-3}

        # Body
        neck1 = {"name": "muscle_neck1", "logger": "INFO", "obj_1": "obj_body", "obj_2": "obj_head",
                 "anch_1": [-0.95, 0, 0.47], "anch_2": [-0.06, 0, -0.71], "k": 2000,
                 "c": 100, "kc": 0, "kl0": 0.8}
        neck2 = {"name": "muscle_neck2", "logger": "INFO", "obj_1": "obj_body", "obj_2": "obj_head",
                 "anch_1": [-0.59, 0, 1.4], "anch_2": [0.117, 0, -0.26], "k": 2000,
                 "c": 100, "kc": 0, "kl0": 0.8}

        vert1_u = {"name": "muscle_vert1_up", "logger": "INFO", "obj_1": "obj_body", "obj_2": "obj_vert.1",
                   "anch_1": [-0.186, 0, 0.93], "anch_2": [-0.01, 0, 0.1], "k": 4000,
                   "c": 100, "kc": 0, "kl0": 0.8}
        vert1_d = {"name": "muscle_vert1_down", "logger": "INFO", "obj_1": "obj_body", "obj_2": "obj_vert.1",
                   "anch_1": [-0.167, 0, 0.65], "anch_2": [-0.01, 0, -0.1], "k": 2000,
                   "c": 100, "kc": 0, "kl0": 0.8}

        vert2_u = {"name": "muscle_vert2_up", "logger": "INFO", "obj_1": "obj_vert.1", "obj_2": "obj_vert.2",
                   "anch_1": [0.01, 0, 0.1], "anch_2": [-0.01, 0, 0.1], "k": 2000,
                   "c": 100, "kc": 0, "kl0": 0.8}
        vert2_d = {"name": "muscle_vert2_down", "logger": "INFO", "obj_1": "obj_vert.1", "obj_2": "obj_vert.2",
                   "anch_1": [0.01, 0, -0.1], "anch_2": [-0.01, 0, -0.1], "k": 2000,
                   "c": 100, "kc": 0, "kl0": 0.8}

        vert3_u = {"name": "muscle_vert3_up", "logger": "INFO", "obj_1": "obj_vert.2", "obj_2": "obj_vert.3",
                   "anch_1": [0.01, 0, 0.1], "anch_2": [-0.01, 0, 0.1], "k": 2000,
                   "c": 100, "kc": 0, "kl0": 0.8}
        vert3_d = {"name": "muscle_vert3_down", "logger": "INFO", "obj_1": "obj_vert.2", "obj_2": "obj_vert.3",
                   "anch_1": [0.01, 0, -0.1], "anch_2": [-0.01, 0, -0.1], "k": 2000,
                   "c": 100, "kc": 0, "kl0": 0.8}

        vert4_u = {"name": "muscle_vert4_up", "logger": "INFO", "obj_1": "obj_vert.3", "obj_2": "obj_vert.4",
                   "anch_1": [0.01, 0, 0.1], "anch_2": [-0.01, 0, 0.1], "k": 2000,
                   "c": 100, "kc": 0, "kl0": 0.8}
        vert4_d = {"name": "muscle_vert4_down", "logger": "INFO", "obj_1": "obj_vert.3", "obj_2": "obj_vert.4",
                   "anch_1": [0.01, 0, -0.1], "anch_2": [-0.01, 0, -0.1], "k": 2000,
                   "c": 100, "kc": 0, "kl0": 0.8}

        vert5_u = {"name": "muscle_vert5_up", "logger": "INFO", "obj_1": "obj_vert.4", "obj_2": "obj_vert.5",
                   "anch_1": [0.01, 0, 0.1], "anch_2": [-0.01, 0, 0.1], "k": 2000,
                   "c": 100, "kc": 0, "kl0": 0.8}
        vert5_d = {"name": "muscle_vert5_down", "logger": "INFO", "obj_1": "obj_vert.4", "obj_2": "obj_vert.5",
                   "anch_1": [0.01, 0, -0.1], "anch_2": [-0.01, 0, -0.1], "k": 2000,
                   "c": 100, "kc": 0, "kl0": 0.8}

        vert6_u = {"name": "muscle_vert6_up", "logger": "INFO", "obj_1": "obj_vert.5", "obj_2": "obj_body.B",
                   "anch_1": [0.01, 0, 0.1], "anch_2": [0.425, 0, 0.93], "k": 2000,
                   "c": 100, "kc": 0, "kl0": 0.8}
        vert6_d = {"name": "muscle_vert6_down", "logger": "INFO", "obj_1": "obj_vert.5", "obj_2": "obj_body.B",
                   "anch_1": [0.01, 0, -0.1], "anch_2": [0.425, 0, 0.65], "k": 2000,
                   "c": 100, "kc": 0, "kl0": 0.8}
        abdos = {"name": "muscle_abdos", "logger": "INFO", "obj_1": "obj_body", "obj_2": "obj_body.B",
                 "anch_1": [-0.1977, 0, -0.61], "anch_2": [0.45, 0, -0.61], "k": 2000,
                 "c": 200, "kc": 0, "kl0": 0.85}
        body_muscles = [neck1, neck2, vert1_u, vert1_d, vert2_u, vert2_d, vert3_u, vert3_d, vert4_u, vert4_d,
                        vert5_u, vert5_d, vert6_u, vert6_d, abdos]
        self.body = {"name": "Doggy Vertebrate", "obj" : "obj_body", "muscles": body_muscles}


class MouseDefConfig(Config):
    """Default configuration file for cheesy.blend"""

    def __init__(self):
        """Init Mouse Default Config parameters"""

        # Simulation parameters
        Config.__init__(self)
        self.name = "default_cheesy_simulation_config"
        self.exit_condition = "bge.logic.getCurrentScene().objects['obj_spine'].worldPosition.z < -1.8"

        # Back legs muscles
        BL_biceps = {"name": "B_biceps.L", "logger": "INFO", "obj_1": "obj_hips", "obj_2": "obj_shin.L",
                     "anch_1": [0.14, -0.01, 0.06], "anch_2": [0.017, -0.13, 0.1], "k": 0,
                     "c": 0, "kc": 0, "kl0": 1, "brain_sig": None}
        BR_biceps = {"name": "B_biceps.R", "logger": "INFO", "obj_1": "obj_hips", "obj_2": "obj_shin.R",
                     "anch_1": [-0.14, -0.01, 0.06], "anch_2": [-0.017, -0.13, 0.1], "k": 0,
                     "c": 10, "kc": 0, "kl0": 1, "brain_sig": None}
        BL_rectus = {"name": "B_rectus.L", "logger": "INFO", "obj_1": "obj_hips", "obj_2": "obj_shin.L",
                     "anch_1": [0.15, -0.11, 0.17], "anch_2": [0.017, -0.22, 0.16], "k": 100,
                     "c": 10, "kc": 0, "kl0": 0.6, "brain_sig": None}
        BR_rectus = {"name": "B_rectus.R", "logger": "INFO", "obj_1": "obj_hips", "obj_2": "obj_shin.R",
                     "anch_1": [-0.15, -0.11, 0.17], "anch_2": [-0.017, -0.22, 0.16], "k": 100,
                     "c": 10, "kc": 0, "kl0": 0.6, "brain_sig": None}
        BL_gastrocenius = {"name": "B_gastro.L", "logger": "INFO", "obj_1": "obj_thigh.L", "obj_2": "obj_shin_lower.L",
                           "anch_1": [-0.01, -0.05, -0.03], "anch_2": [0, 0.18, 0.015], "k": 0,
                           "c": 1, "kc": 0, "kl0": 0.2, "brain_sig": None}
        BR_gastrocenius = {"name": "B_gastro.R", "logger": "INFO", "obj_1": "obj_thigh.R", "obj_2": "obj_shin_lower.R",
                           "anch_1": [0.01, -0.05, -0.03], "anch_2": [0, 0.18, 0.015], "k": 0,
                           "c": 1, "kc": 0, "kl0": 0.2, "brain_sig": None}
        BL_tensor = {"name": "B_tensor.L", "logger": "INFO", "obj_1": "obj_thigh.L", "obj_2": "obj_shin_lower.L",
                     "anch_1": [-0.01, -0.16, -0.07], "anch_2": [0, 0.09, 0.015], "k": 0,
                     "c": 0, "kc": 0, "kl0": 1, "brain_sig": None}
        BR_tensor = {"name": "B_tensor.R", "logger": "INFO", "obj_1": "obj_thigh.R", "obj_2": "obj_shin_lower.R",
                     "anch_1": [0.01, -0.16, -0.07], "anch_2": [0, 0.09, 0.015], "k": 0,
                     "c": 0, "kc": 0, "kl0": 1, "brain_sig": None}
        self.back_leg_L_muscles = [BL_biceps, BL_rectus, BL_gastrocenius, BL_tensor]
        self.back_leg_R_muscles = [BR_biceps, BR_rectus, BR_gastrocenius, BR_tensor]

        # Front Legs muscles
        FL_biceps = {"name": "F_biceps.L", "logger": "INFO", "obj_1": "obj_shoulder.L", "obj_2": "obj_upper_arm.L",
                     "anch_1": [-0.93, -1, 0.48], "anch_2": [-0.01, 0, 0.33], "k": 400,
                     "c": 40, "kc": -5, "kl0": 1, "brain_sig": 1}
        FR_biceps = {"name": "F_biceps.R", "logger": "INFO", "obj_1": "obj_shoulder.R", "obj_2": "obj_upper_arm.R",
                     "anch_1": [-0.93, 1, 0.48], "anch_2": [-0.01, 0, 0.33], "k": 400,
                     "c": 40, "kc": -5, "kl0": 1, "brain_sig": 1}
        FL_triceps = {"name": "F_triceps.L", "logger": "INFO", "obj_1": "obj_shoulder.L", "obj_2": "obj_upper_arm.L",
                      "anch_1": [-0.61, -1, 0.5], "anch_2": [0.13, 0, 0.978], "k": 1000,
                      "c": 100, "kc": 30, "kl0": 0.4, "brain_sig": 0}
        FR_triceps = {"name": "F_triceps.R", "logger": "INFO", "obj_1": "obj_shoulder.R", "obj_2": "obj_upper_arm.R",
                      "anch_1": [-0.61, 1, 0.5], "anch_2": [0.13, 0, 0.978], "k": 1000,
                      "c": 100, "kc": 30, "kl0": 0.4, "brain_sig": 0}
        FL_gastro = {"name": "F_gastro.L", "logger": "INFO", "obj_1": "obj_upper_arm.L", "obj_2": "obj_wrist.L",
                     "anch_1": [0.175, 0, 0.752], "anch_2": [0.085, 0, 0], "k": 10,
                     "c": 2, "kc": 0, "kl0": 1, "brain_sig": None}
        FR_gastro = {"name": "F_gastro.R", "logger": "INFO", "obj_1": "obj_upper_arm.R", "obj_2": "obj_wrist.R",
                     "anch_1": [0.175, 0, 0.752], "anch_2": [0.085, 0, 0], "k": 10,
                     "c": 2, "kc": 0, "kl0": 1, "brain_sig": None}
        self.front_leg_L_muscles = []  # FL_biceps, FL_triceps, FL_gastro]
        self.front_leg_R_muscles = []  # FR_biceps, FR_triceps, FR_gastro]

        # Brain
        self.brain = {"name": "default_dog_matsuoka_brain", "n_osc": 4, "h": 1e-3, "tau": 1e-2,
                      "T": 5e-2, "a": 10.5, "b": 20.5, "c": 0.08, "aa": 3, "time_interval": 1e-3}

        # Body
        neck1 = {"name": "muscle_neck1", "logger": "INFO", "obj_1": "obj_body", "obj_2": "obj_head",
                 "anch_1": [-0.95, 0, 0.47], "anch_2": [-0.06, 0, -0.71], "k": 2000,
                 "c": 100, "kc": 0, "kl0": 0.8}
        neck2 = {"name": "muscle_neck2", "logger": "INFO", "obj_1": "obj_body", "obj_2": "obj_head",
                 "anch_1": [-0.59, 0, 1.4], "anch_2": [0.117, 0, -0.26], "k": 2000,
                 "c": 100, "kc": 0, "kl0": 0.8}
        body_muscles = []  # neck1, neck2]
        self.body = {"name": "Cheesy", "obj" : "obj_body", "muscles": body_muscles}


class MouseSimpleConfig(Config):
    """Simple configuration file for mouse.blend"""

    def __init__(self):
        """Init Mouse Default Config parameters"""

        # Simulation parameters
        Config.__init__(self)
        self.logger_name = "INFO"
        self.logger = logging.Logger(self.logger_name)
        self.name = "simple_mouse_simulation_config"
        self.muscle_type = "SimpleMuscle"
        self.exit_condition = "bge.logic.getCurrentScene().objects['obj_spine'].worldPosition.z < -1.8"

        # Back legs muscles
        BL_HFL = {"name": "B_HFL.L", "logger": "INFO", "obj_1": "obj_hip.L", "obj_2": "obj_shin.L",
                  "anch_1": [0.14, -0.01, 0.06], "anch_2": [0.017, -0.13, 0.1],
                  "brain_sig": None}
        BR_HFL = {"name": "B_HFL.R", "logger": "INFO", "obj_1": "obj_hip.R", "obj_2": "obj_shin.R",
                  "anch_1": [-0.14, -0.01, 0.06], "anch_2": [-0.017, -0.13, 0.1],
                  "brain_sig": None}
        BL_gastrocenius = {"name": "B_gastro.L", "logger": "INFO", "obj_1": "obj_thigh.L", "obj_2": "obj_shin.L",
                           "anch_1": [-0.19195, -0.69294, 0.20698], "anch_2": [-0.23857, -0.6465, -0.01011],
                           "brain_sig": None, "maxF": 0.0}
        BR_gastrocenius = {"name": "B_gastro.R", "logger": "INFO", "obj_1": "obj_thigh.R", "obj_2": "obj_shin.R",
                           "anch_1": [0.1941, -0.69016, 0.20814], "anch_2": [0.23857, -0.6465, -0.01011],
                           "brain_sig": None, "maxF": 0.0}
        BL_tibialis = {"name": "B_tibialis.L", "logger": "INFO", "obj_1": "obj_shin.L", "obj_2": "obj_shin_lower.L",
                       "anch_1": [-0.23857, -0.6465, -0.01011], "anch_2": [-0.27435, -0.754, -0.1395],
                       "brain_sig": None, "maxF": -0.0}
        BR_tibialis = {"name": "B_tibialis.R", "logger": "INFO", "obj_1": "obj_shin.R", "obj_2": "obj_shin_lower.R",
                       "anch_1": [0.23937, -0.64779, -0.01044], "anch_2": [0.27433, -0.75355, -0.1396],
                       "brain_sig": None, "maxF": -0.0}
        self.back_leg_L_muscles = [BL_tibialis, BL_gastrocenius]
        self.back_leg_R_muscles = [BR_tibialis, BR_gastrocenius]

        # Front Legs muscles
        FL_biceps = {"name": "F_biceps.L", "logger": "INFO", "obj_1": "obj_upper_arm.L", "obj_2": "obj_forearm.L",
                     "anch_1": [-0.21322, 0.28541, -0.04615], "anch_2": [-0.27499, 0.32622, -0.22265],
                     "brain_sig": None, "maxF": 1.1}
        FR_biceps = {"name": "F_biceps.R", "logger": "INFO", "obj_1": "obj_upper_arm.R", "obj_2": "obj_forearm.R",
                     "anch_1": [0.21242, 0.29976, -0.04857], "anch_2": [0.2744, 0.32456, -0.22214],
                     "brain_sig": None, "maxF": 1.1}
        FL_gastro = {"name": "F_gastro.L", "logger": "INFO", "obj_1": "obj_forearm.L", "obj_2": "obj_wrist.L",
                     "anch_1": [-0.27499, 0.32622, -0.22265], "anch_2": [-0.2919, 0.51747, -0.28179],
                     "brain_sig": None, "maxF": -0.01}
        FR_gastro = {"name": "F_gastro.R", "logger": "INFO", "obj_1": "obj_forearm.R", "obj_2": "obj_wrist.R",
                     "anch_1": [0.2744, 0.32456, -0.22214], "anch_2": [0.29257, 0.51605, -0.28135],
                     "brain_sig": None, "maxF": -0.01}
        self.front_leg_L_muscles = [FL_biceps, FL_gastro]
        self.front_leg_R_muscles = [FR_biceps, FR_gastro]

        # Brain
        self.brain = {"name": "default_robot_matsuoka_brain", "n_osc": 4, "h": 1e-3, "tau": 1e-2,
                      "T": 5e-2, "a": 10.5, "b": 20.5, "c": 0.08, "aa": 3, "time_interval": 1e-3}

        # Body
        neck = {"name": "muscle_neck2", "logger": "INFO", "obj_1": "joint_1_obj_neck", "obj_2": "obj_neck",
                "anch_1": [-0.59, 0, 1.4], "anch_2": [0.117, 0, -0.26],
                "brain_sig": None, "maxF": -0.465}
        body_muscles = [neck]
        self.body = {"name": "Mouse", "muscles": body_muscles}
