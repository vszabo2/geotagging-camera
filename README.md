# Raspberry Pi Geotagging Camera

A geotagging camera takes photos and records the geographic location into the image file.
I wrote the code in this repo a few years ago to make my own geotagging camera.

## Hardware Setup

* Raspberry Pi 2 Model B V1.1
* RPi camera V2.1 plugged into camera port
* Ribbon cable connected to breakout board/breadboard
* Adafruit Ultimate GPS Breakout v3 connected VIN -> 5V rail, GND -> GND rail, GPS TX -> RPI RXD
* LED connected between IO21 and resistor to GND. 
* Momentary pushbutton connected between 5V and IO5, with pull-down resistor. 
* WLAN adapter (optional, for downloading photos)
* USB Battery Pack and Micro-USB cable for power

I used 1 kΩ resistors in both places. I also put a coin cell in the GPS breakout so that a fix is acquired faster at subsequent power-ups.

## Basic Usage
 1. Power the Pi from the USB Battery Pack.
 2. Wait for the LED to turn on.
 3. Point the camera at the subject and "click" the pushbutton.
 4. The LED turns off. When the LED turns back on, the photo has been saved and you can repeat Step 3.

## Operating Principle
**storage partition** is mounted at /home/pi/app through fstab. It contains the folder `DCIM`, the file `last.zip`, and the file `path`, which contains, in my case, `"DCIM/folder/\n"`.

There are scripts in /usr/local/bin, which is on the PATH. 

**/etc/rc.local** contains `myScript.sh &`

**myScript.sh** kicks off httpd.py, then sets the system time from the GPS time using gpsUTCtime.py, then starts querying the GPS using tmppos.py. It also traps three signals. 

**myScript** turns on the LED when the camera is ready. When pin 5 goes high, it turns the LED off, takes a picture with raspistill, adds the position data to the picture with addGps.py, and makes pi the owner. Then it turns the LED back on.

**gpsUTCtime** waits for the GPS to get a fix and then prints out the time, converting it to a standard format. 

**tmppos** writes the latitude and longitude each on a line in /tmp/position every second. 

**addGps** uses the position from /tmp/position, the piexif library, and some math to add GPS EXIF data to the file specified in the first argument

**httpd.py** provides the primary user interface, which mainly consists of directory listings. It contains the entire webserver and its interesting pages, and it takes its files from /home/pi/app, which is the storage partition. It contains code from a variety of sources, none of which received credit. I wrote some cool code that uses SIGUSR1 to tell myScript to update the path to which it saves new images. There is also code that creates a zip file from the current folder. It stores the zip file in /home/pi while generating it, before moving it to /home/pi/app, where it is accessible to the web server. 

## Installation Instructions
 1. Connect hardware as described in [Hardware Setup](#hardware-setup)
 2. Install Raspbian on a 32 GB micro SD card, which will eventually be plugged into the Pi.
 3. Re-partition the SD Card as follows
    1. boot: 66.1MB fat16 bootable(lba)
    2. system: 4.295GB ext4
    3. storage: 27.6GB ext4
 4. Add a line to `/etc/fstab` (on the system partition) with this content:
    ```
    /dev/mmcblk0p3  /home/pi/app    ext4    defaults        0       2
    ```
 5. Add a line to `/etc/rc.local` (on the system partition) with this content: `myScript.sh &`
 6. Copy the following files from the repo to `/usr/local/bin/`
    * addGps.py
    * gpsUTCtime.py
    * httpd.py
    * myScript.sh
    * tmppos.py
 7. Install the Python libraries `piexif` and `gps`
