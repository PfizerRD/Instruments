#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bronkhorst mass flow meter
"""
import argparse
import logging
import threading
# import serial
from random import random
from time import sleep
from instruments.instrument import Instrument
from instruments.bronkhorst.opc import Opc
from lib import helper_functions
from pdb import set_trace

__author__ = "Brent Maranzano"
__license__ = "MIT"


class Bronkhorst(Instrument, Opc):
    """Object to interact with Bronkhorst flow meter.
    """

    def __init__(self, config_file):
        """Sets an object attribute with defining the service parameters

        Arguments
        config_file (str): Filename containing the configuration parameters for
                            the instrument and services.
        """
        super(Bronkhorst, self).__init__(config_file)
        self._about = {
            "name": "Bronkhorst",
            "parameters": "mass flow rate"
         }
        self._data = {
            "measurement": 0
        }

    def _connect_instrument(self):
        """Connect to the serial instrument
        TODO
        """
        logger.info("connecting to serial")
        self._serial = "serial connection"

    def _update_data(self):
        """Update the instrument data
        TODO
        """
        logger.info("starting thread to update data")
        while True:
            """
            ser.write()
            ser.readline()
            """
            self._data = {
                "measurement": random()
            }
            logger.debug(self._data)
            sleep(2)

    def main(self):
        """Entry point
        """
        self._connect_instrument()
        threading.Thread(target=self._execute_queue, daemon=True).start()
        threading.Thread(target=self._update_data, daemon=True).start()
        self._start_services()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Service to call queued Bronkhorst serial methods."
    )
    parser.add_argument(
        "--parameter_file",
        help="YAML file containing parameters that define the services."
             " See docstring for example.",
        type=str,
        default="parameter_file.yml"
    )
    parser.add_argument(
        "--debug_level",
        help="debugger level (e.g. INFO, WARN, DEBUG, ...)",
        type=str,
        default="INFO"
    )
    args = parser.parse_args()
    helper_functions.setup_logger(level=args.debug_level)
    logger = logging.getLogger("bronkhorst")
    bronkhorst = Bronkhorst(args.parameter_file)
    bronkhorst.main()
