#!/usr/bin/env python

"""
TriButtonRadio: ButtonDispatcher usage example 3 - control mpg123 as net radio with three buttons

  - button1 - radio on/off
  - button2 - next station
  - alt+button1 / alt+button2 - volume up/down

"""

from button_dispatcher import *
import time
import subprocess
import shlex
import re
import sys
import os

mpg123 = None
mpg123pipe = None

player_on = False

stations = []

stations_index = 0
stations_last = 0


MyDispatcher = ButtonDispatcher()

GPIO.setmode(GPIO.BCM)

MyDispatcher.GPIOInited = True

PlayerControlButton = GPIOButton(23,"PlayerControl",PULL_UP, TYPE_DUALMODE, ACTION_INTERNAL, LONG_ACTION)
MyDispatcher.Buttons.append(PlayerControlButton)

NextStationButton = GPIOButton(22,"NextStation",PULL_UP, TYPE_SINGLEMODE, ACTION_INTERNAL)
MyDispatcher.Buttons.append(NextStationButton)

AltButton = GPIOButton(24,"Alt",PULL_UP, TYPE_ALT)
MyDispatcher.Buttons.append(AltButton)


def PlayerControlOnAction():
  global mpg123,mpg123pipe,stations,player_on
 
  mpg123 = subprocess.Popen(shlex.split("mpg123 -R --fifo /tmp/mpg123"),stdout=subprocess.PIPE)
  time.sleep(1)
  mpg123pipe = open("/tmp/mpg123",'w+')
  mpg123pipe.write("load "+stations[stations_index]+"\n")
  mpg123pipe.flush()
  PlayerMessage("Player on. Current station: "+stations[stations_index].replace("\n",""))
  player_on = True

def PlayerControlOnLongAction():
  global mpg123,mpg123pipe,stations,player_on

  if player_on:
    mpg123pipe.write("quit\n")
    mpg123pipe.flush()
    time.sleep(1)
    mpg123.terminate()
    mpg123pipe.close()
    player_on = False
  PlayerMessage("Quit") 
  sys.exit()

def PlayerControlOffAction():
  global mpg123,mpg123pipe,player_on

  if player_on:
    mpg123pipe.write("quit\n")
    mpg123pipe.flush()
    time.sleep(1)
    mpg123.terminate()
    mpg123pipe.close()
    player_on = False
    PlayerMessage("Player off")


def PlayerControlAltAction():   # volume up
  subprocess.call(shlex.split("amixer -c 0 set PCM 1dB+ > /dev/null"))
  PlayerMessage("Volume up")


def NextStationOnAction():
  global mpg123pipe,stations,stations_index,stations_last

  if stations_index == (stations_last):
   stations_index = 0
  else:
   stations_index += 1

  mpg123pipe.write("load "+stations[stations_index]+"\n")
  mpg123pipe.flush()
  PlayerMessage("Current Station: "+stations[stations_index].replace("\n",""))


def NextStationAltAction():  # volume down 
  subprocess.call(shlex.split("amixer -c 0 set PCM 1dB- > /dev/null"))
  PlayerMessage("Volume down")


def FormatICY_META(ICY_META_string):
  tmp_arr = ICY_META_string.split("=")
  icy_title = tmp_arr[1].split(";")[0]
  icy_url = tmp_arr[2].split(";")[0]
  icy_title = icy_title.replace("'","")
  icy_url = icy_url.replace("'","")
  return icy_title,icy_url


def PlayerMessage(msgstring):
  term_height, term_width = os.popen('stty size', 'r').read().split()
  for num in range(1, int(term_width)-1):
   sys.stdout.write(" ")
  sys.stdout.write("\r")
  sys.stdout.write(" [ "+msgstring+" ]\r")
  sys.stdout.flush()



with open("TriButtonRadio.stations.cfg") as stationsfile:
 stations = stationsfile.readlines()

stations_last = len(stations) - 1

PlayerMessage("TriButtonRadio ready!")

while True:

 MyDispatcher.DispatchButtons()

 try:
  mpg123out = mpg123.stdout.readline()
  if(re.match(r'.*ICY-META.*',mpg123out)):
   icy_title,icy_url = FormatICY_META(mpg123out)
   PlayerMessage("Now playing: "+icy_title+", ("+icy_url+")")
 except:
  pass


