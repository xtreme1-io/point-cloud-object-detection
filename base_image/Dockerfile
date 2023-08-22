FROM nvidia/cuda:10.2-cudnn8-devel-ubuntu18.04

USER root
ENV DEBIAN_FRONTEND noninteractive

RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub \
    && apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64/7fa2af80.pub

RUN apt-get clean && apt-get update \
    && apt-get install -y apt-utils ca-certificates git wget sudo vim net-tools 

# install python
RUN apt-get install -y libffi-dev zlib1g-dev libssl-dev python3-dev python3-pip \
    && ln -svf /usr/bin/python3 /usr/bin/python \
    && ln -svf /usr/bin/pip3 /usr/bin/pip \
    && pip install --upgrade pip

# install PyTorch
RUN pip install Pillow==6.2 \
    && pip install torch==1.10.1+cu102 torchvision==0.11.2+cu102 torchaudio==0.10.1 -f https://download.pytorch.org/whl/torch_stable.html

# install spconv
RUN pip install spconv-cu102

WORKDIR /app

# install pcdet
ENV TORCH_CUDA_ARCH_LIST="5.0 5.2 6.0 6.1 7.0 7.5+PTX"
COPY . ./
RUN pip install -e .
