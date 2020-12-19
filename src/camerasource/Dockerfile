FROM  ubuntu:20.04 as pythoncv

RUN apt update -y &&\
    apt upgrade -y
RUN apt install -y python3 python3-pip
RUN python3 -m pip install opencv-python

ENTRYPOINT [ "cat" ]


FROM pythoncv
ENV SOURCE=0
ENV FPS=1
ENV REDIS_SERVER=redis:6379
ENV SESSION=default

ADD . /camerasource

RUN python3 -m pip install -r /camerasource/requirements.txt

ENTRYPOINT python3 /camerasource -i ${SOURCE} -f ${FPS} -r ${REDIS_SERVER} -s ${SESSION} -d
