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


class Observable:
    def __init__(self):
        self.observers = []

    def get_observers(self):
        return self.observers

    def add_observer(self, observer):
        self.observers.append(observer)

    def add_observers(self, observers):
        for o in observers:
            self.add_observer(o)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def remove_observers(self, observers):
        for o in observers:
            self.remove_observer(o)

    def replace_observer(self, ex_observer, new_observer):
        self.remove_observer(ex_observer)
        self.add_observer(new_observer)

    def notify_observers(self, **kwargs):
        for observer in self.observers:
            observer.update(**kwargs)
