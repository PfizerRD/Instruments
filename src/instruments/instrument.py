#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Abstract serial instrument
"""
import queue
import threading
import logging
from time import sleep


__author__ = "Brent Maranzano"
__license__ = "MIT"


logger = logging.getLogger("instrument")


class Instrument(object):
    """Abstract serial instrument that provides state retention, user
    authentification and asynchronous communication.
    """

    def __init__(self, port):
        """Sets an object attribute with defining the service parameters

        Arguments
        port (str): The device port
        callback (func): The function to call after command execution.
        """
        self._port = port
        self._queue = queue.Queue()

    def connect(self, port):
        """Connect to a serial port. Method to be overridden

        Arguments
        port (str): The device port
        """
        pass

    def _process_queue(self):
        """Pop a request off of the queue and process the request.
        """
        logger.info("process queue thread starting")
        while True:
            request = self._queue.get()
            self._process_request(**request)

    def _queue_request(self, **request):
        """Queue requests.

        Arguments
        request (dict): Details of service request
           command (str): Name of command to execute
           callback (fun): function to call back with command results.
        """
        self._queue.put(request)

    def _start_threads(self):
        """Setup the instrument communication.
        """
        threading.Thread(target=self._process_queue, daemon=True).start()
