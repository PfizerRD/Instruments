#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bronkhorst flow meter.
"""
import argparse
import logging
from serial import Serial
from lib import helper_functions


__author__ = "Brent Maranzano"
__license__ = "MIT"


logger = logging.getLogger("instrument.Bronkhorst")


class Bronkhorst(object):
    """Bronkhorst flow meter
    """

    def __init__(self, port):
        """Sets an object attribute with defining the service parameters
        """
        super().__init__(port)
        self._commands = ["set_rate"]

    def connect(self, port="/dev/ttyUSB0", baudrate=9600, parity="N",
                bytesize=8, stopbits=1):
        """Connect to a serial port.

        Arguments
        port (str): Device port
        baudrate (int): Baudrate
        bytesize (int): number of bytes in packet
        parity (str): Single character representing parity
        stopbits (int): Stopbits
        see https://pythonhosted.org/pyserial/pyserial_api.html#module-serial.threaded
        """
        self._ser = Serial(port=port, baudrate=baudrate, bytesize=bytesize,
                           parity=parity, stopbits=stopbits)

    def set_serial_parameters(self, port="/dev/ttyUSB0", baudrate=9600,
                              parity="N", bytesize=8, stopbits=1):
        """Connect to a serial port.

        Arguments
        port (str): Device port
        baudrate (int): Baudrate
        bytesize (int): number of bytes in packet
        parity (str): Single character representing parity
        stopbits (int): Stopbits
        see https://pythonhosted.org/pyserial/pyserial_api.html#module-serial.threaded
        """
        self._ser_params = dict(port=port, baudrate=baudrate, parity=parity,
                                bytesize=bytesize, stopbits=stopbits)

    def set_commands(self, commands):
        """Set the instrument commands.

        commands (dict): Keys are command names, values are formatted strings.
        """
        self._commands = commands

    @classmethod
    def from_file(cls, config_file):
        """Create the instrument object from a configuration file.

        Arguments
        config_file (str): Filename containing parameters formatted
                            as yaml.
        """
        params = helper_functions.yaml_to_dict(config_file)
        instrument = cls()
        instrument.connect(**params["serial"])

    def _update_data(self):
        """Periodically get the current instrument data and store
        in class attribute to expedite responses to service requests.
        Method is to be over-ridden.
        """
        pass

    def _process_queue(self):
        """Pop a request off of the queue and process the request.
        """
        logger.info("process queue thread starting")
        while True:
            request = self._queue.get()
            self._process_request(request)
            sleep(0.3)

    def _process_request(self, request):
        """Proces the reqest. Note that the command may be blocking.

        Arguments
        request (dict): Details of service request
           command (str): Name of command to execute
           parameters (command dependent): Parameters for command.
           callback (fun): function to call back with command results.
        """
        response = False
        command = getattr(self, request["command"], False)
        if command:
            # Some services (e.g. OPC) always pass arguments,
            # so check if the method requires one.
            if len(inspect.getfullargspec(command).args) == 1:
                response = command()
            else:
                response = command(request["parameters"])
        else:
            try:
                command = eval(request["command"]).encode('ascii')
                self._serial.write(command)
                sleep(0.3)
                response = self._serial.readline()
            except Exception:
                logger.error("Error writing serial command {}".format(command))

        if response:
            request["callback"](response)

    def _queue_request(self, **request):
        """Queue requests.

        Arguments
        request (dict): Details of service request
           command (str): Name of command to execute
           parameters (command dependent): Parameters for command.
           callback (fun): function to call back with command results.
        """
        self._queue.put(request)

    def main(self):
        """Start the instrument communication.
        """
        self.connect(**self._ser_params)


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
    instrument = Bronkhorst()
    instrument.run(args.port)
