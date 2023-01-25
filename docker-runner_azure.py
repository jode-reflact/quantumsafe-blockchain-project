from typing import List
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.containerinstance.models import (ContainerGroup,
                                                 Container,
                                                 ContainerGroupNetworkProtocol,
                                                 ContainerGroupRestartPolicy,
                                                 ImageRegistryCredential,
                                                 ContainerPort,
                                                 EnvironmentVariable,
                                                 IpAddress,
                                                 Port,
                                                 ResourceRequests,
                                                 ResourceRequirements,
                                                 OperatingSystemTypes)
import requests
import time
import random
import os
from subprocess import call, run, PIPE
import json
from time import sleep

def createContainerViaCLI(container_name,image, location, resource_group_name="quantumsafe_blockchain" ):
    call(["az", "container", "create", "--resource-group", resource_group_name, "--name", container_name, "--image", image, "--dns-name-label", container_name, "--port", "80", "--registry-login-server", os.environ['RG_SERVER'], "--registry-username", os.environ['RG_USR'], "--registry-password", os.environ['RG_PWD'], "--no-wait", "--location", location])
def listContainers(resource_group_name="quantumsafe_blockchain")-> List[ContainerGroup]:
    output = run(["az", "container", "list", "--resource-group", resource_group_name], stdout=PIPE).stdout
    l = json.loads(output)
    return l
"""
aciclient = ContainerInstanceManagementClient(
        credential=DefaultAzureCredential(),
        subscription_id=os.environ["SUBSCRIPTION_ID"],
    )
resclient = ResourceManagementClient(
        credential=DefaultAzureCredential(),
        subscription_id=os.environ["SUBSCRIPTION_ID"],
    )

def create_container_group(aci_client, resource_group,
                           container_group_name, container_image_name):
    print("Creating container group '{0}'...".format(container_group_name))

    # Configure the container
    container_resource_requests = ResourceRequests(memory_in_gb=1, cpu=1.0)
    container_resource_requirements = ResourceRequirements(
        requests=container_resource_requests)
    container = Container(name=container_group_name,
                          image=container_image_name,
                          
                          resources=container_resource_requirements,
                          ports=[ContainerPort(port=80)])

    # Configure the container group
    ports = [Port(protocol=ContainerGroupNetworkProtocol.tcp, port=80)]
    group_ip_address = IpAddress(ports=ports,
                                 dns_name_label=container_group_name,
                                 type="Public")
    image_registry_credentials = ImageRegistryCredential(
        server=os.environ['RG_SERVER'],
        username=os.environ['RG_USR'],
        password=os.environ['RG_PWD'],
    )
    group = ContainerGroup(location=resource_group.location,
                           containers=[container],
                           os_type=OperatingSystemTypes.linux,
                           ip_address=group_ip_address,
                           restart_policy="Never",
                           image_registry_credentials=image_registry_credentials
                           )

    # Create the container group
    aci_client.container_groups.begin_create_or_update(resource_group.name,
                                                 container_group_name,
                                                 group)

    # Get the created container group
    container_group = aci_client.container_groups.get(resource_group.name,
                                                      container_group_name)

    print("Once DNS has propagated, container group '{0}' will be reachable at"
          " http://{1}".format(container_group_name, container_group.ip_address.fqdn))

resource_group_name = 'quantumsafe_blockchain'
container_group_name = 'my-name'
container_image_app = "quantumsafeblockchain.azurecr.io/blockchain-server:v2"
resource_group = resclient.resource_groups.get(resource_group_name)
create_container_group(aciclient, resource_group, container_group_name,
                           container_image_app)
quit()
"""
#client = docker.from_env()

NUMBER_OF_NODES = 10
NUMBER_OF_CLIENTS = 2

NUMBER_OF_TRANSACTIONS = 50

IMAGE_NODE = "quantumsafeblockchain.azurecr.io/blockchain-server:v6"
IMAGE_CLIENT = "quantumsafeblockchain.azurecr.io/blockchain-client:v3"

LOCATIONS= ["westeurope", "germanywestcentral", "francecentral", "swedencentral", "northeurope", "switzerlandwest"]
LOCATION_USED = 0

FQDN_END = '.azurecontainer.io'

DONT_CREATE = False 


FQDN_NODES = {}
FQDN_CLIENTS = {}

WALLET_CLIENTS = {}

def getDomainFromContainer(container):
    return container['fqdn']

