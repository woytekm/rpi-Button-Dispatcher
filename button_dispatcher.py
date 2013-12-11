#!/usr/bin/env python

"""
ButtonDispatcher - implement GPIOButton and ButtonDispatcher classes
Button Dispatcher provides simple interface to Rasbperry Pi GPIO buttons  
"""

__author__ = "Wojtek Mitus"
__copyright__ = "Copyright 2013, Wojtek Mitus"
__license__ = "GPL"
__version__ = "0.3"


import RPi.GPIO as GPIO
import subprocess
import sys

# global "constant" definitions:

PULL_UP = 1
PULL_DOWN = 2

MODE_ON = 1
MODE_OFF = 2

STATE_RELEASED = 0
STATE_PRESSED = 1

TYPE_SINGLEMODE = 1
TYPE_DUALMODE = 2
TYPE_ALT = 3

ACTION_EXTERNAL = 1
ACTION_INTERNAL = 2
ACTION_NOACTION = 3


class ButtonDispatcher:

 AltState = STATE_RELEASED   
 GPIOInited = False
 GPIONumbering = None
 ExtScriptPath = None

 Buttons = []


 def InitFromParams(): #TODO
  
  pass


 def InitFromFile(self,ConfigPath):
  
  try: 
   CfgFile = open(ConfigPath)

  except:
   print "Cannot open config file "+ConfigPath
   return

  ConfLine = 0
 
  for CfgLine in CfgFile:
      ConfLine += 1
      BadConf = 0

      Fields = CfgLine.split()
     
      if(len(Fields) < 2):
       continue

      if(Fields[0].lower() == "scriptpath") and (len(Fields[1]) > 0):
        self.ExtScriptPath = Fields[1]
        continue

      if(Fields[0].lower() == "gpionumbering"):
        if((Fields[1].lower() == "board") or (Fields[1].lower() == "bcm")):
         self.GPIONumbering = Fields[1]
         continue
        else:
         BadConf = 1
 
      if BadConf:
       print "Error in line ",ConfLine," of ",ConfigPath

      if(Fields[0].lower() == "button"):
       if(Fields[3].lower() == "pullup"): 
        BtnHardware = PULL_UP
       elif (Fields[3].lower() == "pulldown"):
        BtnHardware = PULL_DOWN
       else:
        BadConf = 1

       if(Fields[4].lower() == "singlemode"):
        BtnType = TYPE_SINGLEMODE
       elif (Fields[4].lower() == "dualmode"):
        BtnType = TYPE_DUALMODE
       elif (Fields[4].lower() == "alt"):
        BtnType = TYPE_ALT
       else:
        BadConf = 1 

       if len(Fields) == 6:
         if(Fields[5].lower() == "external"):
          ActionType = ACTION_EXTERNAL
         elif (Fields[5].lower() == "internal"):
          ActionType = ACTION_INTERNAL
         else:
          BadConf = 1
       else:
        ActionType = ACTION_NOACTION

        
       GPIOID = int(Fields[1])

       if(GPIOID < 27) and (GPIOID > 0):
        pass
       else:
        BadConf = 1

       BtnName = Fields[2]
      
       if(len(BtnName) < 255):
        pass
       else:
        BadConf = 1
 
       if BadConf:
        print "Bad button definition in ",ConfigPath," line ", ConfLine
        continue 
     
       if not self.GPIOInited:             # we have to init GPIO before initializing buttons
        if self.GPIONumbering == "BOARD":
          GPIO.setmode(GPIO.BOARD)
        elif self.GPIONumbering == "BCM":
          GPIO.setmode(GPIO.BCM)
        else:
          print "GPIO numbering convention is not set in config file - exit."
        
        self.GPIOInited = True
         
       NewButton = GPIOButton(GPIOID, BtnName, BtnHardware, BtnType, ActionType)

       self.Buttons.append(NewButton) 


 def DispatchButtons(self):

   for Button in self.Buttons:
    if Button.Pressed():
     if Button.State == STATE_RELEASED:
      Button.State = STATE_PRESSED
      Button.DoAction(self)
     if Button.ButtonType == TYPE_ALT:
      if self.AltState == STATE_RELEASED:
       self.AltState = STATE_PRESSED
    else:
     if Button.State == STATE_PRESSED:
      Button.State = STATE_RELEASED
      if Button.ButtonType == TYPE_ALT:
       if self.AltState == STATE_PRESSED:
        self.AltState = STATE_RELEASED


class GPIOButton:

 HardwareType = None  # pull-up (pressed - logic 0), pull-down (pressed - logic 1)
 ButtonType = None    # single mode, dual mode(on|off), alt
 GPIOid = None        # integer - GPIO ID
 State = None         # pressed, released
 Mode = None          # on, off
 Name = None          # button nickname - used in script/routine calls
 ActionType = None    # RunScript|RunPython

 
 def Pressed(self):

  if GPIO.input(self.GPIOid) == True:
   if self.HardwareType == PULL_UP:
    return False
   elif self.HardwareType == PULL_DOWN:
    return True

  else:   # GPIO = 0
   if self.HardwareType == PULL_UP:
    return True
   elif self.HardwareType == PULL_DOWN:
    return False


 def DoAction(self,ButtonDispatcher):

  if not (self.ButtonType == TYPE_ALT):  # alt button alone has no action

    if ButtonDispatcher.AltState == STATE_PRESSED:
     self.DoAltAction(ButtonDispatcher)

    elif self.ButtonType == TYPE_SINGLEMODE:
     self.DoOnAction(ButtonDispatcher)

    elif self.ButtonType == TYPE_DUALMODE:
     if self.Mode == MODE_OFF:
      self.DoOnAction(ButtonDispatcher)
      self.Mode = MODE_ON
     elif self.Mode == MODE_ON:
      self.DoOffAction(ButtonDispatcher)
      self.Mode = MODE_OFF


 def DoOnAction(self,ButtonDispatcher):  
  if self.ActionType == ACTION_EXTERNAL:
   RunScript = ButtonDispatcher.ExtScriptPath+"/"+self.Name+"_on_action"
   subprocess.call(RunScript)
  elif self.ActionType == ACTION_INTERNAL:
   RunRoutine = getattr(sys.modules['__main__'],self.Name+"OnAction")
   RunRoutine()
  
 def DoOffAction(self,ButtonDispatcher): 
  if self.ActionType == ACTION_EXTERNAL:
   RunScript = ButtonDispatcher.ExtScriptPath+"/"+self.Name+"_off_action"
   subprocess.call(RunScript)
  elif self.ActionType == ACTION_INTERNAL:
   RunRoutine = getattr(sys.modules['__main__'],self.Name+"OffAction")
   RunRoutine()

 def DoAltAction(self,ButtonDispatcher):
  if self.ActionType == ACTION_EXTERNAL:
   RunScript = ButtonDispatcher.ExtScriptPath+"/"+self.Name+"_alt_action"
   subprocess.call(RunScript)
  elif self.ActionType == ACTION_INTERNAL:
   RunRoutine = getattr(sys.modules['__main__'],self.Name+"AltAction")
   RunRoutine()

 def __init__(self, gpioid, name=str(GPIOid), hardware=PULL_DOWN, type=TYPE_SINGLEMODE, action=ACTION_NOACTION):

  self.HardwareType = hardware
  self.GPIOid = gpioid
  self.ButtonType = type
  self.Name = name
  self.State = STATE_RELEASED
  self.Mode = MODE_OFF
  self.ActionType = action

  GPIO.setup(self.GPIOid, GPIO.IN)


# end of ButtonDispatcher module

