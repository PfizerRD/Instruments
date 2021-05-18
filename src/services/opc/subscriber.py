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


class SubHandler(object):
    def __init__(self, params, node_map, callback):
        self._params = params
        self._map = node_map
        self._callback = callback

    def datachange_notification(self, node, val, data):
        """This method is called on subscribed node changes.
        see https://python-opcua.readthedocs.io/en/latest/subscription.html
        """
        # If the node is the watchdog node, then update without
        # calling instrument method to reduce CPU cycles.
        if node == self._map[self._params["watchdog"]["controller"]]:
            self._update_watchdog(val)


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

    def _connect(self, endpoint):
        """Conncect to the OPC UA server.

        Arguments
        endpoint (str): OPC server address
        """
        self._client = Client(endpoint)
        self._client.connect()

    def _get_nodes(self, idx, obj, names):
        """Get links to the OPC nodes.

        Arguments
        idx (int): Namespace index
        obj (str): Object name
        names (list): List of string of node names

        returns (list): List of Nodes
        """
        idx = self._client.get_namespace_index(idx)
        root = self._client.get_root_node()
        nodes = [root.get_child(self._get_path(idx, obj, n)) for n in names]
        return nodes

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

    def _get_name(self, node):
        """
        Get the name of the node from the mapping.

        Arguments
        node (node): Node object

        return (str) name associated with node
        """
        return [k for k, v in self._map.items() if v == node][0]

    def _create_node_map(self):
        """Create a map between node names and Node objects
        for fast lookup.
        """
        # Get all the nodes defined in the parameters dictionary.
        names = list(self._params["nodes"].keys())\
            + [v["respond"] for k, v in self._params["nodes"].items()]
        if "watchdog" in self._params:
            names += [self._params["watchdog"]["controller"],
                      self._params["watchdog"]["instrument"]]

        nodes = self._get_nodes(
                    self._params["uri"],
                    self._params["obj"],
                    names
        )

        return {k: v for k, v in zip(names, nodes)}

    def _get_monitor_nodes(self):
        """Get the nodes to be monitored.
        """
        names = list(self._params["nodes"].keys())
        if "watchdog" in self._params:
            names += [self._params["watchdog"]["controller"]]

        return self._get_nodes(self._params["uri"], self._params["obj"], names)

    def _update_watchdog(self, val):
        """Update the watchdog. This is handled at the subscription
        service level and not instrument to reduce CPU overhead.

        Arguments
        val (?): The value to return to the watchdog tag.
        """
        self.respond(self._params["watchdog"]["instrument"], val)

    def respond(self, node, value):
        """Write a value to the node.

        Arguments
        node (str): String associated with node (see self._map)
        value (varries): value to write
        """
        print(self._map[node], value)
        # self._map[node].set_value(value)

    def datachange_notification(self, node, val, data):
        """This method is called on subscribed node changes.
        see https://python-opcua.readthedocs.io/en/latest/subscription.html
        """
        # If the node is the watchdog node, then update without
        # calling instrument method to reduce CPU cycles.
        if node == self._map[self._params["watchdog"]["controller"]]:
            self._update_watchdog(val)
        else:
            return
            name = self._get_name(node)
            # Call the instrument callback with the node information:
            #     desired run command,
            #     callback to the respond method with the node as parameter
            if "parameters" in self._params["nodes"][name]["request"]:
                self._callback(
                    command=self._params["nodes"][name]["request"]["command"],
                    parameters=(val),
                    callback=lambda x: self._respond(
                        self._params["nodes"][name]["respond"], x),
                )
            if "parameters" in self._params["nodes"][name]["request"]:
                self._callback(
                    command=self._params["nodes"][name]["request"]["command"],
                    parameters=None,
                    callback=lambda x: self._respond(
                        self._params["nodes"][name]["respond"], x),
                )

    def run(self):
        """Connect to client, and subscribe to nodes.
        """
        self._connect(self._params["endpoint"])
        # handler = SubHandler(self.datachange_notification)
        sub = self._client.create_subscription(1000, self)
        self._map = self._create_node_map()
        nodes = self._get_monitor_nodes()
        handle = sub.subscribe_data_change(nodes)
        logger.info("OPC subscription started")
