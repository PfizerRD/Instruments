#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Class to monitor OPC UA server nodes.
"""
import argparse
import logging
from opcua import Client
from pdb import set_trace
from lib.helper_functions import yaml_to_dict

__author__ = "Brent Maranzano"
__license__ = "MIT"


logger = logging.getLogger("instrument.opc.client")


class Subscriber():
    """Create a subscription service to monitor node value changes. Upon change
    call a callback function to handle changes. The name representing the nodes
    must be unique.  That means monitoring identical node names in different
    parts of the OPC server tree is not permitted.
    """

    def __init__(self, endpoint):
        """Instantiate an the base class OPC client.

        Arguments
        endpoint (str): Server address
        """
        self._endpoint = endpoint
        self._monitor = []  # list of tuples that define the nodes (see _get_nodes)
        self._map = dict()  # map between name and Node object

    @classmethod
    def from_dictionary(cls, **params):
        """Instantiate an the subscriber from a ditionary

        Arguments
        params (dict): Configuration parameters to start subscription service.
            The dictionary should contain:
            endpoint (str): OPC server address
            uri (str): the namespace for the nodes
            obj (str): the parent object node of the nodes
            nodes (list): list of node names to subscribe
        """
        sub = cls(endpoint=params["endpoint"])
        sub._monitor = [(params["uri"], params["object"]["name"],
                         params["object"]["nodes"])]
        return sub

    @classmethod
    def from_file(cls, parameter_file):
        """Instantiate the subscriber from a parameter file.

        Arguments
        parameter_file (str): Name of YAML confiugration file.
        See from_dictionary for required items in YAML.
        """
        parameters = yaml_to_dict(parameter_file)
        sub = cls.from_dictionary(**parameters)
        return sub

    def _connect(self, endpoint):
        """Conncect to the OPC UA server.

        Arguments
        endpoint (str): OPC server address
        """
        self._client = Client(endpoint)
        self._client.connect()

    def set_callback(self, callback):
        """Set the callback to be called on changes
        in the monitored node values.

        Arguments
        callback (func): Function to be called on node changes.
        """
        self._callback = callback

    def add_nodes(self, uri, obj, nodes):
        """Add nodes to the subscription.

        Arguments
        uri (str): the namespace for the nodes
        obj (str): the parent object node of the nodes
        nodes (list): list of node names to subscribe
        """
        self._monitor.append((uri, obj, nodes))

    def _get_nodes(self, uri, obj, names):
        """Get links to the OPC nodes.

        Arguments
        uri (str): Namespace
        obj (str): Object name
        names (list): List of string of node names

        returns (list): List of Nodes
        """
        idx = self._client.get_namespace_index(uri)
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

    def respond(self, node, value):
        """Write a value to the node.

        Arguments
        node (str): String associated with node (see self._map)
        value (varries): value to write
        """
        self._map[node].set_value(value)

    def datachange_notification(self, node, val, data):
        """This method is called on subscribed node changes.
        see https://python-opcua.readthedocs.io/en/latest/subscription.html
        """
        name = self._get_name(node)
        self._callback(name=name, value=val)

    def run(self):
        """Connect to client, and subscribe to nodes.
        """
        self._connect(self._endpoint)
        for s in self._monitor:
            nodes = self._get_nodes(s[0], s[1], s[2])
            self._map.update({k: v for k, v in zip(s[2], nodes)})
        nodes = [v for k, v in self._map.items()]
        sub = self._client.create_subscription(1000, self)
        handle = sub.subscribe_data_change(nodes)
        logger.info("OPC subscription started")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OPC UA node subscriber")
    parser.add_argument(
        "--parameter_file",
        help="YAML file defining parameters for subscription",
        type=str,
        default="./parameter_file.yml"
    )
    parser.add_argument(
        "--debug_level",
        help="debugger level (e.g. INFO, WARN, DEBUG, ...)",
        type=str,
        default="INFO"
    )
    args = parser.parse_args()
    sub = Subscriber.from_file(args.parameter_file)

    def callback(*args, **kwargs):
        print(args, kwargs.items())
    sub.set_callback(callback)
    sub.run()
