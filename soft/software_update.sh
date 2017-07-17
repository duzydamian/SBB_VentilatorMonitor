#!/bin/bash
#
#
# Script update software package and create archive
# Next depend on parameter send to device and install or update
#
# Author : Damian Karbowiak
# Company: 
# Site   : 
#
# Date   : 13/75/2017
#

# IF YOU DON'T WANT TO ENETER SSH PASSWORD EVERY TIME 
# RUN THIS COMMANDS, 192.168.94.25 DESTINATION IP
# ssh-keygen
# ssh-copy-id -i ~/.ssh/id_rsa.pub root@192.168.94.25
# TO TEST:
# ssh pi@192.168.94.25

# function checks if given path exist and create if necessary
checkPathAndCreate() {
	if [ -d $1 ]; then
		echo "Directory: $1 exist"
		return 0
	else
		echo "Directory: $1 created"
		mkdir $1
		return 1
	fi
}

u=false
i=false
l=false
c=false
ipf=false
portf=false
ip_default=192.168.1.10
port_default=22
revision=$(git rev-list --count HEAD)
#revision=1
version=1.0

if [ "$#" -gt 0 ]; then
	for arg in "$@"; 
	do 
		case "$arg" in
		-u)    c=true; u=true;;
		-i)    c=true; i=true;;
		-l)    l=true;;
		-c)    c=true;;
		-ip*)  ipf=true ip_arg=${arg##*ip};;
		-p*)   portf=true port_arg=${arg##*p};;
		esac
	done
else
	echo "No parameters"
	echo "Supported parameters are:"
	echo -e "-i\t\t-\t Install software on rasp"
	echo -e "-u\t\t-\t Update software on rasp"
	echo -e "-c\t\t-\t Create update archive"
	echo -e "-l\t\t-\t Update on local machine"
	echo -e "-ip x.x.x.x\t-\t Set x.x.x.x IP for update/install"
	echo -e "-p x\t-\t Set x port for update/install"
fi

if $ipf; then
	ip=$ip_arg
else
	ip=$ip_default
fi

if $portf; then
	port=$port_arg
else
	port=$port_default
fi

if $c; then
	echo "Clean dest folder"	
	if checkPathAndCreate dk-wm; then
		rm dk-wm/* -R
	fi

	echo "Compiling programs"
	echo "PYTHON"
	cd VentilatorMonitor/src; python setup.py bdist_egg --exclude-source-files --version $version.$revision; cd ../..

	echo "Copy required files"
	cp install_script.sh update_script.sh dk-wm/
	checkPathAndCreate dk-wm/soft
	checkPathAndCreate dk-wm/soft/lib

	cp VentilatorMonitor/src/VentilatorMonitor* dk-wm/soft/ -v
	cp VentilatorMonitor/src/dist/* dk-wm/soft/lib/ -v
	cp VentilatorMonitor/src/images dk-wm/ -v -R
	cp Desktop dk-wm/ -v -R

	echo "Create archive"
	rm dk-wm.zip
	zip -rq dk-wm.zip dk-wm
fi

if $i; then
	echo "Copy new software to rasp:" $ip -P$port
	scp -P$port dk-wm.zip pi@$ip:dk-wm.zip
	echo "Install software on rasp:" $ip -P$port
	ssh -p$port pi@$ip "rm dk-wm -R; unzip -q dk-wm.zip; cd dk-wm; ./install_script.sh"	
fi

if $u; then
	echo "Copy new software to rasps:" $ip-P$port
	scp -P$port dk-wm.zip pi@$ip:dk-wm.zip
	echo "Update oftware on rasp:" $ip -P$port
	ssh -p$port pi@$ip "rm dk-wm -R; unzip -q dk-wm.zip; cd dk-wm; ./update_script.sh"
fi

echo "FINISH"
