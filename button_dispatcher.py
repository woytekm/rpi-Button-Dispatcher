#!/usr/bin/env python

"""
ButtonDispatcher - implement GPIOButton and ButtonDispatcher classes
Button Dispatcher provides simple interface to Rasbperry Pi GPIO buttons  
"""

__author__ = "Wojtek Mitus"
__copyright__ = "Copyright 2013, Wojtek Mitus"
__license__ = "GPL"
__version__ = "0.31"


import RPi.GPIO as GPIO
import subprocess
import sys
import time

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

LONG_ACTION = True

# timing:
DISPATCH_LOOP_DLY = 0.02
LONG_PRESS_TRIGGER = 1
DEFAULT_BOUNCE_WINDOW = 0.02


# class definitions:
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

  CfgLineNumber = 0
 
  for CfgLine in CfgFile:

      CfgLineNumber += 1
      BadConf = 0
      ActionType = ACTION_NOACTION
      SensePressLen = False

      CfgLineFields = CfgLine.split()
     
      if(len(CfgLineFields) < 2):
       continue

      if(CfgLineFields[0].lower() == "scriptpath") and (len(CfgLineFields[1]) > 0):
        self.ExtScriptPath = CfgLineFields[1]
        continue

      if(CfgLineFields[0].lower() == "gpionumbering"):
        if((CfgLineFields[1].lower() == "board") or (CfgLineFields[1].lower() == "bcm")):
         self.GPIONumbering = CfgLineFields[1]
         continue
        else:
         BadConf = 1
 
      if BadConf:
       print "Error in line ",CfgLineNumber," of ",ConfigPath
       return

      if(CfgLineFields[0].lower() == "button"):
       if(CfgLineFields[3].lower() == "pullup"): 
        BtnHardware = PULL_UP
       elif (CfgLineFields[3].lower() == "pulldown"):
        BtnHardware = PULL_DOWN
       else:
        BadConf = 1

       if(CfgLineFields[4].lower() == "singlemode"):
        BtnType = TYPE_SINGLEMODE
       elif (CfgLineFields[4].lower() == "dualmode"):
        BtnType = TYPE_DUALMODE
       elif (CfgLineFields[4].lower() == "alt"):
        BtnType = TYPE_ALT
       else:
        BadConf = 1 

       if len(CfgLineFields) > 5:
         if(CfgLineFields[5].lower() == "external"):
          ActionType = ACTION_EXTERNAL
         elif (CfgLineFields[5].lower() == "internal"):
          ActionType = ACTION_INTERNAL
         else:
          BadConf = 1

       if len(CfgLineFields) == 7:
        if(CfgLineFields[6].lower() == "longpress"):
          SensePressLen = True
        else:
          BadConf = 1
 
       GPIOID = int(CfgLineFields[1])

       if self.GPIONumbering == "BOARD":
         if(GPIOID < 27) and (GPIOID > 0):
          pass
         else:
          BadConf = 1
       elif self.GPIONumbering == "BCM":
         if(GPIOID < 26) and (GPIOID > 0):
          pass
         else:
          BadConf = 1

       BtnName = CfgLineFields[2]
      
       if(len(BtnName) < 255):
        pass
       else:
        BadConf = 1
 
       if BadConf:
        print "Bad button definition in ",ConfigPath," line ", CfgLineNumber
        continue 
     
       if not self.GPIOInited:             # we have to init GPIO before initializing buttons
        if self.GPIONumbering == "BOARD":
          GPIO.setmode(GPIO.BOARD)
        elif self.GPIONumbering == "BCM":
          GPIO.setmode(GPIO.BCM)
        else:
          print "GPIO numbering convention is not set in config file - exit."
          return
        
        self.GPIOInited = True
         
       NewButton = GPIOButton(GPIOID, BtnName, BtnHardware, BtnType, ActionType, SensePressLen)

       self.Buttons.append(NewButton) 


 def DispatchButtons(self):

  for Button in self.Buttons:

   if Button.Pressed():

     Button.PressTimer += DISPATCH_LOOP_DLY

     if Button.ButtonType == TYPE_ALT:
       if self.AltState == STATE_RELEASED:
        self.AltState = STATE_PRESSED
        Button.State = STATE_PRESSED
       continue
     
     if((Button.State == STATE_RELEASED) and (Button.BounceTimer > Button.BounceWindow)):
      Button.BounceTimer = 0
      Button.State = STATE_PRESSED
      if(Button.PressLengthSensitivity == False):
       Button.DoAction(self)
       Button.ActionDone = True

     elif(Button.State == STATE_PRESSED):
       if(Button.PressLengthSensitivity == True):
        if((Button.PressTimer >= LONG_PRESS_TRIGGER) and not Button.ActionDone): 
         Button.DoAction(self)
         Button.ActionDone = True

   else:

      if Button.State == STATE_PRESSED:

       if Button.ButtonType == TYPE_ALT:
        if self.AltState == STATE_PRESSED:
         self.AltState = STATE_RELEASED
         Button.State = STATE_RELEASED
        continue

       if(Button.PressLengthSensitivity == True):
        if(Button.PressTimer < LONG_PRESS_TRIGGER):
          Button.DoAction(self)
          Button.ActionDone = True

       Button.PressTimer = 0
       Button.State = STATE_RELEASED
       Button.ActionDone = False

      else: 

       if Button.BounceTimer <= Button.BounceWindow:
        Button.BounceTimer+=DISPATCH_LOOP_DLY
    
  time.sleep(DISPATCH_LOOP_DLY)


