#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
General OPC UA client.
"""
import logging
from opcua import Client
from lib import helper_functions
from pdb import set_trace

__author__ = "Giuseppe Cogoni"
__author__ = "Brent Maranzano"
__license__ = "MIT"


logger = logging.getLogger(__name__)


class OpcSubHandler(object):
    """Class to queue OPC node changes.
    """

    def __init__(self, queue):
        """Set the class attribute queue. Upon subscribed node
        changes, the datachange_notification will be called.
        see: https://python-opcua.readthedocs.io/en/latest/subscription.html
        """
        self._queue = queue

    def datachange_notification(self, node, val, data):
        """This method is called on subscribed node changes.
        When called it will queue a request object.
        """
        request = {"service": "opc", "payload": (node, val, data)}
        logger.debug("datachange_notification: {}\n".format(request))
        self._queue.put(request)


class Opc(Client):
    """Create a service to monitor OPC nodes.
    """

    def __init__(self, url):
        """Instantiate an the base class OPC client.

        Arguments
        url (str): Endpoint address for client connection
        """
        super(Opc, self).__init__(url)

    @classmethod
    def run(cls, endpoint=None, nodes=None, queue=None):
        """Start the OPC client, and start a subscription for
        monitoring nodes. Provide the subscription handler with
        a queue to queue node changes.

        Arguments
        endpoing (str): Endpoint for client to connect.
        nodes (str): Address values of nodes to subscribe.
        queue (Queue): Queue for adding request object with node changes.
        """
        client = cls(endpoint)
        client.connect()
        client._nodes = [client.get_node(n) for n in nodes]
        handler = OpcSubHandler(queue)
        sub = client.create_subscription(1000, handler)
        handle = sub.subscribe_data_change(client._nodes)
        return client

    def handle_response(self, node, data):
        """Write back to the OPC server
        """
        pass
