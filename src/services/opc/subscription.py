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


class Subscriber():
    """Create a service to monitor OPC nodes.
    """

    def __init__(self, callback, **params):
        """Instantiate an the base class OPC client.

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
        self._callback = callback
        self._params = params

    def _connect(self):
        """Conncect to the OPC UA server.
        """
        self._client = Client(self._params["endpoint"])
        self._client.connect()

    def _get_nodes(self):
        """Get links to the OPC nodes.
        """
        idx = self._client.get_namespace_index(self._params["uri"])
        root = self._client.get_root_node()
        self._nodes = [
            root.get_child(self.gbp(idx, self._params["obj"], n))
            for n in list(self._params["nodes"].keys())
        ]

    def datachange_notification(self, node, val, data):
        """This method is called on subscribed node changes.
        When called it will queue a request object, which is:
            {
                "service": service,
                "payload": (node. val, data)
                "callback": func
            }
        """
        node.get_browse_name()
        self._callback(command=None, payload=None, callback=None)
        logger.debug("datachange_notification: {}\n".format(node))

    def run(self):
        """Run the serivce.
        """
        self._connect()
        self._get_nodes()
        set_trace()
        self._sub = self._client.create_subscription(1000, self)
        self._handle = self._sub.subscribe_data_change(self._nodes)
        logger.info("OPC subscription started")

    def _gbp(self, idx, obj, name):
        """Make a browse path list from the namespace index and object and
        node name.

        Arguments
        idx (int): Namespace index
        obj (str): Object name
        name (str): Name of node

        Return (list) browse path
        """
        bp = ["0:Objects", f"{idx}:{obj}", f"{idx}:{name}"]
        return bp

    def _make_mapping(self):
        """Make mapping between the node object and the node name.
        """
        self._client._map = {k: v for k, v in zip(self._params["nodes"],
                             self._nodes)}

    def respond(self, node, value):
        """Write a value to the node.

        Arguments
        node (str): String associated with node (see self._map)
        value (varries): value to write
        """
        getattr(self._map[node], "set_value")(value)
