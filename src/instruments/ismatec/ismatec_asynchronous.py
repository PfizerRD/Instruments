#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ismatec pump control
"""
import argparse
import logging
import asyncio
import serial_asyncio
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
        self._ser.write(f"1S{val}{chr(13)}".encode('ascii'))

    def get_flowrate(self):
        """Get the pump rpm (1/min)
        """
        self._ser.write(f"1S{chr(13)}".encode('ascii'))

    async def send(w, command):
        w.write(command)
        await asyncio.sleep(0.3)


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
    instrument.main()
    instrument.set_flowrate(944)
    instrument.start()
    instrument.get_flowrate(callback=print)
    sleep(5)
    instrument.stop()
    try:
        while instrument._queue.empty() is False:
            pass
    except KeyboardInterrupt:
        pass
