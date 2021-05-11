#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run a simulated controller with OPC UA server for testing.
"""
import argparse
import logging
import logging.config
import coloredlogs
import random
import threading
from opcua import Server, ua
from time import sleep
from pdb import set_trace
from lib import helper_functions

__author__ = 'Brent Maranzano'
__license__ = 'MIT'


def setup_logger(config_file, level):
    """Start the logger
    """
    config = helper_functions.yaml_to_dict(config_file)
    logging.config.dictConfig(config)
    coloredlogs.install(level=level)
    logger = logging.getLogger(__name__)
    return logger


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
        #params = helper_functions.dict_to_namespace(params)

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
        """Simulate changes in the server.
        """
        params = self._params
        self._server = Server()
        self._server.set_endpoint(params["endpoint"])
        self._server.set_server_name(params["name"])
        idx = self._server.register_namespace(params["uri"])
        self._create_nodes(idx, params["nodes"])
        self._server.start()
        watchdog = threading.Thread(target=self._update_watchdog, daemon=True)
        pat = threading.Thread(target=self._update_float1_pat, daemon=True)
        watchdog.start()
        pat.start()
        logger.info("OPC server running")
        try:
            while True:
                pass
                sleep(10)
        except KeyboardInterrupt:
            self._logger.debug("KeyboardInterrupt")
            self._watchdog_thread.join()
        finally:
            self.server.stop()

    def _update_watchdog(self):
        """Watchdog thread"""
        logger.info("starting watchdog")
        while True:
            self._nodes["WATCHDOG_DLV"].set_value(
                not self._nodes["WATCHDOG_DLV"].get_value()
            )
            sleep(5)

    def _update_float1_pat(self):
        """PAT thread"""
        logger.info("starting float thread")
        while True:
            self._nodes["FLOAT1_PAT"].set_value(random.random())
            sleep(10)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="simulated OPC UA server")
    parser.add_argument(
        "--parameter_file",
        help="YAML file defining parameters for server",
        type=str,
        default="./parameter_file.yml"
    )
    parser.add_argument(
        "--logger_file",
        help="full path name to the logger_conf.yml file",
        type=str,
        default="./logger_conf.yml"
    )
    parser.add_argument(
        "--debug_level",
        help="debugger level (e.g. INFO, WARN, DEBUG, ...)",
        type=str,
        default="INFO"
    )
    args = parser.parse_args()
    logger = setup_logger(args.logger_file, args.debug_level)
    controller = SimulatedController(args.parameter_file)
    controller.run()
