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

# Instalation python libraries from egg files
echo "Removing old python libs"
sudo pip uninstall -y dk-wm
echo "Instaling  new python libs"
sudo easy_install soft/lib/*

# Configuration backup
#cp /opt/ss/testo/config.cfg testo/config.cfg

# clening destination localizations
sudo rm /opt/dk/wm/* -R

# Coping new files
sudo cp soft/* /opt/dk/wm/
sudo cp images /opt/dk/wm/ -R

checkPathAndCreate /usr/share/icons/dk-wm
sudo cp Desktop/icons/* /usr/share/icons/dk-wm

cp Desktop/*.desktop /home/pi/Desktop
