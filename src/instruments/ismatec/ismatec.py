#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ismatec pump control
"""
import argparse
import logging
from serial import Serial
from instruments.instrument import Instrument
from pdb import set_trace
from time import sleep

__author__ = "Brent Maranzano"
__license__ = "MIT"


logger = logging.getLogger("instrument.ismatec")


class Ismatec(Instrument):
    """Ismatec pump controller.
    """

    def __init__(self, port):
        """Sets an object attribute with defining the device port.

        Arguments
        port (str): Device port
        """
        super().__init__(port)

    def connect(self):
        """Connect to the serial instrument

        Arguments
        params (dict): Parameters to start instrument
        """
        logger.info("connecting to serial")
        self._ser = Serial(port=self._port, baudrate=9600, bytesize=8,
                           parity="N", stopbits=1, timeout=0.5)
        self._ser.write(f"@1{chr(13)}".encode('ascii'))
        self._ser.write(f"1M{chr(13)}".encode('ascii'))

    def _process_request(self, command=None, callback=None, **kwargs):
        response = True
        if command == "start":
            self._ser.write(f"1H{chr(13)}".encode('ascii'))
        elif command == "stop":
            self._ser.write(f"1I{chr(13)}".encode('ascii'))
        elif command == "set_flowrate":
            flowrate = str(int(kwargs["flowrate"])).zfill(5)
            string = f"1S{flowrate}{chr(13)}"
            self._ser.write(string.encode('ascii'))
        elif command == "get_flowrate":
            self._ser.write(f"1S{chr(13)}".encode('ascii'))
            sleep(0.3)
            response = float(self._ser.readline().decode().split("\r")[0].strip("*"))
        if callback is not None:
            callback(response)
        sleep(0.3)

    def start(self, callback=None):
        """Start the pump.
        """
        self._queue_request(command="start", callback=callback)

    def stop(self, callback=None):
        """Stop the pump.
        """
        self._queue_request(command="stop", callback=callback)

    def set_flowrate(self, val, callback=None):
        """Set the pump rpm (1/min)

        Argument
        val (float): Pump RPMs (1/min)
        """
        self._queue_request(command="set_flowrate", flowrate=val,
                            callback=callback)

    def get_flowrate(self, callback=None):
        """Get the pump rpm (1/min)
        """
        self._queue_request(command="get_flowrate", callback=callback)

    def main(self):
        """Entry point
        """
        self.connect()
        self._start_threads()


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
    instrument.set_flowrate(555)
    instrument.start()
    instrument.get_flowrate(callback=print)
    sleep(2)
    instrument.stop()
    try:
        while instrument._queue.empty() is False:
            pass
    except KeyboardInterrupt:
        pass
