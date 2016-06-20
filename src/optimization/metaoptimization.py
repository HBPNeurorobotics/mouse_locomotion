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

import logging
import numpy as np
import matplotlib

import time
from genetic import Genetic
from optimization import Optimization
from utils import PickleUtils

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


class MetaOptimization(Optimization):
    """
    This class provides tools to modify the optimization parameters or methods,
    start different optimisation processes, benchmark and plot them
    Usage:
                # Create meta optimization
                mga = GeneticMetaOptimization(opt, observable)

                # Run cross-over benchmark
                mga.co_bench()
    """

    def __init__(self, opt, observable, minimum=0, max_iteration=1, step=0.1):
        """
        Init MetaOptimization class by creating a generic container to exploit
        different results
        :param opt: Dictionary containing simulation parameters
        :param observable: Observable instance to get update from
        :param minimum: Float Meta optimization loop parameter
        :param max_iteration: Float Meta optimization loop parameter
        :param step: Float Meta optimization loop parameter
        """

        Optimization.__init__(self, opt, None, max_iteration)
        self.res_list = dict()
        self.res_list['n_gen'] = []
        self.res_list['time'] = []
        self.res_list['abs_name'] = "Abscissas"
        self.res_list['ord_name'] = "Ordinates"
        self.res_list['scores'] = []
        self.res_list['configs'] = []
        self.res_list['param_val'] = []

        self.observable = observable
        self.minimum = minimum
        self.step = step
        self.t_init = 0

    def display(self):
        """Print the results"""

        res = "\nMeta Optimization results\n"
        res += "--------------------------\n\n"
        j = 0
        for i in self.res_list['param_val']:
            min_ = ""
            max_ = ""
            mean_ = ""
            for scores in self.res_list["scores"][j]:
                min_ += str(min(scores)) if len(scores) > 0 else str(0.) + " "
                mean_ += str(sum(scores) / len(scores)) if len(scores) > 0 else str(0.) + " "
                max_ += str(max(scores)) if len(scores) > 0 else str(0.) + " "
            res += "## " + self.res_list['abs_name'] + " = " + str(i) + " ##\n"
            res += "\tSimulation time: " + str(self.res_list['time'][j]) + "\n"
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
        for i in self.res_list['param_val']:
            if len(self.res_list["scores"][j]) <= 0:
                break
            min_ = []
            max_ = []
            mean_ = []
            for scores in self.res_list["scores"][j]:
                min_.append(min(scores) if len(scores) > 0 else 0.)
                mean_.append(sum(scores) / len(scores) if len(scores) > 0 else 0.)
                max_.append(max(scores) if len(scores) > 0 else 0.)

            iterations = range(len(self.res_list["scores"][j]))
            last_it_scores.append(self.res_list["scores"][j][-1])
            # raw_scores.append([item for sublist in self.result["scores"][j] for item in sublist])

            fig = plt.figure()
            plt.plot(iterations, min_, 'b-')
            plt.plot(iterations, mean_, 'g-')
            plt.plot(iterations, max_, 'r-')

            ax = fig.add_subplot(111)
            ax.set_title(self.res_list['abs_name'] + " = " + str(i))
            ax.yaxis.grid(True)
            ax.set_xticks([y for y in iterations], )
            ax.set_xlabel("Iteration number")
            ax.set_ylabel(self.res_list["ord_name"])

            plots.append(fig)

            j += 1

        # Create graph for final scores
        if len(last_it_scores) > 0:
            fig, ax = plt.subplots(1)
            ax.set_title("Score of the last iteration in function of " + self.res_list['abs_name'])
            ax.yaxis.grid(True)
            ax.set_xticks([y for y in self.res_list['param_val']], )
            ax.set_xlabel(self.res_list['abs_name'])
            ax.set_ylabel(self.res_list["ord_name"])
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

    def update(self, **kwargs):
        """
        Retrieve results from the simulation and update parameters
        Raise Exception if one of the required parameter is missing
        :param kwargs: Dictionary parameter used for update
        """

        if "interruption" in kwargs.keys() and type(kwargs["interruption"]) == bool:
            self.interruption = kwargs["interruption"]

        if "res" in kwargs.keys():
            self.res_list['scores'] = kwargs["res"]
        else:
            raise Exception("Parameter 'res' missing in notification")
        if "configs" in kwargs.keys():
            self.res_list['configs'].append(kwargs["configs"])
        else:
            raise Exception("Parameter 'configs' missing in notification")
        if "current_gen" in kwargs.keys():
            self.res_list['n_gen'].append(kwargs["current_gen"])
        else:
            raise Exception("Parameter 'n_gen' missing in notification")
        self.res_list['time'].append(time.time() - self.t_init)


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

    def co_bench(self):
        """
        Benchmark evolution of the cross-over parameter
        """

        # Configure result container
        self.res_list['abs_name'] = "Cross-Over Rate"
        self.res_list['ord_name'] = "Loss function scores"

        for i in np.arange(self.minimum, self.max_iteration + self.step, self.step):
            self.res_list['param_val'].append(i)

            genetic = Genetic(self.opt, self.observable, cross_over_rate=i)
            genetic.add_observer(self)
            genetic.start(**{"freq_stats": 2})

            if self.interruption:
                break

        # Save, display and plot results
        PickleUtils.save(self.save_directory + "default.mor", self.res_list)
        self.display()
        self.plot(self.save_directory + "default.pdf")
        PickleUtils.del_all_files(self.save_directory, "qsm")

    def mut_bench(self):
        """Benchmark evolution of the mutation parameter"""

    def pop_size_bench(self):
        """Benchmark evolution of the extrema in the interval [-val val]"""

    def init_strat_bench(self):
        """Benchmark different initialization strategies"""

    def loss_fct_bench(self):
        """Benchmark different loss functions"""
