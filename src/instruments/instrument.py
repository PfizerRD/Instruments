#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generalized instrument that services commands generated by clients over
variuos protocols (MQTT, OPC UA).
"""
import queue
import threading
import logging
from lib import helper_functions
from services.opc import Opc
from time import sleep
from pdb import set_trace

__author__ = "Brent Maranzano"
__license__ = "MIT"


logger = logging.getLogger("instrument")


class Instrument(object):
    """Abastract instrument interface that services command requests generated
    by clients connected by various protocols (e.g. MQTT, HTTP, OPC UA).
    Service parameters and command mappings are defined in an auxillary YAML
    file.  Inhereting classes provide the instrument specific available
    commands.
    """

    def __init__(self, config_file):
        """Sets an object attribute with defining the service parameters

        Arguments
        config_file (str): Filename containing the configuration parameters for
                            the instrument and services.
        """
        self._params = self._get_parameters(config_file)
        self._queue = queue.Queue()
        self._user = None
        self._password = None

    def _get_parameters(self, config_file):
        """Read and parse the yaml file containing the
        configuration parameters to start the services.

        Arguments
        config_file (str): Filename containing parameters formatted
                            as yaml.

        returns (dict): Parameters.
        """
        params = helper_functions.yaml_to_dict(config_file)
        return params

    def _execute_queue(self):
        """Pop a request off of the queue and execute. After execution
        call self._respond.
        request has form {"service": service_name, "payload": service_data}
        """
        while True:
            logger.debug("execute queue")
            request = self._queue.get()
            self._process_request(**request)
            sleep(0.5)
        return

    def _process_request(self, service=None, payload=None):
        """Process the request. If the request is valid, send it
        to the appropriate subclass to handle the request.

        Arguments
        service (str): Name of service that produced request.
        payload (unknown): Request information provided by service.
        """
        logger.debug("process request")
        if not self._validate_request(payload):
            return
        elif service == "opc":
            self._process_opc(*payload)
        elif service == "mqtt":
            self._process_mqtt(*payload)

    def _validate_request(self, request):
        """Validate that the request has the correct user and password,
        if it is set.

        Arguments
        request (dict): Request object

        returns (bool): True if valid, False if invalid
        """
        if self._user is None and self._password is None:
            return True
        elif (request["user"] == self._user
              and request["password"] == self._password):
            return True
        else:
            logger.info("Received an invalid request.")
            return False

    def _process_opc(self, node, val, data):
        """Process an OPC request
        """
        logger.debug("process opc")
        if str(node) in self._map:
            try:
                response = getattr(self, self._map[str(node)])(val)
            except AttributeError:
                pass
            else:
                logger.debug("opc send: {}\n\n\n".format(response))
#                self._opc_client.send(response)

    def _process_mqtt(self, payload):
        """Process MQTT request.
        TODO
        """
        pass

    def _start_services(self):
        """Start the listening services if the service is defined
        in the configuration file.
        """
        logger.info("starting services")
        if "opc" in self._params:
            self._opc_client = Opc.run(**self._extract_opc_params())
            self._create_opc_mapping()

    def _extract_opc_params(self):
        """Extract the parameters to start the OPC service.
        """
        params = {
            "endpoint": self._params["opc"]["endpoint"],
            "nodes": [node["index"]
                      for node in self._params["opc"]["nodes"].values()],
            "queue": self._queue
        }
        return params

    def _create_opc_mapping(self):
        """Create the map between the node and the method called on node
        change. The map expedites the method resolution, but cannot be created
        until the OPC client connects.
        """
        self._map = dict()
        for node in self._opc_client._nodes:
            name = str(node.get_browse_name())
            for k, v in self._params["opc"]["nodes"].items():
                if k in name:
                    if "method" in v:
                        self._map[str(node)] = v["method"]

    def start(self):
        """Start the instrument.
        """
        threading.Thread(target=self._execute_queue, daemon=True).start()
        threading.Thread(target=self._update_data, daemon=True).start()
        self._start_services()