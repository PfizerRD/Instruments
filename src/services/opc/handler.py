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

    def __init__(self, callback):
        """Set the class attribute callback. Upon subscribed node
        changes, the datachange_notification will be called.
        see: https://python-opcua.readthedocs.io/en/latest/subscription.html
        """
        self._callback = callback

    def datachange_notification(self, node, val, data):
        """This method is called on subscribed node changes.
        When called it will queue a request object.
        """
        logger.debug("datachange_notification: {}\n".format(node))
        self._callback({"service": "opc", "payload": (node, val, data)})
