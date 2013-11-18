#
# Button class definition
#

import RPi.GPIO as GPIO
import Defs


class Button:

 HardwareType = None  # pull-up (pressed - False), pull-down (pressed - True)
 ButtonType = None    # single mode, dual mode(on|off), alt
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
     self.do_on_action()

    elif self.ButtonType == Defs.TYPE_DUALMODE:

     if self.Mode == Defs.MODE_OFF:
      self.do_on_action()
      self.Mode = Defs.MODE_ON
     elif self.Mode == Defs.MODE_ON:
      self.do_off_action()
      self.Mode = Defs.MODE_OFF

 def do_on_action(self):  # to be defined at runtime
  pass

 def do_off_action(self): # to be defined at runtime
  pass

 def do_alt_action(self): # to be defined at runtime
  pass

 def __init__(self, gpioid, name=str(GPIOid), hardware=Defs.PULL_DOWN, type=Defs.TYPE_SINGLEMODE):

  self.HardwareType = hardware
  self.GPIOid = gpioid
  self.ButtonType = type
  self.Name = name
  self.State = Defs.STATE_RELEASED
  self.Mode = Defs.MODE_OFF

  GPIO.setup(self.GPIOid, GPIO.IN)

#end of GPIOButton.Button class definition  

