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
    def load(file, logger):
        """Load the result dictionary from file"""

        if os.path.isfile(file):
            try:
                f = open(file, 'rb')
                result_dict = pickle.load(f)
                f.close()
                return result_dict
            except Exception as e:
                logger.error("Can't load save file: " + str(e))

        else:
            logger.error("Can't open the file " + str(file) + ". The file doesn't exist.")
        return {}
