#!/bin/bash

path='/usr/bin'
y2m='youtube2mp3'
logfile="/var/log/${y2m}.log"
youtube2mp3="/usr/local/bin/${y2m}.py"

if (( `/bin/ps aux | $path/awk "/$regex/{print}" | wc -l` < 1 )); then 
    $path/logger -i -t youtube2mp3 "Youtube2mp3 is not running, starting youtube2mp3." -f $logfile;
    $path/sudo $path/python $youtube2mp3 &
    exit;
elif (( `/bin/ps aux | $path/awk "/$regex/{print}" | wc -l` > 2 )); then 
    $path/logger -i -t youtube2mp3 "Killing youtube2mp3." -f $logfile;
    $path/sudo /bin/kill -9 `/bin/ps aux | $path/awk '/[0-9]{1,2}:[0-9]{1,2} .usr.bin.python .usr.local.bin.youtube2mp3/{print $2}'`
    $path/sudo $path/python $youtube2mp3 &
    if (( $? != 0 ));  then
        $path/logger -i -t youtube2mp3 'Failed to kill processes!' -f $logfile;
    fi
    exit;
elif (( `/bin/ps aux | $path/awk "/$regex/{print}" | wc -l` == 1 )); then
    $path/logger -i -t youtube2mp3 "Youtube2mp3 is already running." -f $logfile;
    exit;
fi
