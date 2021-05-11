#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bronkhorst mass flow meter opc commands
"""
import logging
from lib import helper_functions
from random import random

__author__ = "Brent Maranzano"
__license__ = "MIT"

helper_functions.setup_logger()
logger = logging.getLogger(__name__)


class Opc(object):
    """Methods to service Bronkhorst commands from OPC client node changes.
    """

    def config_name(self, name):
        """Repeat back to the opc server the config name.
        """
        return {"node": "CONFIG_NAME_PAT", "value": name}

    def watchdog(self, val):
        """Repeat the number back to the server.
        """
        return {"node": "WATCHDOG_PAT", "value": val}

    def get_measurement(self):
        """Get the current measurement.
        """
