#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
General OPC UA client.
"""
import logging
from opcua import Client
from pdb import set_trace

__author__ = "Brent Maranzano"
__license__ = "MIT"


logger = logging.getLogger("instrument.opc.client")


class Subscriber(Client):
    """Create a service to monitor OPC nodes.
    """

    def __init__(self, url):
        """Instantiate an the base class OPC client.

        Arguments
        url (str): Endpoint address for client connection
        """
        super(Opc, self).__init__(url)

    @classmethod
    def run(cls, endpoint=None, nodes=None, sub_handler=None):
        """Start the OPC client, and start a subscription for
        monitoring nodes. Provide a handler to handler node
        changes.

        Arguments
        endpoing (str): Endpoint for client to connect.
        nodes (str): Address values of nodes to subscribe.
        sub_handler (obj): Object to handler node changes.
        """
        client = cls(endpoint)
        client.connect()
        set_trace()
        client._nodes = [client.get_node(n) for n in nodes]
        sub = client.create_subscription(1000, sub_handler)
        handle = sub.subscribe_data_change(client._nodes)
        logger.info("OPC subscription started")
        return client

    def handle_response(self, node, data):
        """Write back to the OPC server
        """
        pass
