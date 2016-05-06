class Optimization:
    def __init__(self, opt, population_size, stop_thresh, max_iteration):
        self.opt = opt
        self.population_size = population_size
        self.best_solutions_list = []
        self.stop_thresh = stop_thresh
        self.max_iteration = max_iteration

    def __eval_fct(self, specimen):
        pass

    def __conv_fct(self, algorithm):
        pass
