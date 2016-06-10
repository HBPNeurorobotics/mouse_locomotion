import json
import os


class JSonUtils:
    def __init__(self):
        pass

    @staticmethod
    def read_json_file(filename, logger):
        if os.path.isfile(filename):
            try:
                with open(filename, 'r') as data_file:
                    return json.load(data_file)
            except Exception as e:
                logger.error("Can't load save file: " + str(e))

        else:
            logger.error("Can't open the file " + str(filename) + ". The file doesn't exist.")
        return {}

    @staticmethod
    def write_json_file(filename, data):
        with open(filename, 'w') as f:
            json.dump(data, f)
