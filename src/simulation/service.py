from simulation import Simulation
from simulation import Blender
import logging
import sys
from rpyc import Service
from rpyc.utils.registry import REGISTRY_PORT
from rpyc.utils.server import ThreadedServer


class SimService(Service, Simulation):
    """
    SimManager class provides a services server to listen to external requests and start a Blender
    simulation remotely and asynchroously. Results are sent back to SimManager
    Usage:
            # Create and start SimService thread
            s = ThreadedServer(SimService, port=18861, auto_register=True)
            s.start()
    """

    ALIASES = ["BLENDERSIM", "BLENDER", "BLENDERPLAYER"]

    def __init__(self, opt):
        Simulation.__init__(self, opt)

    def start(self):
        """Start a service server"""
        Simulation.start(self)
        logging.info("Start registry server on address: " + str(self.ipaddr) + ":" + str(REGISTRY_PORT))
        try:
            t = ThreadedServer(SimService, port=18861, auto_register=True)
            t.start()
        except KeyboardInterrupt:
            t.stop()
            logging.warning("SINGINT caught from user keyboard interrupt")
            sys.exit(1)

    def on_connect(self):
        self.a = 4
        pass

    def on_disconnect(self):
        pass

    def exposed_simulation(self, opt_):  # this is an exposed method

        # Perform simulation
        logging.info("Processing simulation request")
        s = Blender(opt_, "BLENDERPLAYER")
        s.start()
        logging.info("Simulation request processed")

        return s.get_results()
