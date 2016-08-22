import logging
import os


class FileUtils:
    """
    Abstract utility class to manipulate files
    """

    @staticmethod
    def read_file(filename):
        return {}

    @staticmethod
    def write_file(filename, data):
        pass

    @staticmethod
    def del_file(filename):
        """
        Delete a file if possible
        :param filename: String path to the file
        """

        if os.path.isfile(filename):
            try:
                os.remove(filename)
            except Exception as e:
                logging.error("Can't delete save file: " + str(e))

        else:
            logging.error("Can't find the file " + str(filename) + ". The file doesn't exist.")

    @staticmethod
    def del_all_files(directory, extension):
        """
        Delete a list of files if possible
        :param directory: String path to the directory containing the files
        :param extension: String extension of the files. Should start with a dot.
        """

        for file_ in os.listdir(directory):
            if file_.endswith("." + extension):
                FileUtils.del_file(directory + file_)
