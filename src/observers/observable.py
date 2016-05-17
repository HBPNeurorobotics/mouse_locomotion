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
