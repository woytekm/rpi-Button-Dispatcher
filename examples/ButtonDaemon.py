#!/usr/bin/python

""" ButtonDaemon - daemon which will execute different shell scripts when GPIO buttons are pressed """

from button_dispatcher import *
from daemon import daemon
import time
import sys

class ButtonDispatcherDaemon(Daemon):

  def run(self):

   ConfigPath = "ButtonDaemon.cfg"

   MyDispatcher = ButtonDispatcher()
   MyDispatcher.InitFromFile(ConfigPath)

   if not MyDispatcher.Buttons:
    print "No button definititions loaded! Nothing to do - exit."
    sys.exit()

   while True:
    MyDispatcher.DispatchButtons()
    time.sleep(0.05)


PIDFILE = '/var/run/button_dispatcher.pid'

if __name__ == "__main__":

        daemon = ButtonDispatcherDaemon(PIDFILE)

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


