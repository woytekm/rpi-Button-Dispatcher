#
# Config reading and applying for Button Dispatcher
#

import GPIOButton
import Defs
import RPi.GPIO as GPIO

ConfigPath = "/etc/ButtonDispatcher/ButtonDispatcher.cfg"  # default cfg file
ScriptPath = "/etc/ButtonDispatcher/scripts"               # default script dir 

GPIONumbering = "BOARD"                                    # BOARD|BCM, default = BOARD

Buttons = []                                               # list of Button objects

GPIOInited = False

def ConfigReadAndApply():

 global ConfigPath
 global ScriptPath
 global GPIONumbering
 global Buttons
 global GPIOInited

 try: 
   cfgfile = open(ConfigPath)

 except:
  print "Cannot open config file /etc/ButtonDispatcher/ButtonDispatcher.cfg"
  return

 ConfLine = 0
 
 for cfgline in cfgfile:

      ConfLine += 1
      badconf = 0

      fields = cfgline.split()
     
      if(len(fields) < 2):
       continue

      if(fields[0].lower() == "scriptpath") and (len(fields[1]) > 0):
        ScriptPath = fields[1]
        continue

      if(fields[0].lower() == "gpionumbering"):
        if((fields[1].lower() == "board") or (fields[1].lower() == "bcm")):
         GPIONumbering = fields[1]
         continue
        else:
         badconf = 1
 
      if badconf:
       print "Error in line ",ConfLine," of ",ConfigPath

      if(fields[0].lower() == "button"):

       if(fields[3].lower() == "pullup"): 
        btnhardware = Defs.PULL_UP
       elif (fields[3].lower() == "pulldown"):
        btnhardware = Defs.PULL_DOWN
       else:
        badconf = 1

       if(fields[4].lower() == "singlemode"):
        btntype = Defs.TYPE_SINGLEMODE
       elif (fields[4].lower() == "dualmode"):
        btntype = Defs.TYPE_DUALMODE
       else:
        badconf = 1 
        
       gpioid = int(fields[1])

       if(gpioid < 27) and (gpioid > 0):
        pass
       else:
        badconf = 1

       btn_name = fields[2]
      
       if(len(btn_name) < 255):
        pass
       else:
        badconf = 1
 
       if badconf:
        print "Bad button definition in ",ConfigPath," line ", ConfLine
        continue 
     
       if not GPIOInited: 
        if GPIONumbering == "BOARD":
          GPIO.setmode(GPIO.BOARD)
        elif GPIONumbering == "BCM":
          GPIO.setmode(GPIO.BCM)
        GPIOInited = True
         
       NewButton = GPIOButton.Button(gpioid, btn_name, btnhardware, btntype)

       Buttons.append(NewButton) 



