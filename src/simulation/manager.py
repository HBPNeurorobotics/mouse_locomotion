#!/usr/bin/python2

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
# File created by: Gabriel Urbain <gabriel.urbain@ugent.be>. February 2016
# Modified by: Dimitri Rodarie
##

import threading
from threading import Thread, Lock
from collections import deque
import logging
import time
import rpyc
from rpyc.utils.factory import DiscoveryError

from simulation import Simulation


class Manager(Thread, Simulation):
    """
    Manager class provides a high level interface to distribute a large number of
    simulation requests in a variable size computation cloud using tools like asynchonous
    request and registry server to monitor the network state via UDP requests.
    Usage:
            # Create and start Manager thread
            sm = Manager()
            sm.start()

            # Send simulation list and wait for results
            sim_list = [opt1 opt2]
            res_list = sm.simulate(sim_list)

            # Wait to terminate all work and stop Manager thread
            sm.stop()
    """

    def __init__(self, opt):
        """Create sim manager parameters and start registry server"""
        Simulation.__init__(self, opt)
        # Simulation list stacks
        # NB: FIFO: append answer on the left and remove the right one
        self.rqt = deque([])  # Request FIFO
        self.rsp = deque([])  # Response FIFO
        self.cloud_state = dict()  # dictionary of server state on the cloud. Entries are server hashes
        self.server_list = []  # list of active servers
        self.conn_list = []  # list of active RPYC connections
        # Simulation manager parameter
        self.rqt_n = 0
        self.sim_prun_t = 0.1
        self.mng_prun_t = 0.1
        self.mng_stop = False
        self.bg_async_threads = []
        self.reg_found = True
        self.terminated = False
        self.interrupted = False
        self.interrupt_to = 3
        self.server_dispo = False
        self.t_sim_init = 0
        self.sim_time = 0
        # Threading
        self.mutex_cloud_state = Lock()
        self.mutex_server_list = Lock()
        self.mutex_conn_list = Lock()
        self.mutex_rsp = Lock()
        self.mutex_rqt = Lock()
        Thread.__init__(self)
        logging.debug("Sim Manager initialization achieved. Number of active threads = " +
                      str(threading.active_count()))

    def __refresh_cloud_state(self):
        """Refresh the cloud state list using the registry server"""

        # Check network with rpyc registry thread
        self.mutex_server_list.acquire()
        try:
            self.server_list = rpyc.discover("BLENDERSIM")
            logging.debug("Server list " + str(self.server_list))
        except DiscoveryError:
            if self.reg_found:
                logging.info("Simulation servers not found on the network!")
                self.reg_found = False
            pass
        self.mutex_server_list.release()

        if self.server_list and not self.reg_found:
            logging.info("Simulation servers found on the network: " + str(self.server_list))
            self.reg_found = True

        # Lock cloud_state and server_list resources
        self.mutex_cloud_state.acquire()
        self.mutex_server_list.acquire()

        # Transform server list into a dict
        serv_list_dict = []
        for item in map(lambda x: ["address", x[0], "port", x[1], "n_threads", 0], self.server_list):
            serv_list_dict.append(dict(zip((item[0::2]), (item[1::2]))))
        serv_dict = dict(zip(map(hash, self.server_list), serv_list_dict))

        # Create sets for server_dict and cloud_state
        keys_serv_dict = set(serv_dict.keys())
        keys_cloud_state = set(self.cloud_state.keys())

        # Compare and update cloud_state set if needed
        for elem in keys_serv_dict.difference(keys_cloud_state):
            self.cloud_state[elem] = serv_dict[elem]
        for elem in keys_cloud_state.difference(keys_serv_dict):
            self.cloud_state.pop(elem)

        # Release ressources
        self.mutex_cloud_state.release()
        self.mutex_server_list.release()

        logging.debug("Server list " + str(self.server_list) + " cloud " + str(self.cloud_state))

    def __select_candidate(self):
        """Select the most suited candidate in the simulation cloud. """

        # We check registry_server for new server (adding it as empty one)
        self.__refresh_cloud_state()
        logging.debug("List of registered simulation computers: " + str(self.server_list))

        # We select an available server on the cloud_state list minimizing thread numbers
        self.mutex_cloud_state.acquire()
        for key in self.cloud_state:
            if self.cloud_state[key]["n_threads"] == 0:
                self.mutex_cloud_state.release()
                return key

        for key in self.cloud_state:
            if self.cloud_state[key]["n_threads"] == 1:
                self.mutex_cloud_state.release()
                return key

        self.mutex_cloud_state.release()
        return 0

    def response_sim(self, rsp):
        """Callback function called when a simulation has finished"""

        # We add the rsp from the simulation to the rsp list
        self.mutex_rsp.acquire()
        if not rsp.error:
            # Since rpyc convert some basic types into its own
            # we have to cast back to be able to use the classical functions
            cast = rsp.value
            if not type(rsp.value) == str:
                cast = eval(str(cast))
            self.rsp.appendleft(cast)
        else:
            logging.error('Manager.response_sim() : The server return an exception\n')
        self.mutex_rsp.release()

        self.mutex_conn_list.acquire()
        conn_found = False
        for item in self.conn_list:
            if rsp._conn.__hash__() == item["conn"].__hash__():
                conn_found = True
                server_hash = item["server"]

                # Decrease thread number in cloud_state dict
                if server_hash in self.cloud_state:
                    if not rsp.error:
                        logging.info("Response received from server " + str(self.cloud_state[server_hash]["address"]) +
                                     ":" + str(self.cloud_state[server_hash]["port"]) + " with " +
                                     str(self.cloud_state[server_hash]["n_threads"]) + " threads: " + str(rsp.value))
                    self.mutex_cloud_state.acquire()
                    self.cloud_state[server_hash]["n_threads"] -= 1
                    self.mutex_cloud_state.release()
                else:
                    logging.error("Server " + str(self.cloud_state[server_hash]["address"]) +
                                  ":" + str(self.cloud_state[server_hash]["address"]) +
                                  " not in the list anymore. Please check connection to ensure simulation results.")
                    # Close connection and listening thread
                    # As soon as we stop the thread, the function is directly exited because the callback
                    # function is handle by the thread itself

                logging.info("Deletion of connection: " + str(item["conn"].__hash__()) + "!")
                item["conn"].close()
                t = item["thread"]
                self.conn_list.remove(item)
                try:
                    t.stop()
                except Exception as e:
                    logging.error(str(e))
        self.mutex_conn_list.release()
        # If no candidate in the list
        if not conn_found:
            logging.error("Connection " + str(rsp._conn.__hash__()) +
                          " not in the list anymore. Please check connection to ensure simulation results.")

        return

    def simulate(self, sim_list):
        """Perform synchronous simulation with the given list and return response list"""

        # If rqt list is empty
        if not self.rqt:

            # Add to request list
            self.mutex_rqt.acquire()
            self.rqt.extendleft(sim_list)
            sim_n = len(self.rqt)
            self.mutex_rqt.release()

            # Check for simulation and interrupt when processed or interrupted
            to = 0
            to_init = 0
            while (len(self.rsp) != sim_n or self.rqt) and (not self.terminated) and \
                    (to < self.interrupt_to):
                if self.interrupted:
                    to = time.time() - to_init
                try:
                    time.sleep(self.sim_prun_t)
                except KeyboardInterrupt:
                    logging.warning("Simulation interrupted by user! Please clean up " +
                                    "remote computers.")
                    self.stop()
                    to_init = time.time()
                    self.interrupted = True

            # Create rsp buff and remove all rsp elements
            self.mutex_rsp.acquire()
            rsps = list(self.rsp)
            self.rsp = deque([])
            self.mutex_rsp.release()

            logging.warning("Simulation finished!")
            return rsps

        # If it isn't print error message and return
        else:
            logging.error("Simulation manager hasn't not finished yet with the " + str(self.rqt) +
                          " simulation. Try again later")

            return 0

    def get_cloud_state(self):
        """Return a dict with available machines in the network and their current usage"""

        return self.cloud_state

    def stop(self):
        """Stop the simulation manager"""
        Simulation.stop(self)

        # Stop managing loop
        self.mng_stop = True
        time.sleep(1)
        self.sim_time = time.time() - self.t_sim_init

    def start(self):
        """Start a simulation manager"""
        self.t_sim_init = time.time()
        logging.info("Start sim manager server with PID " + str(self.pid))
        time.sleep(1)
        Thread.start(self)

    def run(self):
        """Run the managing loop. Check rqt stack for simulation request. Select the candidate \
        server for simulation. Start simulation."""

        logging.info("Start Manager main loop")

        # Continue while not asked for termination or when there are candidates in the list
        # and a server to process them
        while (not self.mng_stop) or (self.rqt and self.server_dispo):

            if self.rqt:

                # Select a candidate server
                server_hash = self.__select_candidate()

                if server_hash != 0:

                    # We found a server
                    self.server_dispo = True
                    logging.info("Starting sim service on server: " +
                                 str(self.cloud_state[server_hash]["address"]) + ":" +
                                 str(self.cloud_state[server_hash]["port"]))

                    # Connect to candidate server
                    try:
                        conn = rpyc.connect(self.cloud_state[server_hash]["address"],
                                            self.cloud_state[server_hash]["port"])

                    except Exception as e:
                        logging.error("Exception when connecting:" + str(e))
                        pass

                    # Update the cloud_state list
                    self.mutex_cloud_state.acquire()
                    self.cloud_state[server_hash]["n_threads"] += 1
                    self.mutex_cloud_state.release()

                    # Create serving thread to handle answer
                    bgt = None
                    try:
                        bgt = rpyc.BgServingThread(conn)
                    except Exception as e:
                        logging.error("Exception in serving thread:" + str(e))
                        pass
                    if bgt is not None:
                        self.mutex_conn_list.acquire()
                        self.conn_list.append({"server": server_hash, "conn": conn,
                                               "thread": bgt})
                        self.mutex_conn_list.release()

                        # Create asynchronous handle
                        async_simulation = rpyc.async(conn.root.exposed_simulation)

                        try:
                            # Call asynchronous service
                            res = async_simulation(self.rqt[-1])

                            # Assign asynchronous callback
                            res.add_callback(self.response_sim)

                        except Exception as e:
                            logging.error("Exception from server:" + str(e))
                            pass

                        # Clear request from list: TODO: check if async_simulation don't need it anymore!
                        self.mutex_rqt.acquire()
                        self.rqt.pop()
                        self.mutex_rqt.release()
                        time.sleep(1)
                else:
                    self.server_dispo = False
                    time.sleep(self.mng_prun_t)

            else:
                time.sleep(self.mng_prun_t)

        logging.info("Simulation Manager has terminated properly!")
        self.terminated = True


def run_sim(opt):
    """Run a simple on shot simulation"""

    # Start manager
    manager = Manager(opt)
    manager.start()
    # Simulate
    if type(opt) != list:
        sim_list = [opt]
    else:
        sim_list = opt
    res_list = manager.simulate(sim_list)

    # Stop and display results
    manager.stop()
    time.sleep(1)
    rs_ls = ""
    for i in res_list:
        rs_ls += str(i) + " "
    logging.info("Results: " + str(rs_ls))
    logging.info("Simulation Finished!")
    return res_list
