#!/bin/sh

read_path() {
	dir=/home/pi/app
	dir=$dir/$(cat $dir/path)
	if [ ! -d $dir ]; then
		mkdir $dir
		chown pi:pi $dir
	fi
}

read_path

exit_with_grace() {
	echo 0 > gpio21/value
	echo 5 > unexport
	echo 21 > unexport
	kill $childPIDs
	echo bye
	exit
}

trap read_path USR1

cd /home/pi/app
httpd.py 2> /tmp/httpd.log &
childPIDs=$!

date -us "$(gpsUTCtime.py)"
date

tmppos.py &
childPIDs="childPIDs $!"

cd /sys/class/gpio

echo 5 > export
echo 21 > export
echo out > gpio21/direction
trap exit_with_grace TERM QUIT

echo 1 > gpio21/value

while true; do
	if [ $(cat gpio5/value) = 1 ]; then
		echo 0 > gpio21/value
		path="$dir$(date +%y%m%d_%H%M%S).jpg"
		raspistill -o $path
		addGps.py $path
		chown pi:pi $path
		echo 1 > gpio21/value
	fi
done
