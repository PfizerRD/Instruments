#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IKA overhead stirrer.
"""
import argparse
import logging
from serial import Serial
from instruments.instrument import Instrument
from lib import helper_functions


__author__ = "Brent Maranzano"
__license__ = "MIT"


logger = logging.getLogger("instrument.Bronkhorst")


class Ika(Instrument):
    """Ika overhead stirrer interface.
    """

    def __init__(self, port):
        """Sets an object attribute with defining the device port.

        Arguments
        port (str): Device port
        """
        super().__init__(port)

    def connect(self):
        """Connect to a serial port.

        Arguments
        port (str): Device port
        """
        self._ser = Serial(port=self._port, baudrate=9600, bytesize=7,
                           parity="E", stopbits=1, rtscts=0, timeout=0.5)

    def start(self, callback=None):
        """Start stirrer.
        """
        command = "START_4 \r \n"
        self._queue_request(command=command, callback=callback)

    def stop(self, callback=None):
        """Stop stirrer.
        """
        command = "STOP_4 \r \n"
        self._queue_request(command=command, callback=callback)

    def set_rate(self, rate, callback=None):
        """Set the stir rate (rev/min)
        """
        command = "OUT_SP_4 {:.2f} \r \n".format(rate)
        self._queue_request(command=command, callback=callback)

    def get_rate_SP(self, callback=None):
        """Get the stir rate set point (rev/min)
        """
        command = "IN_SP_4 \r \n"
        self._queue_request(command=command, callback=callback)

    def get_rate_PV(self, callback=None):
        """Get the stir rate present value (rev/min)
        """
        command = "IN_PV_4 \r \n"
        self._queue_request(command=command, callback=callback)

    def main(self):
        """Start the instrument communication.
        """
        super()._start_threads()
        self.connect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bronkhorst mass flow.")
    parser.add_argument(
        "--port",
        help="Device port instrument is connected",
        type=str,
        default="/dev/ttyUSB0"
    )
    parser.add_argument(
        "--debug_level",
        help="debugger level (e.g. INFO, WARN, DEBUG, ...)",
        type=str,
        default="INFO"
    )
    args = parser.parse_args()
    instrument = Ika(args.port)
    instrument.connect()
    instrument.run()
