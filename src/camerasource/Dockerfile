FROM pythoncv

ENV SOURCE=0
ENV DELAY=1
ENV REDIS_SERVER=redis:6379
ENV SESSION=default
ENV PYTHONPATH="/data"

RUN mkdir -p /data/src && \
    touch /data/src/__init__.py

ADD ./camerasource /data/src/camerasource
ADD ./core /data/src/core

RUN pip3 install -r /data/src/camerasource/requirements.txt

ENTRYPOINT python3 /data/src/camerasource -i ${SOURCE} --delay ${DELAY} -r ${REDIS_SERVER} -s ${SESSION} -d
