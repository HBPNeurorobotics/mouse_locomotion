import os
import pickle


class PickleUtils:
    def __init__(self):
        pass

    @staticmethod
    def save(filename, element):
        with open(filename, 'wb') as f:
            pickle.dump(element, f, protocol=2)

    @staticmethod
    def load(filename, logger):
        """Load the result dictionary from file"""

        if os.path.isfile(filename):
            try:
                f = open(filename, 'rb')
                result_dict = pickle.load(f)
                f.close()
                return result_dict
            except Exception as e:
                logger.error("Can't load save file: " + str(e))

        else:
            logger.error("Can't open the file " + str(filename) + ". The file doesn't exist.")
        return {}

    @staticmethod
    def del_file(filename, logger):
        if os.path.isfile(filename):
            try:
                os.remove(filename)
            except Exception as e:
                logger.error("Can't delete save file: " + str(e))

        else:
            logger.error("Can't find the file " + str(filename) + ". The file doesn't exist.")

    @staticmethod
    def del_all_files(directory, extension, logger):
        for file_ in os.listdir(directory):
            if file_.endswith("." + extension):
                PickleUtils.del_file(file_, logger)
