# ec2-cluster


Simple CLI and Python library to spin up and run shell commands on clusters of EC2 instances using [`boto3`](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) and [`fabric`](https://github.com/fabric/fabric). Multi-purpose, but created to make deep learning distributed training infrastructure easier. Also very useful for running performance tests across multiple EC2 instance types.

```
import ec2_cluster as ec3

cluster = ec3.ConfigCluster("cluster.yaml")
cluster.launch()

sh = ec3.ClusterShell.from_ec2_cluster(cluster, ssh_key_path="~/.ssh/ec2-cluster-test.pem")
results = sh.run_on_all("hostname")

hostnames = [result.stdout for result in results]
```

## Overview


`ec2-cluster` is designed for simple distributed tasks where Kubernetes is overkill. There is no setup required other than the ability to launch EC2 instances with `boto3` and the ability to SSH to those instances (if you want to run commands on them). 

`ec2-cluster` provides the ability to launch a cluster, to retrieve IP addresses for all nodes/nodes in the cluster, to delete the cluster and to execute commands on some or all of the instances. 

Unlike like most cluster management tools, all cluster management in `ec2-cluster` happens client-side. `ec2-cluster` creates EC2 instances and gives them globally unique names (using the EC2 Name tag) which is later used to identify which instances are part of a given cluster. `ec2-cluster` then provides convenience classes to run commands on some or all of the instances via SSH (using the [`fabric`](https://github.com/fabric/fabric) library).

## Other benefits

- Resilient to EC2 capacity limits. If instances are not available, `ec2-cluster` will retry until the all nodes in the cluster are created or until the user-set timeout is reached.
- Easy to quickly launch duplicate clusters for parallel training runs.
- Can write orchestration logic that needs to be run when launching a cluster, e.g. enabling passwordless ssh between all instances for Horovod-based training
- Iterative, not disruptive, improvements on the common methodology of manually launching EC2 instances, ssh-ing to them, configuring environments by hand and running scripts






### Usage

`ec2-cluster` can be consumed in two ways:

- A CLI for launching, describing and deleting clusters. 
- A python library for scripting.  

This library has three main components:L
- **infra**: creating cluster infrastructure
- **orch**: orchestrating simple runtime cluster configuration (e.g. generate a hostfile with runtime IPs)
- **control**: running commands on the cluster

### CLI Quick Start

### Library Quick Start





