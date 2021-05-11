#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Miscelaneous helper functions.
"""

import logging
import logging.config
import yaml
import json
import coloredlogs
from types import SimpleNamespace

__author__ = "Brent Maranzano"
__license__ = "MIT"

"""
def setup_logger(config_file="./lib/logger_conf.yml", level=logging.INFO):
    config = yaml_to_dict(config_file)
    logging.config.dictConfig(config)
    coloredlogs.install(level=level)
    logger = logging.getLogger("instrument")
    return logger
"""


def yaml_to_dict(yaml_file):
    """Convert YAML file into a dictionary

    Arguments
    yaml_file (str) YAML file

    returns (dict)
    """
    with open(yaml_file, "rt") as file_obj:
        dict_obj = yaml.safe_load(file_obj.read())
    return dict_obj


def dict_to_namespace(dict_obj):
    """Convert dictionary into a SimpleNamespace

    Arguments
    dict_obj (dict)

    returns (SimpleNamespace)
    """
    name = json.loads(json.dumps(dict_obj),
                      object_hook=lambda item: SimpleNamespace(**item))
    return name


config = yaml_to_dict("lib/logger_conf.yml")
logging.config.dictConfig(config)
coloredlogs.install()
logger = logging.getLogger("instrument")
