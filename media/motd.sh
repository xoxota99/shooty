#!/bin/bash

 let upSeconds="$(/usr/bin/cut -d. -f1 /proc/uptime)"
 let secs=$((${upSeconds}%60))
 let mins=$((${upSeconds}/60%60))
 let hours=$((${upSeconds}/3600%24))
 let days=$((${upSeconds}/86400))
 UPTIME=`printf "%d days, %02dh%02dm%02ds" "$days" "$hours" "$mins" "$secs"`

 # get the load averages
 read one five fifteen rest < /proc/loadavg

 echo "
  ____  _                 _          Uptime........: ${UPTIME}
 / ___|| |__   ___   ___ | |_ _   _  Memory........: `cat /proc/meminfo | grep MemFree | awk {'print $2'}`kB (Free) / `cat /proc/meminfo | grep MemTotal | awk {'print $2'}`kB (Total)
 \___ \| '_ \ / _ \ / _ \| __| | | | Load Averages.: ${one}, ${five}, ${fifteen} (1, 5, 15 min)
  ___) | | | | (_) | (_) | |_| |_| | Running.......: `ps ax | wc -l | tr -d " "` processes
 |____/|_| |_|\___/ \___/ \__|\__, | IP Addr.......: `/sbin/ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'` and `wget -q -O - http://icanhazip.com/ | tail`
                              |___/  Free Space....: `df -Pm | grep -E '^/dev/root' | awk '{ print $4 }' | awk -F '.' '{ print $1 }'`MB on /dev/root
"
