#!/usr/bin/env python

"""
ButtonDispatcher usage example 2
Here, ButtonDispatcher is initialized directly from python.
Button actions are defined as internal, and automatically hooked up to pre-defined functions.
"""

from button_dispatcher import *
import time

MyDispatcher = ButtonDispatcher()

GPIO.setmode(GPIO.BCM)

MyDispatcher.GPIOInited = True

GreenButton = GPIOButton(22,"Green",PULL_UP, TYPE_DUALMODE, ACTION_INTERNAL)
MyDispatcher.Buttons.append(GreenButton)

BlueButton = GPIOButton(23,"Blue",PULL_UP, TYPE_DUALMODE, ACTION_INTERNAL)
MyDispatcher.Buttons.append(BlueButton)

YellowButton = GPIOButton(24,"Yellow",PULL_UP, TYPE_ALT)
MyDispatcher.Buttons.append(YellowButton)

def GreenOnAction():
 print "Green on action!"

def GreenOffAction():
 print "Green off action!"

def GreenAltAction():
 print "Alt+Green action!"

def BlueOnAction():
 print "Blue on action!"

def BlueOffAction():
 print "Blue off action!"

def BlueAltAction():
 print "Alt+Blue action!"


while True:
 MyDispatcher.DispatchButtons()
 time.sleep(0.05)


