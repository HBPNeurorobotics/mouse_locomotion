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
# June 2016
##
import copy


class SimulationRequest:
    def __init__(self, rqt, index, callback=None):
        self.rqt = rqt
        self.index = index
        self.callback = callback

    def copy(self):
        return SimulationRequest(self.rqt, self.index, copy.copy(self.callback))


class Connexion:
    def __init__(self, server_id, connexion, thread=None):
        self.server_id = server_id
        self.connexion = connexion
        self.thread = thread


class ServerInfo:
    def __init__(self, address, port, nb_threads=0, status=False):
        self.address = address
        self.port = port
        self.nb_threads = nb_threads
        self.status = status
