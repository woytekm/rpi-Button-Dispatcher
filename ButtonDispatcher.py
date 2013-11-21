#!/usr/bin/python
#
# Button Dispatcher - main program
#

import Defs
import Config
import GPIOButton
from daemon import Daemon

import sys
import time
import subprocess

class ButtonDispatcher(Daemon):
  def run(self):

   while True:

    for button in Config.Buttons:
     if button.Pressed():
      if button.State == Defs.STATE_RELEASED:
       button.State = Defs.STATE_PRESSED
       button.DoAction()
      if button.ButtonType == Defs.TYPE_ALT:
       GPIOButton.AltPressed = True
       print "alt pressed"
     else:
      if button.State == Defs.STATE_PRESSED:
       button.State = Defs.STATE_RELEASED
       if button.ButtonType == Defs.TYPE_ALT:
        GPIOButton.AltPressed = False
        print "alt released"

    time.sleep(0.05)


Config.ConfigReadAndApply()  # read in the config file, initialize GPIO and button objects

if Config.Buttons:

 def DoOnAction(self):
  RunScript = Config.ScriptPath+"/"+self.Name+"_on_action.sh"
  subprocess.call(RunScript)
 
 def DoOffAction(self):
  RunScript = Config.ScriptPath+"/"+self.Name+"_off_action.sh"
  subprocess.call(RunScript)

 def DoAltAction(self):
  RunScript = Config.ScriptPath+"/"+self.Name+"_alt_action.sh"
  subprocess.call(RunScript)
 
 for button in Config.Buttons:
  button.DoOnAction = DoOnAction
  button.DoOffAction = DoOffAction
  button.DoAltAction = DoAltAction

else:
  print "No button definititions! Nothing to do - exit."

PIDFILE = '/var/run/button_dispatcher.pid'
LOGFILE = '/var/log/button_dispatcher.log'

if __name__ == "__main__":

        daemon = ButtonDispatcher(PIDFILE)

        if len(sys.argv) == 2:

                if 'start' == sys.argv[1]:
                        try:
                                daemon.start()
                        except:
                                pass

                elif 'stop' == sys.argv[1]:
                        print "Stopping ..."
                        daemon.stop()

                elif 'restart' == sys.argv[1]:
                        print "Restaring ..."
                        daemon.restart()

                elif 'status' == sys.argv[1]:
                        try:
                                pf = file(PIDFILE,'r')
                                pid = int(pf.read().strip())
                                pf.close()
                        except IOError:
                                pid = None
                        except SystemExit:
                                pid = None

                        if pid:
                                print 'ButtonDispatcher is running as pid %s' % pid
                        else:
                                print 'ButtonDispatcher is not running.'

                else:
                        print "Unknown command"
                        sys.exit(2)
                        sys.exit(0)
        else:
                print "usage: %s start|stop|restart|status" % sys.argv[0]
                sys.exit(2)

