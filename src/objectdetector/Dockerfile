FROM pythoncv

ENV SOURCE=0
ENV FRAME_DELAY=1
ENV REDIS_SERVER=redis:6379
ENV SESSION=default
ENV FROZEN_MODEL="/data/frozen_inference_graph.pb"
ENV LABEL_MAP="/data/mscoco_label_map.pbtxt"
ENV THREASHOLD=0.5
ENV PYTHONPATH="/data:/usr/lib/python3.6/dist-packages/"

RUN mkdir -p /data/src && \
    touch /data/src/__init__.py

ADD ./objectdetector /data/src/objectdetector
ADD ./core /data/src/core

RUN pip3 install --upgrade pip
RUN pip3 install -r /data/src/objectdetector/requirements.txt

ENTRYPOINT python3 /data/src/objectdetector -m ${FROZEN_MODEL} -l ${LABEL_MAP} -t ${THREASHOLD} -r ${REDIS_SERVER} -s ${SESSION} -d --frame-delay {FRAME_DELAY}
