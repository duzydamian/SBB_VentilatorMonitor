#!/bin/bash
#
# Script executed on device
#
# Author : Damian Karbowiak
# Company:
# Site   : 
#
# Date   : 13/07/2017
#

# function checks if given path exist and create if necessary
checkPathAndCreate() {
	if [ -d $1 ]; then
		echo "Directory: $1 exist"
	else
		echo "Directory: $1 created"
		sudo mkdir $1
	fi
}

# instalation extra software in system
sudo apt-get update
sudo apt-get install htop nano
sudo apt-get install zip unzip wget bash-completion

# instalation python libs
sudo pip install --upgrade pip
sudo pip install pygatt pyexpect

# create directories
checkPathAndCreate /opt/dk
checkPathAndCreate /opt/dk/wm

# execution script to install software
./update_script.sh

# asking if reboot system after instlation
echo "Reboot system (y/n)?"
read -p "Reboot system (y/n)?" CONT
if [ "$CONT" = "y" ]; then
	echo "REBOOT NOW"
	reboot
else
  echo "SOME CHANGES MAY BE AVAIBLE AFTER SYSTEM REBOOT";
fi
