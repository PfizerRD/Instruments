#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OPC subscriptin handler.
"""
import logging

__author__ = "Brent Maranzano"
__license__ = "MIT"


logger = logging.getLogger("instrument.opc.handler")


class Handler(object):
    """Class to handler OPC node changes.
    """

    def __init__(self, on_change, mapping):
        """Set the attributes change_callback and respond_callback.
        see: https://python-opcua.readthedocs.io/en/latest/subscription.html

        Arguments
        on_change (func): Function to call on node changes.
        mapping (dict): Object to define how to handle node value changes.
        """
        self._onchange = change_callback
        self._mapping = mapping

    def datachange_notification(self, node, val, data):
        """This method is called on subscribed node changes.
        When called it will queue a request object, which is:
            {
                "service": service,
                "payload": (node. val, data)
                "callback": func
            }
        """
        logger.debug("datachange_notification: {}\n".format(node))
        self._onchange(
                command="opc_client",
                payload={"args": (node, val, data), "kwargs": {}},
                callback=self._respond
        )
