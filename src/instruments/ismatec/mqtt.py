#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bronkhorst mass flow meter MQTT commands
"""
import logging
from random import random

__author__ = "Brent Maranzano"
__license__ = "MIT"


logger = logging.getLogger(__name__)


class Opc(object):
    """Methods to service Bronkhorst commands from OPC client node changes.
    """

    def get_measurement(self):
        """Get the current measurement.
        """
