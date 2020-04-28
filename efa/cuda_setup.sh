#! /bin/bash

###################################################
# Pin MPI EFA and NCCL version
###################################################

EFA_VERSION=1.8.4
OPENMPI_VERSION=4.0.1
NCCL_VERSION=2.5.6-2

###################################################
# Download and install EFA driver
###################################################
cd

curl -O  https://s3-us-west-2.amazonaws.com/aws-efa-installer/aws-efa-installer-${EFA_VERSION}.tar.gz

tar -xf aws-efa-installer-${EFA_VERSION}.tar.gz

cd aws-efa-installer

sudo ./efa_installer.sh -y

sudo sed -i 's/kernel.yama.ptrace_scope = 1/kernel.yama.ptrace_scope = 0/g' \
	/etc/sysctl.d/10-ptrace.conf

###################################################
# Install CUDA
###################################################
cd

wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-ubuntu1804.pin

sudo mv cuda-ubuntu1804.pin /etc/apt/preferences.d/cuda-repository-pin-600

sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub

sudo add-apt-repository "deb http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/ /"

sudo apt-get update

sudo apt-get -y install cuda

###################################################
# Install NCCL
###################################################
cd

wget https://github.com/NVIDIA/nccl/archive/v${NCCL_VERSION}.tar.gz

tar -xf  v${NCCL_VERSION}.tar.gz

mv nccl-${NCCL_VERSION} nccl

cd nccl

make -j src.build