from typing import List
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.containerinstance.models import (ContainerGroup,Container,ContainerGroupNetworkProtocol,ContainerGroupRestartPolicy,ImageRegistryCredential,ContainerPort,EnvironmentVariable,IpAddress,Port,ResourceRequests,ResourceRequirements,OperatingSystemTypes)
import requests
import time
import random
import os
from subprocess import call, run, PIPE
import json
from time import sleep
import re

def createContainerViaCLI(container_name,image, location, resource_group_name="quantumsafe_blockchain" ):
    call(["az", "container", "create", "--resource-group", resource_group_name, "--name", container_name, "--image", image, "--dns-name-label", container_name, "--port", "80", "--registry-login-server", os.environ['RG_SERVER'], "--registry-username", os.environ['RG_USR'], "--registry-password", os.environ['RG_PWD'], "--no-wait", "--location", location])
def listContainers(resource_group_name="quantumsafe_blockchain")-> List[ContainerGroup]:
    output = run(["az", "container", "list", "--resource-group", resource_group_name], stdout=PIPE).stdout
    l = json.loads(output)
    return l
def deleteContainer(container_name, resource_group_name="quantumsafe_blockchain"):
    output = run(["az", "container", "delete", "--resource-group", resource_group_name, "--name", container_name, "--yes"], stdout=PIPE).stdout
    l = json.loads(output)
    return l
#client = docker.from_env()

NUMBER_OF_NODES = 10
NUMBER_OF_CLIENTS = 2

NUMBER_OF_TRANSACTIONS = 0

IMAGE_NODE = "quantumsafeblockchain.azurecr.io/blockchain-server:v7"
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

def deleteAllOldContainers():
    containerList = listContainers()
    if len(containerList) > 0:
        for container in containerList:
            container_name = container["name"]
            print("Container Name", container_name)
            match = re.search("chain(node|client)-", container_name)
            if match != None:
                print("Deletion", container_name)
                deleteContainer(container_name=container_name)
        sleep(60)

deleteAllOldContainers()
# create new nodes
for node_i in range(NUMBER_OF_NODES):
    node_index = node_i + 1
    node_name = 'chainnode-' + node_index.__str__()
    location = LOCATIONS[LOCATION_USED // 6]
    if DONT_CREATE != True:
        createContainerViaCLI(node_name, IMAGE_NODE, location)
    node_fqdn = node_name + "." + location + FQDN_END
    FQDN_NODES[node_name] = node_fqdn
    LOCATION_USED = LOCATION_USED + 1
print("FQDN_NODES", FQDN_NODES)

# create new clients
for client_i in range(NUMBER_OF_CLIENTS):
    client_index = client_i + 1
    client_name = 'chainclient-' + client_index.__str__()
    location = LOCATIONS[LOCATION_USED // 6]
    if DONT_CREATE != True:
        createContainerViaCLI(client_name, IMAGE_CLIENT, location)
    client_fqdn = client_name + "." + location + FQDN_END
    FQDN_CLIENTS[client_name] = client_fqdn
    LOCATION_USED = LOCATION_USED + 1
print("FQDN_CLIENTS", FQDN_CLIENTS)
if DONT_CREATE != True:
    sleep(60 * 5)

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