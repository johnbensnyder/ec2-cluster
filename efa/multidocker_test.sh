git clone https://github.com/NVIDIA/nccl-tests.git

cd nccl-tests

make MPI=1 MPI_HOME=/usr/local/ NCCL_HOME=/nccl/build


echo "Running with EFA"

mpirun -x FI_PROVIDER="efa" \
                --prefix /usr/local \
                 -x LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/efa/lib:/usr/local/lib:/nccl/build/lib:/aws-ofi-nccl/install/lib \
                 -x NCCL_DEBUG=INFO \
                 -x NCCL_TREE_THRESHOLD=0 \
                 -x NCCL_SOCKET_IFNAME=ens5 \
                 --hostfile /root/.ssh/hosts \
                 --mca oob_tcp_if_include ens5 \
                 --mca btl_tcp_if_include ens5 \
                 --oversubscribe \
                 --bind-to none \
                 /nccl-tests/build/all_reduce_perf \
                 -b 8 -e 4G -f 2 -g 1 -c0


echo "Running without EFA"

mpirun -x FI_PROVIDER="ena" \
                --allow-run-as-root \
                 -x LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/efa/lib:/usr/local/lib:/nccl/build/lib:/aws-ofi-nccl/install/lib \
                 -x NCCL_DEBUG=INFO \
                 -x NCCL_TREE_THRESHOLD=0 \
                 -x NCCL_SOCKET_IFNAME=^docker0,lo \
                 --hostfile /root/.ssh/hosts \
                 --mca plm_rsh_no_tree_spawn 1 -bind-to none -map-by slot -mca pml ob1 \
                 --mca btl_vader_single_copy_mechanism none \
                 --mca btl tcp,self \
                 --mca btl_tcp_if_exclude lo,docker0 \
                 --oversubscribe \
                 /nccl-tests/build/all_reduce_perf \
                 -b 8 -e 4G -f 2 -g 1 -c0

mpirun -x FI_PROVIDER="efa" \
            --allow-run-as-root \
            -x LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/efa/lib:/usr/local/lib:/nccl/build/lib:/aws-ofi-nccl/install/lib \
            -x NCCL_DEBUG=INFO \
             -x NCCL_TREE_THRESHOLD=0 \
             -x NCCL_SOCKET_IFNAME=ens5 \
             --hostfile /root/.ssh/hosts \
             --mca plm_rsh_no_tree_spawn 1 -bind-to none -map-by slot -mca pml ob1 \
             --mca btl_vader_single_copy_mechanism none \
             --mca oob_tcp_if_include ens5 \
             --mca btl_tcp_if_include ens5 \
             --oversubscribe \
             /nccl-tests/build/all_reduce_perf \
                 -b 8 -e 4G -f 2 -g 1 -c0