class GPIOButton:

 HardwareType = None            # pull-up (pressed - 0), pull-down (pressed - 1)
 ButtonType = None              # single mode, dual mode(on|off), alt
 PressLengthSensitivity = False # False|True
 GPIOid = None                  # integer - GPIO ID
 State = None                   # pressed, released
 Mode = None                    # on, off
 Name = None                    # button nickname - used in script/routine calls
 ActionType = None              # RunScript|CallPython

 PressTimer = 0                
 BounceTimer = 0                
 ActionDone = False
 
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
     if self.PressLengthSensitivity == False:
      self.DoOnAction(ButtonDispatcher)
     elif self.PressLengthSensitivity == True:
      if(self.PressTimer >= LONG_PRESS_TRIGGER):
       self.DoOnLongAction(ButtonDispatcher)
      else:
       self.DoOnAction(ButtonDispatcher)

    elif self.ButtonType == TYPE_DUALMODE:
     if self.PressLengthSensitivity == False:
      if self.Mode == MODE_OFF:
       self.DoOnAction(ButtonDispatcher)
       self.Mode = MODE_ON
      elif self.Mode == MODE_ON:
       self.DoOffAction(ButtonDispatcher)
       self.Mode = MODE_OFF
     elif self.PressLengthSensitivity == True:
      if(self.PressTimer >= LONG_PRESS_TRIGGER):
       self.DoOnLongAction(ButtonDispatcher)
      else:
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
   CallRoutine = getattr(sys.modules['__main__'],self.Name+"OnAction")
   CallRoutine()

 def DoOnLongAction(self,ButtonDispatcher):
  if self.ActionType == ACTION_EXTERNAL:
   RunScript = ButtonDispatcher.ExtScriptPath+"/"+self.Name+"_on_long_action"
   subprocess.call(RunScript)
  elif self.ActionType == ACTION_INTERNAL:
   CallRoutine = getattr(sys.modules['__main__'],self.Name+"OnLongAction")
   CallRoutine()
  
 def DoOffAction(self,ButtonDispatcher): 
  if self.ActionType == ACTION_EXTERNAL:
   RunScript = ButtonDispatcher.ExtScriptPath+"/"+self.Name+"_off_action"
   subprocess.call(RunScript)
  elif self.ActionType == ACTION_INTERNAL:
   CallRoutine = getattr(sys.modules['__main__'],self.Name+"OffAction")
   CallRoutine()

 def DoAltAction(self,ButtonDispatcher):
  if self.ActionType == ACTION_EXTERNAL:
   RunScript = ButtonDispatcher.ExtScriptPath+"/"+self.Name+"_alt_action"
   subprocess.call(RunScript)
  elif self.ActionType == ACTION_INTERNAL:
   CallRoutine = getattr(sys.modules['__main__'],self.Name+"AltAction")
   CallRoutine()

 def __init__(self, gpioid, name=str(GPIOid), hardware=PULL_DOWN, type=TYPE_SINGLEMODE, action=ACTION_NOACTION,
              sense_press_len=False):

  self.HardwareType = hardware
  self.GPIOid = gpioid
  self.ButtonType = type
  self.PressLengthSensitivity = sense_press_len
  self.Name = name
  self.State = STATE_RELEASED
  self.Mode = MODE_OFF
  self.ActionType = action
  self.BounceWindow = DEFAULT_BOUNCE_WINDOW

  GPIO.setup(self.GPIOid, GPIO.IN)


# end of ButtonDispatcher module

