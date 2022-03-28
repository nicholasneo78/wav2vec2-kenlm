ARG BASE_CONTAINER=jupyter/minimal-notebook
FROM $BASE_CONTAINER

USER root

COPY requirements.txt .

ENV TZ=Asia/Singapore
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

#Downloading dependencies 
RUN apt-get update \
&& apt-get upgrade -y \
&& apt-get install -y \
&& apt-get -y install apt-utils gcc libpq-dev libsndfile1 ffmpeg cython wget \
&& apt-get -y install build-essential cmake libboost-system-dev libboost-thread-dev libboost-program-options-dev libboost-test-dev libeigen3-dev zlib1g-dev libbz2-dev liblzma-dev

RUN wget -O - https://kheafield.com/code/kenlm.tar.gz | tar xz

RUN mkdir kenlm/build && cd kenlm/build && cmake .. && make -j2

#Installing dependencies
RUN pip install -r requirements.txt

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID
WORKDIR /w2v2_kenlm