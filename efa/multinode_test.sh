#! /bin/bash

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/amazon/efa/lib:/opt/amazon/openmpi/lib
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/nccl/build/lib:$HOME/aws-ofi-nccl/install/lib

export INCLUDE_PATH=$INCLUDE_PATH:/opt/amazon/efa/include:/opt/amazon/openmpi/include
export INCLUDE_PATH=$INCLUDE_PATH:$HOME/nccl/build/include:$HOME/aws-ofi-nccl/install/include

export PATH=$PATH:/opt/amazon/efa/bin:/opt/amazon/openmpi/bin

source $HOME/.bashrc

echo "Running with EFA"

mpirun -x FI_PROVIDER="efa" \
                --prefix /opt/amazon/openmpi \
                 -x LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/amazon/efa/lib:/opt/amazon/openmpi/lib:$HOME/nccl/build/lib:$HOME/aws-ofi-nccl/install/lib \
                 -x NCCL_DEBUG=INFO \
                 -x NCCL_TREE_THRESHOLD=0 \
                 -x NCCL_SOCKET_IFNAME=ens5 \
                 --hostfile $HOME/hosts \
                 --mca oob_tcp_if_include ens5 \
                 --mca btl_tcp_if_include ens5 \
                 --oversubscribe \
                 --bind-to none \
                 $HOME/nccl-tests/build/all_reduce_perf \
                 -b 8 -e 4G -f 2 -g 1 -c0


echo "Running without EFA"

mpirun -x FI_PROVIDER="ena" \
                --prefix /opt/amazon/openmpi \
                 -x LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/amazon/efa/lib:/opt/amazon/openmpi/lib:$HOME/nccl/build/lib:$HOME/aws-ofi-nccl/install/lib \
                 -x NCCL_DEBUG=INFO \
                 -x NCCL_TREE_THRESHOLD=0 \
                 --hostfile $HOME/hosts \
                 --oversubscribe \
                 --bind-to none \
                 $HOME/nccl-tests/build/all_reduce_perf \
                 -b 8 -e 4G -f 2 -g 1 -c0