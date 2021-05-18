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
        self._serial.write(f"@1{chr(13)}".encode('ascii'))
        self._serial.write(f"1M{chr(13)}".encode('ascii'))

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
        print("start")
        self._serial.write(f"1H{chr(13)}".encode('ascii'))
        return self._serial.read(1)

    def stop(self):
        """Stop the pump.
        """
        print("stop")
        self._serial.write(f"1I{chr(13)}".encode('ascii'))
        return self._serial.read(1)

    def set_flowrate(self, val):
        val = str(int(val)).zfill(5)
        print(val)
        self._serial.write(f"1S{val}{chr(13)}".encode('ascii'))

    def get_flowrate(self):
        self._serial.write(f"1S{chr(13)}".encode('ascii'))
        return self._serial.readline()

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
