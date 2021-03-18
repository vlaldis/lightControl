# FROM nvcr.io/nvidia/l4t-tensorflow:r32.5.0-tf2.3-py3
FROM pythoncv

ENV SOURCE=0
ENV DELAY=1.0
ENV REDIS_SERVER=redis:6379
ENV SESSION=default
ENV FROZEN_MODEL="/data/frozen_inference_graph.pb"
ENV THREASHOLD=0.5
ENV PYTHONPATH="/data:/usr/lib/python3.6/dist-packages/"

RUN apt update -y && \
    apt install -y --no-install-recommends \
    python3-pip
	libv4l-dev \
	libv4l-0 \
	v4l-utils \
    libavcodec-dev \
	libavformat-dev \
	libswscale-dev \
	libxvidcore-dev \
	libx264-dev

# RUN pip3 install --upgrade pip

RUN mkdir -p /data/src && \
    touch /data/src/__init__.py

ADD ./objectdetector /data/src/objectdetector
ADD ./core /data/src/core

RUN pip3 install -r /data/src/objectdetector/requirements.txt

ENTRYPOINT python3 /data/src/objectdetector/__main__.py -i ${SOURCE} -m ${FROZEN_MODEL} -t ${THREASHOLD} -r ${REDIS_SERVER} -s ${SESSION} -d --delay ${DELAY}
