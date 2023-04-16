#!/bin/bash

printf '#############################################\nStart of ecosystem monitoring startup script\n############################################\n'

# One off expanding of filesystem to fill SD card
if [ ! -f fs_expanded ]; then
  sudo touch fs_expanded
  sudo raspi-config --expand-rootfs
  sudo reboot
fi

# Restart udev to simulate hotplugging of 3G dongle
sudo service udev stop
sudo service udev start

tries=0
max_tries=5
while true; do
	timeout 2s wget -q --spider http://google.com
	if [ $? -eq 0 ]; then
		printf "Online\n"
    break
	else
	    printf "Offline\n"
	fi
	printf 'Waiting for internet connection before continuing ('$max_tries' tries max)\n'
	sleep 1
	let tries=tries+1
	if [[ $tries -eq $max_tries ]] ;then
		break
	fi
done	

# Change to correct folder
cd /home/pi/multi-channel-rpi-eco-monitoring

# Update time from internet
sudo bash ./bash_update_time.sh

# Start ssh-agent so password not required
eval $(ssh-agent -s)

# Add in current date and time to log files
currentDate=$(date +"%Y-%m-%d_%H.%M")

# Check the config exists
config_file="./config.json"
if [ ! -f $config_file ]; then
    echo "Config file not found! Run \'python setup.py\' to generate one";
    exit 1
fi

# export the raspberry pi serial number to an environment variable
export PI_ID=$(python discover_serial.py)

# the file in which to store to store the logging from this run
logdir='logs'
logfile_name="multi_rpi_eco_"$PI_ID"_"$currentDate".log"

# Start recording script
printf 'End of startup script\n'
sudo -E python3 -u python_record.py $config_file $logfile_name $logdir
