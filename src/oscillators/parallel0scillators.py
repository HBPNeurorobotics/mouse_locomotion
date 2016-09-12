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

import numpy as np
import time

from .matsuokaNeurons import MatsuokaNeurons

from .synapse import Synapse


class ParallelOscillator:
    def __init__(self, config_):
        self.save = False
        self.config = config_
        self.neurons = []
        self.rec = np.array(np.zeros((4, 1)))
        self.state = []
        for i in range(2):
            self.neurons.append(MatsuokaNeurons(self.config["neuron_config"],
                                                self.config["neuron_config"],
                                                self.config["inner_weights"],
                                                self.config["weights"], 0.01 * (i + 1)))

        self.neurons[0].add_synapse(1, self.neurons[1].output)
        self.neurons[1].add_synapse(1, self.neurons[0].output)

    def update(self):
        res = []

        # We take
        for i in range(2):
            self.neurons[i].reset_updates()
        self.state = []
        for i in range(2):
            self.neurons[i].update()
            self.state.append(self.neurons[i].exitatingNeuron.y / 5.)
            self.state.append(self.neurons[i].inhibitingNeuron.y / 5.)
            if self.save:
                res.append([self.neurons[i].exitatingNeuron.y / 5.])
                res.append([self.neurons[i].inhibitingNeuron.y / 5.])
        if self.save:
            res = np.array(res)
            self.rec = np.hstack((self.rec, res))

if __name__ == "__main__":
    # Configuration for Test
    config = dict()
    config['neuron_config'] = {"tau": 0.6e-2, "T": 1.5e-2, "b": 2.5, "c": 0.68, "threshold": 0., "h": 1e-3}
    config["inner_weights"] = 2.0
    config['weights'] = 0.5
    config["neuron_config2"] = {"tau": 0.6e-2, "T": 3.2e-2, "b": 2.5, "c": 0.15, "threshold": 0., "h": 1e-3}

    # Test
    osc = ParallelOscillator(config)  # Oscillator with high frequency
    osc.save = True
    perturbation = MatsuokaNeurons(config["neuron_config2"],
                                   config["neuron_config2"],
                                   config["inner_weights"],
                                   config['weights'], 0.02)  # Low frequency perturbation
    if perturbation.inhibitingNeuron.x > 0.:
        perturbation.inhibitingNeuron.set_activity(0.001)
    else:
        perturbation.exitatingNeuron.set_activity(0.001)
    perturbation.reset_updates()
    perturbation.update()
    sim_time = 400
    start_perturbation = 500  # Start perturbation after a specific time
    perturbation_started = False
    for iteration in range(sim_time):
        if not perturbation_started and iteration >= start_perturbation \
                and -0.001 < osc.neurons[0].output.y - perturbation.output.y < 0.001:
            osc.neurons[0].synapses.append(Synapse(perturbation.output, osc.neurons[0].inhibitingNeuron, 2))
            osc.neurons[1].synapses.append(Synapse(perturbation.output, osc.neurons[1].exitatingNeuron, 2))
            perturbation_started = True
        elif perturbation_started:
            perturbation.reset_updates()
            perturbation.update()
        osc.update()
    osc.plot(sim_time)
