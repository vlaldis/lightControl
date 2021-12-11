FROM nvcr.io/nvidia/l4t-base:r32.5.0 as gpio_base

ARG uid
ARG gid
ARG gid_gpio
RUN groupadd -f -r -g $gid_gpio gpio
RUN groupadd -f -r -g 1000 user

RUN useradd -M --uid $uid -g $gid_gpio user --groups uucp,$gid,user 
RUN mkdir -p /etc/sudoers.d \ 
   && echo 'user ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers.d/user \
   && echo 'Defaults exempt_group+=user' >> /etc/sudoers.d/user \
   && chmod a=r,o= /etc/sudoers.d/user


FROM gpio_base

ENV REDIS_SERVER=redis:6379
ENV SESSION=default
ENV DELAY=1.0
ENV PYTHONPATH="/data:/usr/lib/python3.6/dist-packages/"
ENV CONTROL_PIN=-1

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    python3-pip \
    nano

RUN python3 -m pip install --upgrade pip

RUN mkdir -p /data/src && \
    touch /data/src/__init__.py

ADD ./lightcontrol /data/src/lightcontrol
ADD ./core /data/src/core

RUN python3 -m pip install -r /data/src/lightcontrol/requirements.txt

ENTRYPOINT python3 /data/src/lightcontrol/__main__.py -r ${REDIS_SERVER} -s ${SESSION} -d --period ${DELAY} --control-pin ${CONTROL_PIN}
