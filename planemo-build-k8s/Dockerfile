FROM ubuntu:18.04

RUN sed -i -e "s/ports.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g" \
        -e "s/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g"  \
        -e "s/security.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g" /etc/apt/sources.list
WORKDIR /home

COPY get-pip.py get-pip.py

RUN    apt-get update \
    && apt-get install -y python3.7 curl python3-pip \
    && python3.7 get-pip.py \
    && ln -s /usr/bin/python3.7 /usr/bin/python \
    && pip install -i https://pypi.tuna.tsinghua.edu.cn/simple planemo