# make sure all nodes are fresh / running / up to date
for node_i in range(NUMBER_OF_NODES):
    node_index = node_i + 1
    node_name = 'chainnode-' + node_index.__str__()
    location = LOCATIONS[LOCATION_USED // 6]
    """
    containerList = listContainers()
    if len(containerList) > 0:
        container = containerList[0]
        print("x",container)
        break
        if len(container.image.tags) > 0 and container.image.tags[0] == IMAGE_NODE:
            container.restart()
            IP_NODES[node_name] = {'ip': getIPFromContainer(container), 'port': node_port}
            continue
        else:
            container.remove(force=True)
    """
    if DONT_CREATE != True:
        createContainerViaCLI(node_name, IMAGE_NODE, location)
    node_fqdn = node_name + "." + location + FQDN_END
    #client.containers.run(image=IMAGE_NODE, detach=True, name=node_name, ports={'80/tcp': node_port})
    #container = client.containers.get(node_name)
    FQDN_NODES[node_name] = node_fqdn
    LOCATION_USED = LOCATION_USED + 1
print("FQDN_NODES", FQDN_NODES)

# make sure all clients are fresh / running / up to date
for client_i in range(NUMBER_OF_CLIENTS):
    client_index = client_i + 1
    client_name = 'chainclient-' + client_index.__str__()
    location = LOCATIONS[LOCATION_USED // 6]
    """
    listFilter = {"name": client_name}
    containerList = client.containers.list(filters=listFilter,all=True)
    if len(containerList) > 0:
        container = containerList[0]
        if len(container.image.tags) > 0 and container.image.tags[0] == IMAGE_CLIENT:
            container.restart()
            time.sleep(1)
            IP_CLIENTS[client_name] = {'ip' :getIPFromContainer(container), 'port': client_port}
            continue
        else:
            container.remove(force=True)
    """
    if DONT_CREATE != True:
        createContainerViaCLI(client_name, IMAGE_CLIENT, location)
    client_fqdn = client_name + "." + location + FQDN_END
    FQDN_CLIENTS[client_name] = client_fqdn
    LOCATION_USED = LOCATION_USED + 1
print("FQDN_CLIENTS", FQDN_CLIENTS)
if DONT_CREATE != True:
    sleep(60 * 2)
"""
# remove all clients and nodes above the node / client count
all_container = client.containers.list()
for container in all_container:
    container_name = container.name
    split = container_name.split("-")
    index = int(split[-1])
    if "node-" in container_name:
        # is node container
        if index > NUMBER_OF_NODES:
            container.remove(force=True)
    if "client-" in container_name:
        # is client container
        if index > NUMBER_OF_CLIENTS:
            container.remove(force=True)

#remove unused images called none
images = client.images.list(filters={"dangling": True})
for image in images:
    image.remove(force=True)
"""

def getFQDNSOtherNodes(node_name):
    nodes = FQDN_NODES.copy()
    nodes.pop(node_name)
    return nodes.values()

if DONT_CREATE != True:
    # connect nodes to each other
    for name, fqdn in FQDN_NODES.items():
        url = 'http://'+fqdn+'/nodes/register'
        fqdns = getFQDNSOtherNodes(name)
        form_data = {'nodes': ','.join(fqdns)}
        response = requests.post(url, data=form_data)
        print(name,response) #201 == gut

if (NUMBER_OF_CLIENTS == 0):
    print("Abort, no clients")
    quit()

# create client wallets
for name, fqdn in FQDN_CLIENTS.items():
    url = 'http://'+fqdn+'/wallet/new'
    response = requests.get(url)
    print(name,response) # 200 == gut
    WALLET_CLIENTS[name] = response.json()

def sendTransaction(nodeName: str, senderClientName: str,  receiverClientName: str, amount: int):
    node_fqdn = FQDN_NODES[nodeName]
    client_fqdn = FQDN_CLIENTS[senderClientName]
    client_wallet = WALLET_CLIENTS[senderClientName]
    receiver_wallet = WALLET_CLIENTS[receiverClientName]

    url = 'http://'+client_fqdn+'/generate/transaction'
    form_data = {}
    form_data['sender_address'] = client_wallet['public_key']
    form_data['sender_private_key'] = client_wallet['private_key']
    form_data['receiver_address'] = receiver_wallet['public_key']
    form_data['amount'] = amount
    response = requests.post(url, data=form_data)
    jsonBody = response.json()
    #print("generate transaction",response) # 200 == gut

    #adding signature
    body_node = {}
    body_node['signature'] = jsonBody['signature']
    body_node['timestamp'] = jsonBody['transaction']['timestamp']
    body_node["sender"] = form_data['sender_address']
    body_node["receiver"] = form_data['receiver_address']
    body_node["amount"] = amount
    url_node = 'http://'+node_fqdn+'/transactions'
    response_node = requests.post(url_node, json=body_node)
    print("send transaction to node",response_node) # 201 == gut

# make a test transaction -> remove later
#sendTransaction('chainnode-1', 'chainclient-1', 'chainclient-2', 100)

# some more transactions
for i in range(NUMBER_OF_TRANSACTIONS):
    random_node = random.choice(list(FQDN_NODES.keys()))
    clients = FQDN_CLIENTS.copy()
    random_sender = random.choice(list(clients.keys()))
    clients.pop(random_sender)
    random_receiver = random.choice(list(clients.keys()))
    amount = random.randint(1, 1000)
    print("Random Transaction",i, random_node, random_sender, random_receiver, amount)
    sendTransaction(random_node, random_sender, random_receiver, amount)

quit()

# mine some blocks
time_needed_seconds = 0.0
for i in range(NUMBER_OF_MINED_BLOCKS):
    #random_node = random.choice(list(IP_NODES.keys()))
    #node_ip = IP_NODES[random_node]['ip']
    #node_port = IP_NODES[random_node]['port']
    node_port = 2001
    url_node = 'http://localhost:'+node_port.__str__()+'/mine'
    start_time = time.time()
    response_node = requests.get(url_node)
    time_needed_seconds += time.time() - start_time
    print("Time needed for block", i, time.time() - start_time)
print("Average", time_needed_seconds / NUMBER_OF_MINED_BLOCKS)
# mine genesis block on a random node (node transmits new block to all nodes --> mine battle begins)

# run speed_test with random nodes and random transactions