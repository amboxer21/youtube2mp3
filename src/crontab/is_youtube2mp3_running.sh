#!/bin/bash

path='/usr/bin'
y2m='youtube2mp3'
logfile="/var/log/${y2m}.log"
youtube2mp3="/usr/local/bin/${y2m}.py"

if [[ `/bin/ps aux | $path/awk '/^root.*:[0-9]{1,2}.*youtube2mp3.py/{if($11 !~ /sudo|vim|awk/) print}' | wc -l` -eq 0 ]]; then 
    $path/logger -i -t youtube2mp3 "Youtube2mp3 is not running, starting youtube2mp3." -f $logfile;
    $path/sudo $path/python $youtube2mp3 &
elif [[ `/bin/ps aux | $path/awk '/^root.*:[0-9]{1,2}.*youtube2mp3.py/{if($11 !~ /sudo|vim|awk/) print}' | wc -l` -gt 3 ]]; then 
    /bin/ps aux | $path/awk '/^root.*:[0-9]{1,2}.*youtube2mp3.py/{if($11 !~ /sudo|vim|awk/) print}'
    $path/logger -i -t youtube2mp3 "Killing youtube2mp3." -f $logfile;
    $path/sudo /bin/kill -9 `/bin/ps aux | $path/awk '/^root.*:[0-9]{1,2}.*youtube2mp3.py/{if($11 !~ /sudo|vim|awk/) print $2}'`;
    $path/sudo $path/python $youtube2mp3 &
elif [[ `/bin/ps aux | $path/awk '/^root.*:[0-9]{1,2}.*youtube2mp3.py/{if($11 !~ /sudo|vim|awk/) print}' | wc -l` -eq 1 ]]; then
    /bin/ps aux | $path/awk '/^root.*:[0-9]{1,2}.*youtube2mp3.py/{if($11 !~ /sudo|vim|awk/) print}'
    $path/logger -i -t youtube2mp3 "Youtube2mp3 is already running." -f $logfile;
fi
