FROM  jjanzic/docker-python3-opencv:opencv-4.0.0

ENV SOURCE=0
ENV FPS=1
ENV REDIS_SERVER=redis:6379
ENV SESSION=default

RUN pip install --upgrade pip

ADD . /camerasource

RUN pip install -r /camerasource/requirements.txt

ENTRYPOINT python3 /camerasource -i ${SOURCE} -f ${FPS} -r ${REDIS_SERVER} -s ${SESSION} -d
