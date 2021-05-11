#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OPC service to subscribe to node value changes on an OPC server. Upon
a node change the service executes a callback to handle the changes.
"""
import logging
import logging.config
import coloredlogs
from opcua import Client
import helper_functions

__author__ = "Giuseppe Cogoni"
__author__ = "Brent Maranzano"
__license__ = "MIT"


def setup_logger(config_file="./logger_conf.yml"):
    """Start the logger
    """
    config = helper_functions.yaml_to_dict(config_file)
    logging.config.dictConfig(config)
    coloredlogs.install(level="DEBUG")
    logger = logging.getLogger(__name__)
    return logger


try:
    logger = setup_logger()
except Exception:
    pass


class SubHandler(object):
    """Class to handle subscription to OPC node value changes.
    """

    def __init__(self, callback):
        self._callback = callback

    def datachange_notification(self, node, val, data):
        """Method required for handler passed to
        opc.Client.create_subscription.
        """
        logger.debug("""data change""")
        self._callback(node, val, data)


def start_service(params=None, callback=None):
    """Instantiate an OPC UA client, and subscribe to
    node changes. On node changes call the function
    "callback".

    Arguments
    params (dict): Parameters to define the OPC UA client connection.
    callback (func): Function to call upon OPC UA node changes.
    """
    client = Client(params["endpoint"])
    client.connect()
    sub_handler = SubHandler(callback)
    client.create_subscription(1000, sub_handler)
    nodes = [client.get_node(n) for n in params["nodes"].keys()]
    client.sub.subscribe_data_change(nodes)
    return client


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Service to subscribe to OPC UA node changes".
    )
    parser.add_argument(
        "--parameter_file",
        help="YAML file containing parameters that define the services."
             " See docstring for example.",
        type=str,
        default="parameter_file.yml"
    )
    args = parser.parse_args()
    instrument = Instrument(args.parameter_file)
    instrument.run()
