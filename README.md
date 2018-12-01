# youtube2mp3
This is a Python program that allows you to convert youtube videos to mp3 by sending a youtube link to your email. This program monitors that inbox and will convert the videos and email them back.

---

### System App Versions

#### [ffmpeg]
```python
pi@raspberrypi:~/Documents/Python/youtube2mp3 $ ffmpeg -version
```
```python
ffmpeg version 3.4.5 Copyright (c) 2000-2018 the FFmpeg developers
built with gcc 4.9.2 (Raspbian 4.9.2-10+deb8u1)
configuration: --enable-libmp3lame --enable-libv4l2 --enable-opengl
libavutil      55. 78.100 / 55. 78.100
libavcodec     57.107.100 / 57.107.100
libavformat    57. 83.100 / 57. 83.100
libavdevice    57. 10.100 / 57. 10.100
libavfilter     6.107.100 /  6.107.100
libswscale      4.  8.100 /  4.  8.100
libswresample   2.  9.100 /  2.  9.100
```

---

### Youtube-dl Download and Installation

#### [curl]
**To install it right away for all UNIX users (Linux, OS X, etc.), type:**
```python
sudo curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl

sudo chmod a+rx /usr/local/bin/youtube-dl
```

#### [wget]
**If you do not have curl, you can alternatively use a recent wget:**
```python
sudo wget https://yt-dl.org/downloads/latest/youtube-dl -O /usr/local/bin/youtube-dl

sudo chmod a+rx /usr/local/bin/youtube-dl
```

[youtube-dl website](https://rg3.github.io/youtube-dl/download.html)

---

### Scripts

#### [crontab]

```python
pi@raspberrypi:~/Documents/Python/youtube2mp3 $ sudo crontab -l -u root | egrep -i youtube
```
```python
* * * * * /bin/bash /home/pi/.youtube2mp3/scripts/is_youtube2mp3_running.sh
```
