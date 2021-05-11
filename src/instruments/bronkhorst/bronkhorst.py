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


logger = logging.getLogger(__name__)


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
        print(self._params["serial"])
        self._serial = "serial connection"

    def _update_data(self):
        """Update the instrument data
        ser.write()
        data = ser.readline()
        """
        while True:
            self._data = {
                "measurement": random()
            }
            sleep(2)

    def main(self):
        """Start the instrument.
        """
        self._connect_instrument()
#        threading.Thread(target="self._update_data", daemon=True).start()
        self.start()


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
    helper_functions.setup_logger(args.logger_file, args.debug_level)
    bronkhorst = Bronkhorst(args.parameter_file)
    bronkhorst.main()
