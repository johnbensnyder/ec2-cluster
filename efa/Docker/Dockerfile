FROM nvidia/cuda:10.2-base-ubuntu18.04

LABEL maintainer="Amazon AI"

# prevent stopping by user interaction
ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true
ENV SAGEMAKER_TRAINING_MODULE sagemaker_tensorflow_container.training:main

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Set environment variables for MKL
# For more about MKL with TensorFlow see:
# https://www.tensorflow.org/performance/performance_guide#tensorflow_with_intel%C2%AE_mkl_dnn
ENV KMP_AFFINITY=granularity=fine,compact,1,0
ENV KMP_BLOCKTIME=1
ENV KMP_SETTINGS=0

ARG PYTHON=python3
ARG PYTHON_PIP=python3-pip
ARG PIP=pip3

ARG TF_URL=https://tensorflow-aws.s3-us-west-2.amazonaws.com/2.1/AmazonLinux/gpu/final/tensorflow_gpu-2.1.0-cp36-cp36m-manylinux2010_x86_64.whl

ARG NCCL_VERSION=2.5.6-2
ARG OPENMPI_VERSION_MINOR=4.0.1
ARG OPENMPI_VERSION_MAJOR=4.0

RUN apt-get update && apt-get install -y --no-install-recommends --allow-unauthenticated \
    python3-dev \
    python3-pip \
    python3-setuptools \
    ca-certificates \
    cuda-command-line-tools-10-1 \
    cuda-cudart-dev-10-1 \
    cuda-cufft-dev-10-1 \
    cuda-curand-dev-10-1 \
    cuda-cusolver-dev-10-1 \
    cuda-cusparse-dev-10-1 \
    curl \
    libcudnn7=7.6.2.24-1+cuda10.1 \
    libgomp1 \
    libfreetype6-dev \
    libhdf5-serial-dev \
    libpng-dev \
    libzmq3-dev \
    git \
    wget \
    vim \
    build-essential \
    openssh-client \
    openssh-server \
    zlib1g-dev \
    # Install dependent library for OpenCV
    libgtk2.0-dev \
    #cuda-cublas-dev not available with 10-1, install libcublas instead
    #it will downgrade the cublas from 10-2 to 10-1
    #adding an extra flag --allow-downgrades for it
    && apt-get update \
    && apt-get install -y --no-install-recommends --allow-unauthenticated --allow-downgrades \
    libcublas10=10.1.0.105-1 \
    libcublas-dev=10.1.0.105-1 \
 && apt-get update && apt-get install -y --no-install-recommends --allow-unauthenticated  \
    nvinfer-runtime-trt-repo-ubuntu1804-5.0.2-ga-cuda10.0 \
 && apt-get update && apt-get install -y --no-install-recommends --allow-unauthenticated  \
    libnvinfer6=6.0.1-1+cuda10.1 \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir -p /var/run/sshd

##########################################################################
# Install NCCL, MPI, and EFA adapter
# Note that EFA driver does not install properly in Dockerfile
# But matching driver is needed to compile nccl adapter used
# within the docker container. The solution is to build
# the Docker image on the DL AMI by copying EFA drivers
# into Docker build environment, then temporarily copy
# drivers into image
# cp -R /opt/amazon/efa .
#########################################################################

RUN cd / \
    && wget https://github.com/NVIDIA/nccl/archive/v${NCCL_VERSION}.tar.gz \
    && tar -xf  v${NCCL_VERSION}.tar.gz \
    && mv nccl-${NCCL_VERSION} nccl \
    && cd nccl \
    && make -j src.build

# copy local efa drivers into image
COPY efa /efa

# Install Open MPI
RUN mkdir /tmp/openmpi \
 && cd /tmp/openmpi \
 && curl -fSsL -O https://download.open-mpi.org/release/open-mpi/v${OPENMPI_VERSION_MAJOR}/openmpi-${OPENMPI_VERSION_MINOR}.tar.gz \
 && tar zxf openmpi-${OPENMPI_VERSION_MINOR}.tar.gz \
 && cd openmpi-${OPENMPI_VERSION_MINOR} \
 && ./configure --enable-orterun-prefix-by-default \
 && make -j $(nproc) all \
 && make install \
 && ldconfig \
 && rm -rf /tmp/openmpi

RUN echo NCCL_DEBUG=INFO >> /etc/nccl.conf

ENV LD_LIBRARY_PATH=/usr/local/cuda/extras/CUPTI/lib64:/usr/local/openmpi/lib:$LD_LIBRARY_PATH
ENV PATH /usr/local/openmpi/bin/:$PATH
ENV PATH=/usr/local/nvidia/bin:$PATH

# Download EFA NCCL adapter
RUN cd / \
    && git clone https://github.com/aws/aws-ofi-nccl.git -b aws \
    && cd aws-ofi-nccl \
    && apt-get update && apt-get install -y libudev-dev dh-autoreconf \
    && ./autogen.sh \
    && ./configure \
       --with-libfabric=/efa \
       --with-cuda=/usr/local/cuda \
       --with-nccl=/nccl/build \
       --with-mpi=/usr/local \
       --prefix=/aws-ofi-nccl/install \
    && make && make install

# Delete efa driver from image
RUN rm -rf /efa
