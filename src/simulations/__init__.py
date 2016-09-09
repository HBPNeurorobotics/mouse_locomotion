import rpyc

PROTOCOL_CONFIG = rpyc.core.protocol.DEFAULT_CONFIG
rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True

from .registry import Registry
from servers import *
from clients import *
