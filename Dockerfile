ARG BASE_CONTAINER=python:3.8.13-slim-buster 
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
&& apt-get -y install apt-utils gcc libpq-dev libsndfile1 ffmpeg cython wget git \
&& apt-get -y install build-essential cmake libboost-system-dev libboost-thread-dev libboost-program-options-dev libboost-test-dev libeigen3-dev zlib1g-dev libbz2-dev liblzma-dev

RUN wget -O - https://kheafield.com/code/kenlm.tar.gz | tar xz

# build kenlm from source
RUN mkdir kenlm/build && cd kenlm/build && cmake .. && make -j2

# build ctc-segmentation from source
# RUN git clone https://github.com/lumaku/ctc-segmentation \
# && cd ctc-segmentation \
# && cython -3 ctc_segmentation/ctc_segmentation_dyn.pyx \
# && python setup.py build \
# && python setup.py install --optimize=1 --skip-build

# numpy problems
#RUN pip uninstall -y numpy --no-cache-dir
RUN pip install numpy==1.15.1 --no-binary numpy

#Installing dependencies
RUN pip install -r requirements.txt

# build ctcdecode from source
RUN git clone --recursive https://github.com/parlance/ctcdecode.git \
&& cd ctcdecode \ 
&& pip install .

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID
WORKDIR /w2v2_kenlm