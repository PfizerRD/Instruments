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
            root.get_child(self._get_path(idx, self._params["obj"], n))
            for n in list(self._params["nodes"].keys())
        ]
        self._map = {
            k: v for k, v in zip(self._params["nodes"].keys(), self._nodes)
        }

    def _get_path(self, idx, obj, name):
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
        self._map = {k: v for k, v in zip(self._params["nodes"],
                     self._nodes)}

    def _get_name(self, node):
        """
        Get the name of the node from the mapping.

        Arguments
        node (node): Node object

        return (str) name associated with node
        """
        return [k for k, v in self._map.items() if v == node][0]

    def datachange_notification(self, node, val, data):
        """This method is called on subscribed node changes.
        """
        name = self._get_name(node)
#        if name ==
        # Call the instrument callback with the node information:
        #     desired run command,
        #     callback to the respond method with the node as parameter
        self._callback(
            command=self._params["nodes"][name]["command"],
            parameters=val,
            callback=lambda x: self._respond(
                self._params["nodes"][name]["respond"], x),
        )

    def respond(self, node, value):
        """Write a value to the node.

        Arguments
        node (str): String associated with node (see self._map)
        value (varries): value to write
        """
        self._client.set_values(self._map[node], value)

    def run(self):
        """Run the serivce.
        """
        self._connect()
        self._get_nodes()
        sub = self._client.create_subscription(1000, self)
        handle = sub.subscribe_data_change(self._nodes)
        logger.info("OPC subscription started")
