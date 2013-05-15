#! /bin/bash

#rev 0.1
#who is in via bash
#Emilio Del Plato 5/14/2013

#example ping to bt device
#l2ping 5C:6B:32:49:36:B6 -c 3

declare -A btaddr
btaddr[Karen]='5C:6B:32:49:36:B6'
btaddr[Emilio]='04:E4:51:10:10:B0'
btaddr[Pebble]='00:18:33:E4:F2:F0'
btaddr[noname]='00:00:00:00:00:01'

for i in "${!btaddr[@]}"
do 
	:
	l2ping ${btaddr[$i]} -c 3 &> /dev/null
	status=$?
	if [ $status -eq 0 ];
	then
		echo "$i (${btaddr[$i]}) is in range. exit status : $status"
	else
		echo "$i is out of range. exit status : $status"
	fi
done

