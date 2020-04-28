

docker run --rm -it --gpus all \
    --name mpicont \
    --net=host --uts=host --ipc=host \
    --ulimit stack=67108864 --ulimit memlock=-1 \
    --security-opt seccomp=unconfined \
    -v /opt/amazon/efa:/efa \
    --device=/dev/infiniband/uverbs0 \
    johnbensnyder/efa:base /bin/bash

git clone https://github.com/NVIDIA/nccl-tests.git

make MPI=1 MPI_HOME=/usr/local NCCL_HOME=/nccl/build

mpirun --allow-run-as-root \
       -x FI_PROVIDER="efa" \
       -x LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/efa/lib:/usr/local/lib:/nccl/build/lib:/aws-ofi-nccl/install/lib \
       -x NCCL_DEBUG=INFO -H 127.0.0.1:8 \
       /nccl-tests/build/all_reduce_perf -b 8 -e 1G -f 2 -c0