#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tesing Ismatec OPC control from Delta V
"""
from pdb import set_trace
from time import sleep
from services.opc.subscriber import Subscriber
from instruments.ismatec.ismatec import Ismatec


__author__ = "Brent Maranzano"
__license__ = "MIT"


ismatec = Ismatec("/dev/ttyUSB0")
ismatec.main()


def run_command(name, value):
    if name == "START_CONTROLLER":
        if value:
            print("start")
            ismatec.start()
        else:
            print("stop")
            ismatec.stop()


def main():
    sub = Subscriber.from_file("./project/parameter_file.yml")
    sub.set_callback(run_command)
    sub.run()


if __name__ == "__main__":
    main()
