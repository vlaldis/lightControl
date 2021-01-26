FROM dustynv/jetson-inference:r32.4.3

ENV SOURCE=0
ENV FPS=1
ENV REDIS_SERVER=redis:6379
ENV SESSION=default
ENV ZMQ=zmq:3000
ENV NETWORK=ssd-mobilenet-v2
ENV OVERLAY=box,labels,conf
ENV THREASHOLD=0.5
ENV PYTHONPATH="/data:/usr/lib/python3.6/dist-packages/"

RUN mkdir -p /data/src && \
    touch /data/src/__init__.py && \
    mkdir /inference && \
    apt install -y git cmake libpython3-dev

ADD ./objectdetector /data/src/objectdetector
ADD ./core /data/src/core

# #start
# RUN apt-get install -y git cmake libpython3-dev python3-numpy
# RUN git clone --recursive https://github.com/dusty-nv/jetson-inference
# RUN mkdir -p /jetson-inference/build

# RUN apt-get install python2.7 python3.7
# WORKDIR /jetson-inference/build
# RUN cmake ../ && make -j$(nproc) && make install && ldconfig
# #end

RUN pip3 install --upgrade pip
RUN pip3 install -r /data/src/objectdetector/requirements.txt

ENTRYPOINT python3 /data/src/objectdetector -n ${NETWORK} -o ${OVERLAY} -t ${THREASHOLD} -r ${REDIS_SERVER} -q ${ZMQ} -s ${SESSION} -d
