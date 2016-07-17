cd /sys/class/gpio
echo $1 > export
sleep 0.5
echo out > gpio$1/direction
echo 1 > gpio$1/value
sleep 1
echo $1 > unexport
