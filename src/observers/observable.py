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
# April 2016
##


class Observable:
    """
    Observer/Observable pattern
    Observable Class is used to notify Observers of an update
    """

    def __init__(self):
        """Class initialization"""

        self.__observers = []

    def get_observers(self):
        """
        Get observers list
        :return: Observer List
        """

        return self.__observers

    def add_observer(self, observer):
        """
        Add observer to the list
        :param observer: Observer to add
        """

        self.__observers.append(observer)

    def add_observers(self, observers):
        """
        Add a list of observers to the list
        :param observers: Observer list
        """

        for o in observers:
            self.add_observer(o)

    def remove_observer(self, observer):
        """
        Remove one observer from the list
        :param observer: Observer to remove
        """

        self.__observers.remove(observer)

    def remove_observers(self, observers):
        """
        Remove a list of observers from the list
        :param observers: Observer list
        """

        for o in observers:
            self.remove_observer(o)

    def replace_observer(self, ex_observer, new_observer):
        """
        Replace one observer of the list with an other
        :param ex_observer: Observer to remove
        :param new_observer: Observer to add
        """

        self.remove_observer(ex_observer)
        self.add_observer(new_observer)

    def notify_observers(self, **kwargs):
        """
        Notify observers for an update
        :param kwargs: Dictionary parameter for the update
        """

        for observer in self.__observers:
            observer.update(**kwargs)
