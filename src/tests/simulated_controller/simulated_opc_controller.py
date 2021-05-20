#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run a simulated controller with OPC UA server for testing.
"""
import argparse
import logging
from random import random
import threading
from services.opc import server
from time import sleep

__author__ = 'Brent Maranzano'
__license__ = 'MIT'


logger = logging.getLogger("instrument.simulated_controller")


class SimulatedOpcController(object):
    """Simulated controller with OPC UA server for testing.
    """

    def __init__(self):
        """Create a Fake OPC UA server with updating nodes.
        """
        pass

    def create_server(self, parameter_file):
        """Create an OPC UA server.

        Arguments
        parameter_file (str): Name of YAML file for server configuration.
        """
        self._server = server.OpcServer.from_parameter_file(parameter_file)
        self._server.run()

    def simulate(self):
        """Start the simulations for the various nodes.
        """
        nodes = self._server.get_nodes()
        logger.info("starting simulation threads")
        try:
            watchdog = threading.Thread(
                target=self._update_WATCHDOG_CONTROLLER, daemon=True)
            watchdog.start()
            for i in range(10):
                logger.info("set flow")
                nodes["SET_FLOWRATE_CONTROLLER"].set_value(random()*1000)
                sleep(2)
                logger.info("start")
                nodes["STOP_CONTROLLER"].set_value(False)
                nodes["START_CONTROLLER"].set_value(True)
                sleep(10)
                logger.info("stop")
                nodes["START_CONTROLLER"].set_value(False)
                nodes["STOP_CONTROLLER"].set_value(True)
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
        nodes = self._server.get_nodes()
        logger.info("starting WATCHDOG_CONTROLLER thread")
        while True:
            nodes["WATCHDOG_CONTROLLER"].set_value(
                not nodes["WATCHDOG_CONTROLLER"].get_value()
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
    controller = SimulatedOpcController()
    controller.create_server(args.parameter_file)
    controller.simulate()
