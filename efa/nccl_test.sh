#! /bin/bash

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/amazon/efa/lib:/opt/amazon/openmpi/lib:/home/ubuntu/nccl/build/lib:/home/ubuntu/aws-ofi-nccl/install/lib

export INCLUDE_PATH=$INCLUDE_PATH:/opt/amazon/efa/include/:/opt/amazon/openmpi/include:/home/ubuntu/nccl/build/include

export PATH=$PATH:/opt/amazon/efa/bin:/opt/amazon/openmpi/bin

source ~/.bashrc

cd

git clone https://github.com/NVIDIA/nccl-tests.git

cd nccl-tests

make MPI=1 MPI_HOME=/opt/amazon/openmpi NCCL_HOME=/home/ubuntu/nccl/build

mpirun -x FI_PROVIDER="efa" \
       -x LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/amazon/efa/lib:/opt/amazon/openmpi/lib:/home/ubuntu/nccl/build/lib:/home/ubuntu/aws-ofi-nccl/install/lib \
       -x NCCL_DEBUG=INFO -H 127.0.0.1:8 \
       /home/ubuntu/nccl-tests/build/all_reduce_perf -b 8 -e 1G -f 2 -c0