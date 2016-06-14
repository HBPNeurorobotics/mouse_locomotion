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

import math
import rpyc
from rpyc.utils.factory import DiscoveryError
from observers import Observable
from simulation import Simulation
import sys

if sys.version_info[:2] < (3, 4):
    import common
else:
    from simulation import common


class Manager(Simulation, Observable):
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
        Observable.__init__(self)
        # Simulation list stacks
        # NB: FIFO: append answer on the left and remove the right one
        self.rqt = deque([])  # Request FIFO
        self.rsp = deque([])  # Response FIFO
        self.cloud_state = dict()  # dictionary of server state on the cloud. Entries are server hashes
        self.server_list = []  # list of active servers
        self.conn_list = []  # list of active RPYC connections
        # Server parameters
        self.max_CPU_percent_use = opt["cpu_use"]
        self.max_memory_percent_use = opt["memory_use"]
        self.simulator = opt["simulator"]
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
        self.sim_timeout = opt["timeout"]
        self.results = {}
        # Threading
        self.mutex_cloud_state = Lock()
        self.mutex_conn_list = Lock()
        self.mutex_rsp = Lock()
        self.mutex_rqt = Lock()
        self.mutex_res = Lock()
        self.lock_test_server = Lock()

        self.thread = None
        logging.debug("Sim Manager initialization achieved. Number of active threads = " +
                      str(threading.active_count()))

    def __refresh_cloud_state(self):
        """Refresh the cloud state list using the registry server"""

        # Check network with rpyc registry thread
        try:
            self.server_list = rpyc.discover("BLENDERSIM")
            logging.debug("Server list " + str(self.server_list))
        except DiscoveryError:
            if self.reg_found:
                logging.info("Simulation servers not found on the network!")
                self.reg_found = False
                self.server_list = []

        if self.server_list and not self.reg_found:
            logging.info("Simulation servers found on the network: " + str(self.server_list))
            self.reg_found = True

        # Transform server list into a dict
        serv_list_dict = []
        for item in map(lambda x: ["address", x[0], "port", x[1], "n_threads", 0, "status", False], self.server_list):
            serv_list_dict.append(dict(zip((item[0::2]), (item[1::2]))))
        serv_dict = dict(zip(map(hash, self.server_list), serv_list_dict))

        # Create sets for server_dict and cloud_state
        keys_serv_dict = set(serv_dict.keys())
        keys_cloud_state = set(self.cloud_state.keys())

        # Compare and update cloud_state set if needed
        for elem in keys_serv_dict.difference(keys_cloud_state):
            if len(self.rqt) > 0:
                try:
                    self.request_server(elem, serv_dict[elem], self.rqt[0], "Test")
                except Exception as e:
                    logging.error("Exception during test on the server " +
                                  serv_dict[elem]["address"] + ":" +
                                  serv_dict[elem]["port"] + "\n" +
                                  "The server will now be ignored\n" +
                                  "Details: " + str(e))
                self.mutex_cloud_state.acquire()
                self.cloud_state[elem] = serv_dict[elem]
                self.mutex_cloud_state.release()

        for elem in keys_cloud_state.difference(keys_serv_dict):
            self.mutex_cloud_state.acquire()
            self.cloud_state.pop(elem)
            self.mutex_cloud_state.release()

        logging.debug("Server list " + str(self.server_list) + " cloud " + str(self.cloud_state))

    def __select_candidate(self):
        """Select the most suited candidate in the simulation cloud. """

        # We check registry_server for new server (adding it as empty one)
        self.__refresh_cloud_state()
        logging.debug("List of registered simulation computers: " + str(self.server_list))

        # We select an available server on the cloud_state list minimizing thread numbers
        self.check_sim()
        self.mutex_cloud_state.acquire()
        # Select the server with the largest number of simulations available
        if len(self.cloud_state) >= 2:
            self.cloud_state = sorted(self.cloud_state.items(), key=lambda x: x[1]["n_threads"], reverse=True)
        for key in self.cloud_state:
            if self.cloud_state[key]["n_threads"] > 0 and self.cloud_state[key]["status"]:
                self.mutex_cloud_state.release()
                return key
        self.mutex_cloud_state.release()
        return 0

    @staticmethod
    def rpyc_casting(rsp):
        cast = rsp.value
        if not type(rsp.value) == str:
            cast = eval(str(cast))
        return cast

    def response_simulation(self, rsp):
        """Callback function called when a simulation has finished"""

        def function(server_hash, rsp_):
            # We add the rsp from the simulation to the rsp list
            self.mutex_rsp.acquire()
            # Since rpyc convert some basic types into its own
            # we have to cast back to be able to use the classical functions
            self.rsp.appendleft(rsp_)
            self.mutex_rsp.release()

            # Notify observer about the new result
            self.notify_observers(**{"res": rsp_})

            # Decrease thread number in cloud_state dict
            self.mutex_cloud_state.acquire()
            self.cloud_state[server_hash]["n_threads"] += 1
            self.mutex_cloud_state.release()

        self.process_callback(rsp, function)

    def response_test(self, rsp):
        def function(server_id, rsp_):
            cpu_capacity = (self.max_CPU_percent_use - rsp_["common"]["CPU"]) / rsp_[self.simulator]["CPU"]
            memory_capacity = (self.max_memory_percent_use - rsp_["common"]["memory"]) / rsp_[self.simulator]["memory"]
            nb_thread = math.floor(min(cpu_capacity, memory_capacity))
            if nb_thread > 0:
                self.mutex_cloud_state.acquire()
                self.cloud_state[server_id]["status"] = True
                self.cloud_state[server_id]["n_threads"] = nb_thread
                logging.info("The server " + str(self.cloud_state[server_id]["address"]) +
                             ":" + str(self.cloud_state[server_id]["port"]) +
                             " is now available for a maximum of " + str(nb_thread) + " simulation(s).")
                self.mutex_cloud_state.release()

        self.process_callback(rsp, function)

    def process_callback(self, rsp, function):
        if not rsp.error:
            conn_found = False
            for item in self.conn_list:
                if rsp._conn.__hash__() == item["conn"].__hash__():
                    conn_found = True
                    server_id = item["server"]
                    if server_id in self.cloud_state:
                        function(server_id, self.rpyc_casting(rsp))
                        logging.info("Response received from server " + str(self.cloud_state[server_id]["address"]) +
                                     ":" + str(self.cloud_state[server_id]["port"]))

                        # Remove clean simulation callback from the list
                        self.del_clean_simulation(server_id, rsp)
                    else:
                        logging.error("Server " + str(server_id) +
                                      " not in the list anymore. Please check connection to ensure simulation results.")
                    # Close connection and listening thread
                    # As soon as we stop the thread, the function is directly exited because the callback
                    # function is handle by the thread itself

                    logging.info("Deletion of connection: " + str(item["conn"].__hash__()) + "!")
                    item["conn"].close()
                    t = item["thread"]
                    self.mutex_conn_list.acquire()
                    self.conn_list.remove(item)
                    self.mutex_conn_list.release()
                    t._active = False
                    break

            # If no candidate in the list
            if not conn_found:
                logging.error("Connection " + str(rsp._conn.__hash__()) +
                              " not in the list anymore. Please check connection to ensure simulation results.")
        else:
            logging.error('Manager.process_callback() : The simulation server return an exception\n')

    def simulate(self, sim_list):
        """Perform synchronous simulation with the given list and return response list"""

        # If rqt list is empty
        if not self.rqt:

            # Create a request list and reset results
            self.mutex_rqt.acquire()
            self.rqt.extendleft(sim_list)
            sim_n = len(self.rqt)
            self.mutex_rqt.release()
            self.mutex_rsp.acquire()
            self.rsp = deque([])
            self.mutex_rsp.release()
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
                    self.notify_observers(**{"interruption": True})
                    self.stop()
                    to_init = time.time()
                    self.interrupted = True

            # Create rsp buff
            rsps = list(self.rsp)
            logging.warning("Simulation finished!")
            return rsps

        # If it isn't print error message and return
        else:
            logging.error("Simulation manager hasn't not finished yet with the " + str(self.rqt) +
                          " simulation. Try again later")

            return 0

    def stop(self):
        """Stop the simulation manager"""
        Simulation.stop(self)

        # Stop managing loop
        self.mng_stop = True
        self.sim_time = time.time() - self.t_sim_init
        if self.thread.is_alive():
            self.thread.join()

    def start(self):
        """Start a simulation manager"""
        self.t_sim_init = time.time()
        logging.info("Start sim manager server with PID " + str(self.pid))
        time.sleep(1)
        self.terminated = False
        self.mng_stop = False
        self.thread = Thread(target=self.run)
        self.thread.start()

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
                    try:
                        self.request_server(server_hash, self.cloud_state[server_hash], self.rqt[-1], "Simulation")
                    except Exception as e:
                        raise Exception("Exception during simulation on the server " +
                                        self.cloud_state[server_hash]["address"] + ":" +
                                        self.cloud_state[server_hash]["port"] + "\n" + str(e))
                    # Update the cloud_state list
                    self.mutex_cloud_state.acquire()
                    self.cloud_state[server_hash]["n_threads"] -= 1
                    self.mutex_cloud_state.release()

                    # Clear request from list:
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

    def del_clean_simulation(self, server_hash, res):
        if server_hash in self.results:
            server = self.results[server_hash]
            for simulation in server:
                if res == simulation[1] and res.ready:
                    self.mutex_res.acquire()
                    del self.results[server_hash][server.index(simulation)]
                    self.mutex_res.release()
                    break

    def check_sim(self):
        for server_hash, simulations in self.results.items():
            clean = True
            for simulation in simulations:
                result = simulation[1]
                if result.expired or result.error:
                    clean = False
                    break
            if not clean:
                self.mutex_rqt.acquire()
                for simulation in simulations:
                    rqt = simulation[0]
                    self.rqt.append(rqt)
                self.mutex_rqt.release()

                self.mutex_cloud_state.acquire()
                logging.error("Timeout from server: " +
                              str(self.cloud_state[server_hash]["address"]) + ":" +
                              str(self.cloud_state[server_hash]["port"]))
                self.cloud_state[server_hash]["status"] = False
                self.mutex_cloud_state.release()

                self.mutex_res.acquire()
                del self.results[server_hash]
                self.mutex_res.release()

    def request_server(self, server_id, server, rqt, service):
        # Connect to the server
        try:
            conn = rpyc.connect(server["address"],
                                server["port"])
        except Exception as e:
            exception = "Exception when connecting: " + str(e)
            logging.error(exception)
            raise Exception(exception)

        # Create serving thread to handle answer
        try:
            bgt = rpyc.BgServingThread(conn)
        except Exception as e:
            exception = "Exception in serving thread: " + str(e)
            logging.error(exception)
            conn.close()
            raise Exception(exception)
        self.mutex_conn_list.acquire()
        self.conn_list.append({"server": server_id, "conn": conn,
                               "thread": bgt})
        self.mutex_conn_list.release()

        # Create asynchronous handle
        if service in common.REQUESTS:
            logging.info("Starting " + common.REQUESTS[service] + " service on server: " +
                         str(server["address"]) + ":" +
                         str(server["port"]))
            async_simulation = rpyc.async(eval("conn.root.exposed_" + common.REQUESTS[service]))
            callback = eval("self.response_" + common.REQUESTS[service])
        else:
            exception = "Manager.request_server: Service unhandled by the manager"
            logging.error(exception)
            conn.close()
            bgt._active = False
            raise Exception(exception)

        try:
            res = async_simulation(rqt)
            res.set_expiry(self.sim_timeout)

            # Assign asynchronous callback
            res.add_callback(callback)
        except Exception as e:
            exception = "Exception from server: " + str(e)
            logging.error(exception)
            conn.close()
            bgt._active = False
            raise Exception(exception)

        # Add result to the result list to be handled after
        self.mutex_res.acquire()
        if server_id not in self.results:
            self.results[server_id] = []
        self.results[server_id].append([rqt, res])
        self.mutex_res.release()
