import sys
from importlib import reload
import re
sys.path.append('ec2-cluster')
import ec2_cluster
ec2_cluster = reload(ec2_cluster)

################################################################
# Read configuration file
################################################################

cluster = ec2_cluster.infra.ConfigCluster("ec2-cluster/efa/cluster_config.yaml")

################################################################
# Launch Cluster
################################################################

cluster.launch(verbose=True)

################################################################
# Create cluster shell
################################################################

sh = cluster.get_shell(ssh_key_path='~/.aws/jbsnyder.pem')
sh.run_on_all('lspci')

################################################################
# Setup CUDA and EFA
################################################################

sh.copy_from_local_to_all('ec2-cluster/efa/cuda_setup.sh', 'cuda_setup.sh')

sh.run_on_all('chmod +x cuda_setup.sh && ./cuda_setup.sh')

sh.run_on_all('sudo reboot')

sh = cluster.get_shell(ssh_key_path='~/.aws/jbsnyder.pem')

sh.run_on_all('hostname')

sh.copy_from_local_to_all('ec2-cluster/efa/ofi_setup.sh', 'ofi_setup.sh')

sh.run_on_all('chmod +x ofi_setup.sh && ./ofi_setup.sh')

sh.run_on_all('export PATH=PATH:/opt/amazon/openmpi/bin/:/usr/bin/:/bin/ && cd aws-ofi-nccl && make && make install')

################################################################
# Setup SSH for internode communication
################################################################

ec2_cluster.utils.setup_node_communication(sh, cluster)

################################################################
# Compile NCCL tests
################################################################

sh.copy_from_local_to_all('ec2-cluster/efa/nccl_test.sh', 'nccl_test.sh')

sh.run_on_all('chmod +x nccl_test.sh && ./nccl_test.sh')

################################################################
# Run multinode MPI NCCL tests
################################################################

sh = cluster.get_shell(ssh_key_path='~/.aws/jbsnyder.pem')

sh.copy_from_local_to_all('ec2-cluster/efa/multinode_test.sh', 'multinode_test.sh')

sh.run_on_master('chmod +x multinode_test.sh')

perf = sh.run_on_master('./multinode_test.sh')

################################################################
# Print EFA and non EFA performance results
################################################################

bandwidth = [re.findall('\d+\.\d+', i)[0] for i in perf.stdout.split('\n') if "bus bandwidth" in i]

print("EFA bandwith: {0}\nNon EFA bandwidth {1}".format(*bandwidth))

################################################################
# setup docker
################################################################

sh = cluster.get_shell(ssh_key_path='~/.aws/jbsnyder.pem')

sh.copy_from_local_to_all('ec2-cluster/efa/docker_setup.sh', 'docker_setup.sh')

sh.run_on_all('chmod +x docker_setup.sh')

sh.run_on_all('./docker_setup.sh')

sh = cluster.get_shell(ssh_key_path='~/.aws/jbsnyder.pem')

sh.run_on_all("docker run --gpus all nvidia/cuda:10.1-base nvidia-smi")

################################################################
# setup container communication
################################################################

ec2_cluster.utils.setup_container_communication(sh)

################################################################
# launch containers
################################################################

worker_cont = """docker run --rm -it --gpus all \
                    --name mpicont \
                    --net=host --uts=host --ipc=host \
                    --ulimit stack=67108864 --ulimit memlock=-1 \
                    --security-opt seccomp=unconfined \
                    -v /opt/amazon/efa:/efa \
                    -v /home/ubuntu/ssh_container:/root/.ssh \
                    --device=/dev/infiniband/uverbs0 \
                    johnbensnyder/efa:base /bin/bash
                    """

master_cont = """docker run --rm -it --gpus all \
                    --name mpicont \
                    --net=host --uts=host --ipc=host \
                    --ulimit stack=67108864 --ulimit memlock=-1 \
                    --security-opt seccomp=unconfined \
                    -v /opt/amazon/efa:/efa \
                    -v /home/ubuntu/ssh_container:/root/.ssh \
                    --device=/dev/infiniband/uverbs0 \
                    johnbensnyder/efa:base /bin/bash
                    """

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
                 --hostfile /root/.ssh/hosts \
                 --oversubscribe \
                 --bind-to none \
                 /nccl-tests/build/all_reduce_perf \
                 -b 8 -e 4G -f 2 -g 1 -c0
