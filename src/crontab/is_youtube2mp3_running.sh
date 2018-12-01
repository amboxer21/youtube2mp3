#!/bin/bash

if [[ `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python /usr/local/bin/youtube2mp3.py" | wc -l` < 1 ]]; then 
    logger -i -t youtube2mp3 "Youtube2mp3 is not running, starting youtube2mp3." -f /var/log/youtube2mp3.log
    /usr/bin/python /usr/local/bin/youtube2mp3.py &
elif [[ `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python /usr/local/bin/youtube2mp3.py" | wc -l` > 1 ]]; then 
    logger -i -t youtube2mp3 "Killing youtube2mp3." -f /var/log/youtube2mp3.log
    /usr/bin/sudo /bin/kill -9 `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python /usr/local/bin/youtube2mp3.py" | /usr/bin/awk '{print $2}'`;
else
    logger -i -t youtube2mp3 "Youtube2mp3 is already running." -f /var/log/youtube2mp3.log
fi
