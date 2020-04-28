#! /bin/bash

cd

sudo
sudo apt-get install -y libudev-dev dh-autoreconf

git clone -b aws https://github.com/aws/aws-ofi-nccl.git

cd aws-ofi-nccl

./autogen.sh

./configure --with-libfabric=/opt/amazon/efa \
	    --with-cuda=/usr/local/cuda \
	    --with-nccl=/home/ubuntu/nccl/build \
	    --with-mpi=/opt/amazon/openmpi \
	    --prefix=/home/ubuntu/aws-ofi-nccl/install
