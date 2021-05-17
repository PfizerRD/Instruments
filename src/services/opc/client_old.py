#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
General OPC UA client.
"""
import logging
import opcua
from services.opc.handler import Handler
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
    def run(cls, callback=None, **params):
        """Start the OPC client, and start a subscription for
        monitoring nodes. Provide a handler to handler node
        changes. Optonally provide the name of a watchdog node, for
        the client to monitor/respond.

        Arguments
        callback (func): Function to call on node value changes.
        params (dict): Configuration parameters to start service.
            The dictionary should contain:
            endpoint (str): OPC server address
            uri (str): the namespace for the nodes
            obj (str): the parent object node of the nodes
            nodes (dict): Keys are the name of the nodes to monitor. The
                values are dictionaries:
                    "respond": node to respond
            watchdog (optional) (str): the name of the node used for
                the watchdog
        """
        client = cls(params["endpoint"])
        client.connect()

        # Get the nodes from the parameter information
        idx = client.get_namespace_index(params["uri"])
        root = client.get_root_node()
        client._nodes = [
            root.get_child(list(client.get_browse_path(idx, params["obj"], n)))
            for n in list(params["nodes"].keys())
        ]

        client._map = {k: v for k, v in zip(params["nodes"], client._nodes)}
        sub_handler = Handler(params["callback"], client._respond)
        sub = client.create_subscription(1000, sub_handler)
        handle = sub.subscribe_data_change(client._nodes)
        logger.info("OPC subscription started")
        return client

    def get_browse_path(self, idx, obj, n):
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
        """Write a value to the node.

        Arguments
        node (str): String associated with node (see self._map)
        value (varries): value to write
        """
        getattr(self._map[node], "set_value")(value)
