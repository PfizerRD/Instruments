#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run an OPC UA server.
"""
import argparse
import logging
from opcua import Server, ua
from lib import helper_functions
from pdb import set_trace
__author__ = 'Brent Maranzano'
__license__ = 'MIT'


logger = logging.getLogger("services.opc.server")


class OpcServer(Server):
    """OPC server
    class attributes added to opcua.Server:
        _server
        _nodes
    """

    def __init__(self, parameters):
        """Create an OPC UA server

        Arguments
        parameters (dict): Dictionary of server configuration parameters.
        """
        self._params = parameters
        self._nodes = {}  # Define a map between the node name and Node.

    @classmethod
    def from_parameter_file(cls, parameter_file):
        """Create an OPC UA server

        Arguments
        parameter_file (str): Filename for the service parameters.
        """
        params = helper_functions.yaml_to_dict(parameter_file)
        return cls(params)

    def _create_nodes(self, idx, obj, nodes):
        """Create nodes in the namespace and object.

        Arguments
        idx (int): Namesapce index
        obj (str): Name of object
        nodes (dict): Information on node creation
        """
        for name, attr in nodes.items():
            node = obj.add_variable(idx, name, attr["value"],
                                    getattr(ua.VariantType, attr["type"]))
            node.set_writable() if attr["writable"] else node.set_read_only()
            self._nodes[name] = node

    def get_nodes(self):
        """Return the nodes.

        return (list): list of dictionary of nodes.
        """
        return self._nodes

    def run(self):
        """Instantiate and run server
        """
        logger.info("starting OPC service")
        params = self._params
        self._server = Server()
        self._server.set_endpoint(params["endpoint"])
        self._server.set_server_name(params["name"])
        idx = self._server.register_namespace(params["uri"])
        obj = self._server.nodes.objects.add_object(idx, params["object"]["name"])
        self._create_nodes(idx, obj, params["object"]["nodes"])
        self._server.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="simulated OPC UA server")
    parser.add_argument(
        "--parameter_file",
        help="YAML file defining parameters for server",
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
    server = OpcServer.from_parameter_file(args.parameter_file)
    server.run()
