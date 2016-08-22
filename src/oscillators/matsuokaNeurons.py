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
# File created by: Dimitri Rodarie <d.rodarie@gmail.com>. May 2016
# Modified by: Gabriel Urbain <gabriel.urbain@ugent.be>.
##

from .neuron import Neuron
from .integrateAndFireNeuron import IntegrateAndFireAdaptationNeuron
from .synapse import Synapse

import numpy as np


class MatsuokaNeurons:
    def __init__(self, exitating_config, inhibiting_config, inner_weight, out_weight):
        self.exitatingNeuron = IntegrateAndFireAdaptationNeuron(exitating_config)
        self.inhibitingNeuron = IntegrateAndFireAdaptationNeuron(inhibiting_config)
        self.input = Neuron()
        self.output = Neuron()

        self.inner_weight = inner_weight

        self.synapses = []

        # Input synapses
        self.synapses.append(Synapse(self.input, self.exitatingNeuron, out_weight))
        self.synapses.append(Synapse(self.input, self.inhibitingNeuron, -out_weight))

        # Inner synapses
        self.synapses.append(Synapse(self.exitatingNeuron, self.inhibitingNeuron, inner_weight))
        self.synapses.append(Synapse(self.inhibitingNeuron, self.exitatingNeuron, inner_weight))

        # Output synapses
        self.synapses.append(Synapse(self.inhibitingNeuron, self.output, -1))
        self.synapses.append(Synapse(self.exitatingNeuron, self.output, 1))

        # We give a little impact on one of the neuron to start the oscillation
        rand = np.random.rand() * 2 - 1
        if rand < 0:
            self.inhibitingNeuron.set_activity(-rand)
        else:
            self.exitatingNeuron.set_activity(rand)

        # We reset the updates
        self.updates = {}
        self.reset_updates()
        self.input.update(self.updates[self.input])
        self.output.update(self.updates[self.output])

    def reset_updates(self):
        self.updates = {self.input: 0., self.inhibitingNeuron: 0., self.exitatingNeuron: 0., self.output: 0.}
        for synapse in self.synapses:
            self.updates[synapse.neuron2] += synapse.get_update_neuron()

    def update(self):
        self.input.reset()
        self.output.reset()
        self.input.update(self.updates[self.input])
        self.inhibitingNeuron.update(self.updates[self.inhibitingNeuron])
        self.exitatingNeuron.update(self.updates[self.exitatingNeuron])
        self.output.update(self.updates[self.output])

    def add_synapse(self, weight, from_):
        self.synapses.append(Synapse(from_, self.input, weight))
