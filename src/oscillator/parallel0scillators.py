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
from matsuokaNeurons import MatsuokaNeurons
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt


class ParallelOscillators:
    def __init__(self, config_):
        self.config = config_
        self.n_osc = self.config.n_osc * 2  # Number of parallel oscillators
        self.neurons = []
        self.rec = np.array(np.zeros((self.n_osc, 1)))

        assert self.n_osc * 2 == len(self.config.neurons)
        for i in range(self.n_osc):
            self.neurons.append(MatsuokaNeurons(self.config.neurons[i],
                                                self.config.neurons[i + 1],
                                                config_.inner_weights,
                                                config_.weights))

        for i in range(0, self.n_osc, 2):
            self.neurons[i].add_synapse(1, self.neurons[i + 1].output)
            self.neurons[i + 1].add_synapse(1, self.neurons[i].output)

    def update(self):
        res = []

        # We take
        for i in range(self.n_osc):
            self.neurons[i].reset_updates()

        for i in range(self.n_osc):
            self.neurons[i].update()
            res.append([self.neurons[i].output.y])

        res = np.array(res)
        self.rec = np.hstack((self.rec, res))

    def plot(self, stop_time):
        time_ = np.arange(0, stop_time + 1)
        plot_abscissa_step = stop_time / 10
        plt.figure(2, figsize=(15, 10))
        plt.suptitle('Matsuoka Oscillator for mouse gaits control\n')
        plt.subplot(211)
        for n in range(self.n_osc):
            plt.plot(time_, self.rec[n, :], color=np.random.rand(3, 1), label='y' + str(n))
        plt.xticks(np.arange(0, stop_time, plot_abscissa_step))
        plt.xlabel('Time step')
        plt.ylabel('Value of state variables')
        plt.legend()
        plt.savefig('Matsuoka_oscillator_mouse_' + str(time.clock()) + '.png')
        plt.clf()


if __name__ == "__main__":
    # Configuration for Test
    config = type('ConfigTest', (), {})()
    config.n_osc = 1
    neuron_config = {"tau": 0.6, "T": 1.2, "b": 2.5, "c": 0.68, "threshold": 0., "h": 1e-3}
    config.neurons = [neuron_config, neuron_config, neuron_config, neuron_config]
    config.inner_weights = 2.0
    config.weights = 0.5

    # Test
    osc = ParallelOscillators(config)
    for iteration in range(20000):
        osc.update()
    osc.plot(20000)
