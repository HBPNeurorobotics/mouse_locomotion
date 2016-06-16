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
# File created by: Gabriel Urbain <gabriel.urbain@ugent.be>
#                  Dimitri Rodarie <d.rodarie@gmail.com>
# June 2016
##

import logging
import numpy as np
import matplotlib

import time
from genetic import Genetic

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


class MetaOptimization:
    """
    This class provides tools to modify the optimization parameters or methods,
    start different optimisation processes, benchmark and plot them
    Usage:
                # Create meta optimization
                mga = GeneticMetaOptimization(opt, observable)

                # Run cross-over benchmark
                mga.co_bench()
    """

    def __init__(self, opt, observable):
        """
        Init MetaOptimization class by creating a generic container to exploit
        different results
        :param opt: Dictionary containing simulation parameters
        :param observable: Observable instance to get update from
        """

        self.result = dict()
        self.result['n_gen'] = []
        self.result['time'] = []
        self.result['abs_name'] = "Abscissas"
        self.result['ord_name'] = "Ordinates"
        self.result['scores'] = []
        self.result['configs'] = []
        self.result['param_val'] = []

        self.opt = opt
        self.observable = observable

    def display(self):
        """Print the results"""

        res = "\nMeta Optimization results\n"
        res += "--------------------------\n\n"
        j = 0
        for i in self.result['param_val']:
            min_ = ""
            max_ = ""
            mean_ = ""
            for scores in self.result["scores"][j]:
                min_ += str(min(scores)) if len(scores) > 0 else str(0.) + " "
                mean_ += str(sum(scores) / len(scores)) if len(scores) > 0 else str(0.) + " "
                max_ += str(max(scores)) if len(scores) > 0 else str(0.) + " "
            res += "## " + self.result['abs_name'] + " = " + str(i) + " ##\n"
            res += "\tSimulation time: " + str(self.result['time'][j]) + "\n"
            res += "\tMin score evolution: " + "\n\t" + min_ + "\n"
            res += "\tMean score evolution: " + "\n\t" + mean_ + "\n"
            res += "\tMax score evolution: " + "\n\t" + max_ + "\n"
            j += 1

        print(res)

    def plot(self, filename="default.pdf"):
        """
        Plot the result container
        :param filename: String path for the pdf file
        """

        logging.info("Printing plots into pdf file" + filename)
        plots = []

        # Create evolution graphs for each parameters value
        j = 0
        last_it_scores = []
        # raw_scores = []
        for i in self.result['param_val']:
            if len(self.result["scores"][j]) <= 0:
                break
            min_ = []
            max_ = []
            mean_ = []
            for scores in self.result["scores"][j]:
                min_.append(min(scores) if len(scores) > 0 else 0.)
                mean_.append(sum(scores) / len(scores) if len(scores) > 0 else 0.)
                max_.append(max(scores) if len(scores) > 0 else 0.)

            iterations = range(len(self.result["scores"][j]))
            last_it_scores.append(self.result["scores"][j][-1])
            # raw_scores.append([item for sublist in self.result["scores"][j] for item in sublist])

            fig = plt.figure()
            plt.plot(iterations, min_, 'b-')
            plt.plot(iterations, mean_, 'g-')
            plt.plot(iterations, max_, 'r-')

            ax = fig.add_subplot(111)
            ax.set_title(self.result['abs_name'] + " = " + str(i))
            ax.yaxis.grid(True)
            ax.set_xticks([y for y in iterations], )
            ax.set_xlabel("Iteration number")
            ax.set_ylabel(self.result["ord_name"])

            plots.append(fig)

            j += 1

        # Create graph for final scores
        if len(last_it_scores) > 0:
            fig, ax = plt.subplots(1)
            ax.set_title("Score of the last iteration in function of " + self.result['abs_name'])
            ax.yaxis.grid(True)
            ax.set_xticks([y for y in self.result['param_val']], )
            ax.set_xlabel(self.result['abs_name'])
            ax.set_ylabel(self.result["ord_name"])
            bplot = ax.boxplot(last_it_scores,
                               notch=True,  # notch shape
                               vert=True,  # vertical box alignment
                               patch_artist=True)  # fill with color
            colors = ['pink', 'lightblue', 'lightgreen']
            for patch, color in zip(bplot['boxes'], colors):
                patch.set_facecolor(color)
            plots.append(fig)

            # Copy figures in a pdf
            pp = PdfPages(filename)
            for plot in plots:
                pp.savefig(plot)

            pp.close()
        else:
            logging.warning("Nothing to save in the pdf file")


class GeneticMetaOptimization(MetaOptimization):
    """
    This class provides tools to benchmark the Genetic Algorithm parameters
    """

    def __init__(self, opt, observable):
        """
        Init genetic meta optimization objects
        :param opt: Dictionary containing simulation parameters
        :param observable: Observable instance to get update from
        """

        MetaOptimization.__init__(self, opt, observable)

    def co_bench(self, min_=0, max_=1, step_=0.1):
        """
        Benchmark evolution of the cross-over parameter
        :param min_: Float Meta optimization loop parameter
        :param max_: Float Meta optimization loop parameter
        :param step_: Float Meta optimization loop parameter
        """

        # Configure result container
        self.result['abs_name'] = "Cross-Over Rate"
        self.result['ord_name'] = "Loss function scores"

        for i in np.arange(min_, max_ + step_, step_):
            self.result['param_val'].append(i)
            t_init = time.time()

            genetic = Genetic(self.opt, self.observable, cross_over_rate=i)
            genetic.start(**{"freq_stats": 2})

            self.result['scores'].append(genetic.results)
            self.result['configs'].append(genetic.configs)
            self.result['time'].append(time.time() - t_init)
            self.result['n_gen'].append(genetic.ga.getCurrentGeneration())
            if genetic.interruption:
                break

    def mut_bench(self, min_=0, max_=1, step_=0.1):
        """
        Benchmark evolution of the mutation parameter
        :param min_: Float Meta optimization loop parameter
        :param max_: Float Meta optimization loop parameter
        :param step_: Float Meta optimization loop parameter
        """

    def pop_size_bench(self):
        """Benchmark evolution of the extrema in the interval [-val val]"""

    def init_strat_bench(self):
        """Benchmark different initialization strategies"""

    def loss_fct_bench(self):
        """Benchmark different loss functions"""
