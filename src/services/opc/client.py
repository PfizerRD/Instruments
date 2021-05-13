#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
General OPC UA client.
"""
import logging
import opcua
from pdb import set_trace

__author__ = "Brent Maranzano"
__license__ = "MIT"


logger = logging.getLogger("instrument.opc.client")


class Client(opcua.Client):
    """Create a service to monitor OPC nodes.
    """

    def __init__(self, url):
        """Instantiate an the base class OPC client.

        Arguments
        url (str): Endpoint address for client connection
        """
        super(Client, self).__init__(url)

    @classmethod
    def run(cls, endpoint=None, uri=None, obj=None,
            nodes=None, sub_handler=None):
        """Start the OPC client, and start a subscription for
        monitoring nodes. Provide a handler to handler node
        changes.

        Arguments
        endpoint (str): Endpoint for client to connect.
        uri (str): Namespace.
        obj (str): Object name nodes are grouped under.
        nodes (dict): Nodes to subscripbe
            {"name": {"namespace": str "index": int}}
        sub_handler (obj): Object to handler node changes.
        """
        client = cls(endpoint)
        client.connect()
        idx = client.get_namespace_index(uri)
        root = client.get_root_node()
        node_bps = [list(client._bp(idx, obj, n)) for n in nodes]
        client._nodes = [root.get_child(n) for n in node_bps]
        client._map = zip(str([n.get_browse_name() for n in client._nodes]), client._nodes)
        sub = client.create_subscription(1000, sub_handler)
        handle = sub.subscribe_data_change(client._nodes)
        logger.info("OPC subscription started")
        return client

    def _bp(self, idx, obj, n):
        """Make a browse path string from the namespace index and object and
        node name

        Arguments
        idx (int): Namespace index
        obj (str): Object name

        Return (str) browse path
        """
        bp = "0:Objects", f"{idx}:{obj}", f"{idx}:{n}"
        return bp

    def respond(self, node, value):
        """Write back to the OPC server
        """
        node = self.client.get_node
        logger.info("opc respond {}".format(node))
