#!/usr/bin/python

import gps
import thread

Gps = gps.gps(mode=gps.WATCH_ENABLE)

def myThread():
    while True:
        Gps.next()

thread.start_new_thread(myThread, ())

while True:
    time = Gps.fix.time
    if isinstance(time, unicode):
        time = time[:10] + " " + time[11:19] #convert `time` into format readable by `date`
        print time
        break
