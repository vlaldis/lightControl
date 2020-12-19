# Light control using person/car detection

I'm pissed by motion sensor triggered by cats, birds and hedgehogs. Lights are going crazy during night.

I'll be using security camera to switch on lights when **person** OR **car** is detected.

Solution is designed to run on Nvidia Jetson Nano due to its computing abilities.


## Why?
**Because Why NOT?**

## Modules

### Camera source
```
usage: . [-h] [-i http://my.video.source.com/] [-f N] [-r server:port] [-s session-name] [-d]

Parse video input to separate frames.

optional arguments:
  -h, --help            show this help message and exit
  -i http://my.video.source.com/, --input http://my.video.source.com/
                        Source can be id of connected web camera or stream URL. Default '0' (internal web camera id).
  -f N, --fps N         Framerate per second. Default 1.
  -r server:port, --redis-server server:port
                        URL to redis server. Default 'redis:6379'.
  -s session-name, --session session-name
                        Session identification. Frames will be stored in redis under session-name:key. Default 'default'.
  -d, --debug           Write debug messages to console.
```
