#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run a simulated controller with OPC UA server for testing.
"""
import argparse
import logging
from random import random
import threading
from opcua import Server, ua
from time import sleep
from lib import helper_functions

__author__ = 'Brent Maranzano'
__license__ = 'MIT'


logger = logging.getLogger("instrument.simulated_controller")


class SimulatedController(Server):
    """Simulated controller with OPC UA server for testing.
    class attributes added to opcua.Server:
        _server
        _nodes
    """

    def __init__(self, parameter_file):
        """Create a Fake OPC UA server with updating nodes.

        Arguments
        parameter_file (str): Filename for the service parameters.
        """
        super(SimulatedController, self).__init__()
        self._server = None
        self._nodes = dict()
        self._params = self._get_parameters(parameter_file)

    def _get_parameters(self, config_file):
        """Read and parse the yaml file containing the
        configuration parameters to start the services.

        Arguments
        config_file (str): Filename containing parameters formatted
                            as yaml.

        returns (dict): Parameters.
        """
        params = helper_functions.yaml_to_dict(config_file)
        logger.info("retrieved service parameters from file")
        return params

    def _create_nodes(self, idx, nodes):
        """Create nodes defined by params.
        """
        for node_obj, node_group in nodes.items():
            obj = self._server.nodes.objects.add_object(idx, node_obj)
            for name, attr in node_group.items():
                node = obj.add_variable(idx, name, attr["value"],
                                        getattr(ua.VariantType, attr["type"]))
                node.set_writable() if attr["writable"] else node.set_read_only()
                self._nodes[name] = node

    def run(self):
        """Instantiate and run server
        """
        logger.info("starting OPC service")
        params = self._params
        self._server = Server()
        self._server.set_endpoint(params["endpoint"])
        self._server.set_server_name(params["name"])
        idx = self._server.register_namespace(params["uri"])
        self._create_nodes(idx, params["nodes"])
        self._server.start()
        self._start_simulations()

    def _start_simulations(self):
        """Start the simulations for the various nodes.
        """
        logger.info("starting simulation threads")
        try:
            watchdog = threading.Thread(
                target=self._update_WATCHDOG_CONTROLLER, daemon=True)
            watchdog.start()
            for i in range(10):
                logger.info("set flow")
                self._nodes["SETFLOW_CONTROLLER"].set_value(random())
                sleep(2)
                logger.info("start")
                self._nodes["START_CONTROLLER"].set_value(True)
                self._nodes["STOP_CONTROLLER"].set_value(False)
                sleep(10)
                logger.info("stop")
                self._nodes["START_CONTROLLER"].set_value(False)
                self._nodes["STOP_CONTROLLER"].set_value(True)
            logger.info("complete")
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt")
        finally:
            # run the server indefinetely for evaluation
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                pass
            self._server.stop()
            logger.info("shutdown")

    def _update_WATCHDOG_CONTROLLER(self):
        """Watchdog thread"""
        logger.info("starting WATCHDOG_CONTROLLER thread")
        while True:
            self._nodes["WATCHDOG_CONTROLLER"].set_value(
                not self._nodes["WATCHDOG_CONTROLLER"].get_value()
            )
            sleep(5)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="simulated OPC UA server")
    parser.add_argument(
        "--parameter_file",
        help="YAML file defining parameters for server",
        type=str,
        default="./parameter_file.yml"
    )
    parser.add_argument(
        "--debug_level",
        help="debugger level (e.g. INFO, WARN, DEBUG, ...)",
        type=str,
        default="INFO"
    )
    args = parser.parse_args()
    controller = SimulatedController(args.parameter_file)
    controller.run()
