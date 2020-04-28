import yaml
import boto3
import os


def get_dlamis(region, ami_type="Ubuntu"):

    assert ami_type in ['Ubuntu', 'Amazon Linux']


    session = boto3.session.Session(region_name=region)
    ec2_client = session.client("ec2")

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_images
    response = ec2_client.describe_images(
            ExecutableUsers=[
                'all',
            ],
            Filters=[
                {
                    'Name': 'name',
                    'Values': [
                        f'Deep Learning AMI ({ami_type}) Version *',
                    ]
                },

            ],
            Owners=[
                'amazon',  # 'self' to get AMIs created by you
            ]
    )


    images = []
    for image in response['Images']:
        name = image['Name']
        description = image['Description']
        image_id = image['ImageId']
        snapshot_id = image['BlockDeviceMappings'][0]['Ebs']['SnapshotId']
        version = float(name.split('Version')[1].strip())

        images.append({
            'Name': name,
            'Version': version,
            'Description': description,
            'ImageId': image_id,
            'SnapshotId': snapshot_id
        })


    return sorted(images, key = lambda i: i['Version'], reverse=True)





def get_my_amis(region):

    session = boto3.session.Session(region_name=region)
    ec2_client = session.client("ec2")

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_images
    response = ec2_client.describe_images(Owners=['self'])

    images = []
    for image in response['Images']:
        name = image['Name']
        if 'Description' in image.keys():
            description = image['Description']
        else:
            description = "No description available"
        image_id = image['ImageId']
        snapshot_id = image['BlockDeviceMappings'][0]['Ebs']['SnapshotId']

        images.append({
            'Name': name,
            'Description': description,
            'ImageId': image_id,
            'SnapshotId': snapshot_id
        })

    return sorted(images, key = lambda i: i['Name'])


def get_config_params():
    path_to_containing_dir = os.path.dirname(os.path.realpath(__file__))
    param_list_yaml_abspath = os.path.join(path_to_containing_dir, "clusterdef_params.yaml")
    config_param_list = yaml.safe_load(open(param_list_yaml_abspath, 'r'))["params"]
    return config_param_list

def setup_container_communication(sh):
    sh.run_on_all('mkdir ssh_container')
    sh.run_on_all('cp hosts ssh_container/')
    sh.run_on_master('ssh-keygen -t rsa -N "" -f ${HOME}/ssh_container/id_rsa')
    sh.run_on_all('printf "Host *\n\tForwardAgent yes\n\tStrictHostKeyChecking no\n" >> ${HOME}/ssh_container/config')
    sh.run_on_all('printf "\tUserKnownHostsFile=/dev/null\n" >> ${HOME}/ssh_container/config')
    sh.run_on_all('printf "\tLogLevel=ERROR\n\tServerAliveInterval=30\n" >> ${HOME}/ssh_container/config')
    sh.run_on_all('printf "\tUser ubuntu\n" >> ${HOME}/ssh_container/config')
    private_key = sh.run_on_master("cat $HOME/ssh_container/id_rsa")
    public_key = sh.run_on_master("cat $HOME/ssh_container/id_rsa.pub")
    sh.run_on_all('printf "{0}" >> $HOME/ssh_container/authorized_keys'.format(public_key.stdout))
    sh.run_on_workers('echo "{0}" >> $HOME/ssh_container/id_rsa'.format(private_key.stdout))
    sh.run_on_all('chmod 600 $HOME/.ssh/id_rsa')
    sh.run_on_all('sudo chown root:root ${HOME}/ssh_container/config')
    sh.run_on_all('printf "#!/bin/bash\n" >> $HOME/.ssh/mpicont.sh')
    sh.run_on_all('printf "echo \\"entering container\\"\n" >> $HOME/.ssh/mpicont.sh')
    sh.run_on_all('printf "docker exec mpicont /bin/bash -c \\"\\$SSH_ORIGINAL_COMMAND\\"\n" >> $HOME/.ssh/mpicont.sh')
    sh.run_on_all('chmod +x $HOME/.ssh/mpicont.sh')
    sh.run_on_all('printf "command=\\"bash $HOME/.ssh/mpicont.sh\\"" >> $HOME/.ssh/authorized_keys')
    sh.run_on_all('printf ",no-port-forwarding,no-agent-forwarding,no-X11-forwarding " >> $HOME/.ssh/authorized_keys')
    sh.run_on_all('printf "{0}\n" >> $HOME/.ssh/authorized_keys'.format(public_key.stdout))


def setup_node_communication(sh, cluster):
    """
    Sets up ssh communication between all nodes in a cluster
    :param cluster: an ec2 cluster object
    :return:
    """
    create_hostfile(sh, cluster)
    create_ssh_comm(sh)
    return

def create_ssh_comm(sh):
    sh.run_on_master('ssh-keygen -t rsa -N "" -f ${HOME}/.ssh/id_rsa')
    sh.run_on_all('printf "Host *\n\tForwardAgent yes\n\tStrictHostKeyChecking no\n" >> ${HOME}/.ssh/config')
    sh.run_on_all('printf "\tUserKnownHostsFile=/dev/null\n" >> ${HOME}/.ssh/config')
    sh.run_on_all('printf "\tLogLevel=ERROR\n\tServerAliveInterval=30\n" >> ${HOME}/.ssh/config')
    sh.run_on_all('printf "\tUser ubuntu\n" >> ${HOME}/.ssh/config')
    private_key = sh.run_on_master("cat $HOME/.ssh/id_rsa")
    public_key = sh.run_on_master("cat $HOME/.ssh/id_rsa.pub")
    sh.run_on_all('printf "{0}" >> $HOME/.ssh/authorized_keys'.format(public_key.stdout))
    sh.run_on_workers('echo "{0}" >> $HOME/.ssh/id_rsa'.format(private_key.stdout))
    sh.run_on_all('chmod 600 $HOME/.ssh/id_rsa')
    return

def create_hostfile(sh, cluster, outfile='hosts'):
    gpu_counts = get_gpu_counts(sh)
    slots = {ip: count for ip, count in zip(cluster.private_ips, gpu_counts)}
    hosts = ''
    for i, j in slots.items():
        hosts += "{0}\tslots={1}\n".format(i, j)
    sh.run_on_all("printf \"{0}\" >> {1}".format(hosts, outfile))
    return

def get_gpu_counts(sh):
    counts = sh.run_on_all('nvidia-smi --query-gpu=gpu_name --format=csv | wc -l')
    counts = [int(count.stdout)-1 for count in counts]
    return counts



