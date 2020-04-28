import sys
from importlib import reload
import re
sys.path.append('..')
import ec2_cluster
ec2_cluster = reload(ec2_cluster)

################################################################
# Read configuration file
################################################################

cluster = ec2_cluster.infra.ConfigCluster("cluster_config.yaml")

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

sh.copy_from_local_to_all('cuda_setup.sh', 'cuda_setup.sh')

sh.run_on_all('chmod +x cuda_setup.sh && ./cuda_setup.sh')

sh.run_on_all('sudo reboot')

sh = cluster.get_shell(ssh_key_path='~/.aws/jbsnyder.pem')

sh.run_on_all('hostname')

sh.copy_from_local_to_all('ofi_setup.sh', 'ofi_setup.sh')

sh.run_on_all('chmod +x ofi_setup.sh && ./ofi_setup.sh')

sh.run_on_all('cd aws-ofi-nccl && make && make install')

################################################################
# Setup SSH for internode communication
################################################################

ec2_cluster.utils.create_ssh_comm(sh)

################################################################
# Compile NCCL tests
################################################################

sh.copy_from_local_to_all('nccl_test.sh', 'nccl_test.sh')

sh.run_on_all('chmod +x nccl_test.sh && ./nccl_test.sh')

################################################################
# Run multinode MPI NCCL tests
################################################################

sh = cluster.get_shell(ssh_key_path='~/.aws/jbsnyder.pem')

sh.copy_from_local_to_all('multinode_test.sh', 'multinode_test.sh')

sh.run_on_master('chmod +x multinode_test.sh')

perf = sh.run_on_master('./multinode_test.sh')

################################################################
# Print EFA and non EFA performance results
################################################################

bandwidth = [re.findall('\d+\.\d+', i)[0] for i in perf.stdout.split('\n') if "bus bandwidth" in i]

print("EFA bandwith: {0}\nNon EFA bandwidth {1}".format(*bandwidth))

