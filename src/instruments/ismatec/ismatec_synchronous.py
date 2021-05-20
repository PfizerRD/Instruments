#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ismatec pump control
"""
import argparse
import logging
from serial import Serial
from pdb import set_trace
from time import sleep

__author__ = "Brent Maranzano"
__license__ = "MIT"


logger = logging.getLogger("instrument.ismatec")


class Ismatec():
    """Ismatec pump controller.
    """

    def __init__(self, port):
        """Sets an object attribute with defining the device port.

        Arguments
        port (str): Device port
        """
        self._connect(port)

    def _connect(self, port):
        """Connect to the serial instrument

        Arguments
        params (dict): Parameters to start instrument
        """
        logger.info("connecting to serial")
        self._ser = Serial(port=port, baudrate=9600, bytesize=8,
                           parity="N", stopbits=1, timeout=0.5)
        self._ser.write(f"@1{chr(13)}".encode('ascii'))
        self._ser.write(f"1M{chr(13)}".encode('ascii'))

    def start(self):
        """Start the pump.
        """
        self._ser.write(f"1H{chr(13)}".encode('ascii'))

    def stop(self):
        """Stop the pump.
        """
        self._ser.write(f"1I{chr(13)}".encode('ascii'))

    def set_flowrate(self, val):
        """Set the pump rpm (1/min)

        Argument
        val (float): Pump RPMs (1/min)
        """
        val = str(int(val)).zfill(5)
        string = f"1S{val}{chr(13)}"
        self._ser.write(string.encode('ascii'))

    def get_flowrate(self):
        """Get the pump rpm (1/min)
        """
        self._ser.write(f"1S{chr(13)}".encode('ascii'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Service to call queued Bronkhorst serial methods."
    )
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
    instrument = Ismatec(args.port)
    instrument.set_flowrate(999)
    sleep(0.3)
    instrument.start()
    sleep(0.3)
    instrument.get_flowrate()
    sleep(2)
    instrument.stop()
