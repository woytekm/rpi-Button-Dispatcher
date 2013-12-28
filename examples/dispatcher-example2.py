#!/usr/bin/env python

"""
ButtonDispatcher usage example 2
Here, ButtonDispatcher is initialized directly from python.
Button actions are defined as internal, and automatically hooked up to pre-defined functions.
We have three buttons here: 
 one single mode with short and long actions,
 one dual mode
 one alt
"""

from button_dispatcher import *
import time

MyDispatcher = ButtonDispatcher()

GPIO.setmode(GPIO.BCM)

MyDispatcher.GPIOInited = True

GPIO22 = 22
GPIO23 = 23
GPIO24 = 24

GreenButton = GPIOButton(GPIO22,"Green",PULL_UP, TYPE_SINGLEMODE, ACTION_INTERNAL, LONG_ACTION) 
MyDispatcher.Buttons.append(GreenButton)

BlueButton = GPIOButton(GPIO23,"Blue",PULL_UP, TYPE_DUALMODE, ACTION_INTERNAL)
MyDispatcher.Buttons.append(BlueButton)

YellowButton = GPIOButton(GPIO24,"Yellow",PULL_UP, TYPE_ALT)
MyDispatcher.Buttons.append(YellowButton)

def GreenOnAction():
 print "Green on action!"

def GreenOnLongAction():
 print "Green on long action!"

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


