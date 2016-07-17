#!/usr/bin/python

import piexif
import sys

SEC_DEN = 50000000

def _parse(val):
    sign = 1
    if val < 0:
        val = -val
        sign = -1
    deg = int(val)
    other = (val - deg) * 60
    minutes = int(other)
    secs = (other - minutes) * 60
    secs = long(secs * SEC_DEN)
    return (sign, deg, minutes, secs)

with open("/tmp/position") as f:
    lat, lon = (float(f.readline()) for i in range(2))

exif = piexif.load(sys.argv[1])
gpsExif = exif["GPS"]
ifd = piexif.GPSIFD

sign, deg, min, sec = _parse(lat)
ref = "N"
if sign < 0: ref = "S"
gpsExif[ifd.GPSLatitudeRef] = ref
gpsExif[ifd.GPSLatitude] = ((deg, 1), (min, 1), (sec, SEC_DEN))

sign, deg, min, sec = _parse(lon)
ref = "E"
if sign < 0: ref = "W"
gpsExif[ifd.GPSLongitudeRef] = ref
gpsExif[ifd.GPSLongitude] = ((deg, 1), (min, 1), (sec, SEC_DEN))

piexif.insert(piexif.dump(exif), sys.argv[1])
