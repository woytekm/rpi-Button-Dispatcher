#!/usr/bin/python
#
# Button class definition
#

import RPi.GPIO as GPIO
import Defs


class Button:

 HardwareType = None  # pull-up (pressed - False), pull-down (pressed - True)
 ButtonType = None    # single mode, double mode (on|off), alt
 GPIOid = None        # integer - GPIO number
 State = None         # pressed, released
 Mode = None          # on, off
 Name = None          # button nickname - used in script calls
 
 def pressed(self):

  if GPIO.input(self.GPIOid) == True:

   if self.HardwareType == Defs.PULL_UP:
    return False
   elif self.HardwareType == Defs.PULL_DOWN:
    return True

  else:   # GPIO = 0

   if self.HardwareType == Defs.PULL_UP:
    return True
   elif self.HardwareType == Defs.PULL_DOWN:
    return False

 def do_action(self):

  if not (self.ButtonType == Defs.TYPE_ALT):  # alt button alone has no action

    if self.ButtonType == Defs.TYPE_SINGLEMODE:
     print self.Name, " action on"

    elif self.ButtonType == Defs.TYPE_DOUBLEMODE:

     if self.Mode == Defs.MODE_OFF:
      print self.Name, "action on"
      self.Mode = Defs.MODE_ON
     elif self.Mode == Defs.MODE_ON:
      print self.Name, "action off" 
      self.Mode = Defs.MODE_OFF

 def do_alt_action(self):
  print self.Name, "alt action"

 def __init__(self, gpioid, name=str(GPIOid), hardware=Defs.PULL_DOWN, type=Defs.TYPE_SINGLEMODE):

  self.HardwareType = hardware
  self.GPIOid = gpioid
  self.ButtonType = type
  self.Name = name
  self.State = Defs.STATE_RELEASED
  self.Mode = Defs.MODE_OFF

  GPIO.setup(self.GPIOid, GPIO.IN)

#end of GPIOButton.Button class definition  

