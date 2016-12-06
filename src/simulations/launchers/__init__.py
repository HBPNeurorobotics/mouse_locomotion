import os.path
import sys
from os.path import dirname, realpath

if sys.version_info < (3, 0):
    import ConfigParser
else:
    from configparser import ConfigParser

# Add src folder to path
SRC = dirname(dirname(dirname(realpath(__file__)))).replace("\\", "/")
ROOT = dirname(SRC).replace("\\", "/")
sys.path.append(SRC)

__defaults = ConfigParser.ConfigParser()
__defaults.read(os.path.join(SRC, 'config.ini'))
DEF_OPT = eval(__defaults.get('defaults', 'DEF_OPT'))

from .serverLauncher import ServerLauncher
from .clientLauncher import ClientLauncher
from .registryLauncher import RegistryLauncher
