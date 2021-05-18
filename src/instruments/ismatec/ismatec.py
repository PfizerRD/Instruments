#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ismatec pump control
"""
import argparse
import logging
from random import random
from serial import Serial
from time import sleep
from instruments.instrument import Instrument

__author__ = "Brent Maranzano"
__license__ = "MIT"


logger = logging.getLogger("instrument.bronkhorst")


class Ismatec(Instrument):
    """Ismatec pump controller.
    """

    def __init__(self, config_file):
        """Sets an object attribute with defining the service parameters

        Arguments
        config_file (str): Filename containing the configuration parameters for
                            the instrument and services.
        """
        super(Ismatec, self).__init__(config_file)
        self._about = {
            "name": "Ismatec",
            "parameters": "rpm"
         }
        self._data = {
            "measurement": 0
        }

    def _connect_instrument(self):
        """Connect to the serial instrument

        Arguments
        params (dict): Parameters to start instrument
        """
        logger.info("connecting to serial")
        self._serial = Serial(**self._params["serial"])

    def _update_data(self):
        """Update the instrument data
        TODO
        """
        logger.info("starting thread to update data")
        while True:
            """
            """
            self._data = {
                "measurement": random()
            }
            logger.debug(self._data)
            sleep(2)

    def start(self):
        """Start the pump.
        """
        self._serial.write(f"3H{chr(13)}".encode('ascii'))
        return True

    def stop(self):
        """Stop the pump.
        """
        self._serial.write(f"3I{chr(13)}".encode('ascii'))
        return True

    def set_flowrate(self, val):
        return val

    def get_flowrate(self):
        return 3

    def main(self):
        """Entry point
        """
        self._connect_instrument()
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
    ismatec = Ismatec(args.parameter_file)
    ismatec.main()
