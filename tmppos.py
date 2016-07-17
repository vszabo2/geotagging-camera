#!/usr/bin/python

import gps
import thread
import time

Gps = gps.gps(mode=gps.WATCH_ENABLE)

def myThread():
    while True:
        Gps.next()
thread.start_new_thread(myThread, ())

while True:
    f = open("/tmp/position", "w")
    line = str(Gps.fix.latitude) + "\n" + str(Gps.fix.longitude) + "\n"
    #print line
    f.write(line)
    f.close()
    time.sleep(1)
