#!/usr/bin/env python
"""
 ButtonDispatcher usage example 1
 Button configuration is loaded from config file dispatcher-example1.cfg
"""

from button_dispatcher import *
import time
import sys

ConfigPath = "dispatcher-example1.cfg"

MyDispatcher = ButtonDispatcher()
MyDispatcher.InitFromFile(ConfigPath)

if not MyDispatcher.Buttons:
 sys.exit("No button definititions loaded! Nothing to do - exit.")

while True:
 MyDispatcher.DispatchButtons()
 time.sleep(0.05)

