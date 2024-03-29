import uuid
import docker
import requests
import time
import random
import sys

client = docker.from_env()

_, CIPHER, NUMBER_OF_TRANSACTIONS, USE_CACHE, BLOCK_SIZE = sys.argv
NUMBER_OF_TRANSACTIONS = int(NUMBER_OF_TRANSACTIONS)
BLOCK_SIZE = int(BLOCK_SIZE)
USE_CACHE = (USE_CACHE == 'true') | (USE_CACHE == 'True')
#CIPHER = "dilithium"

#NUMBER_OF_TRANSACTIONS = 1000

NUMBER_OF_NODES = 10
NUMBER_OF_CLIENTS = 2

STANDARD_PORT_NODE = 2000
STANDARD_PORT_CLIENT = 3000

IMAGE_NODE = 'blockchain-server:latest'
IMAGE_CLIENT = 'blockchain-client:latest'

IP_NODES = {}
IP_CLIENTS = {}

WALLET_CLIENTS = {}

def getIPFromContainer(container):
    return container.attrs['NetworkSettings']['Networks']['bridge']['IPAddress']

if CIPHER == "ecc":
    CIPHER_TYPE = "P-256"
elif CIPHER == "rsa":
    CIPHER_TYPE = "3072"
elif CIPHER == "dilithium":
    CIPHER_TYPE = "Dilithium3"

container_env = {
    "CIPHER":CIPHER,
    "CIPHER_TYPE": CIPHER_TYPE,
    "TEST_ID": str(uuid.uuid4()).replace("-", ""),
    "TEST_TRANSACTION_COUNT": NUMBER_OF_TRANSACTIONS,
    "TEST_DATE": time.strftime('%d-%m-%Y %H:%M:%S'),
    "TEST_NODE_COUNT": NUMBER_OF_NODES,
    "TEST_CLIENT_COUNT": NUMBER_OF_CLIENTS,
    "HOST": "116.203.116.29",
    "PYTHONUNBUFFERED": "foobar",
    "USE_CACHE": USE_CACHE,
    "BLOCK_SIZE": BLOCK_SIZE
    }

# remove all clients and nodes
all_container = client.containers.list()
for container in all_container:
    container.remove(force=True)

time.sleep(30)

# make sure all nodes are fresh / running / up to date
for node_i in range(NUMBER_OF_NODES):
    node_index = node_i + 1
    node_name = 'node-' + node_index.__str__()
    node_port = STANDARD_PORT_NODE + node_index
    listFilter = {"name": '^/'+node_name+'$'}
    
    client.containers.run(image=IMAGE_NODE, detach=True, name=node_name, ports={'80/tcp': node_port}, environment=container_env)
    container = client.containers.get(node_name)
    IP_NODES[node_name] = {'ip': getIPFromContainer(container), 'port': node_port}
print("IP_NODES", IP_NODES)

# make sure all clients are fresh / running / up to date
for client_i in range(NUMBER_OF_CLIENTS):
    client_index = client_i + 1
    client_name = 'client-' + client_index.__str__()
    client_port = STANDARD_PORT_CLIENT + client_index
    listFilter = {"name": client_name}
    
    client.containers.run(image=IMAGE_CLIENT, detach=True, name=client_name, ports={'80/tcp': client_port}, environment=container_env)
    time.sleep(1)
    container = client.containers.get(client_name)
    IP_CLIENTS[client_name] = {'ip' :getIPFromContainer(container), 'port': client_port}
print("IP_CLIENTS", IP_CLIENTS)

time.sleep(30)

#remove unused images called none
images = client.images.list(filters={"dangling": True})
for image in images:
    image.remove(force=True)

def getIPOfOtherNodes(node_name):
    nodes = IP_NODES.copy()
    nodes.pop(node_name)
    node_values = nodes.values()
    ips = [node['ip'] for node in node_values]
    return ips

# connect nodes to each other
for name, value in IP_NODES.items():
    ip: str = value['ip']
    port: int = value['port']
    url = 'http://localhost:'+port.__str__()+'/nodes/'
    ips = getIPOfOtherNodes(name)
    data = {'nodes': ips}
    response = requests.post(url, json=data)
    print(name,response) #204 == gut

# create client wallets
for name, value in IP_CLIENTS.items():
    ip: str = value['ip']
    port: int = value['port']
    url = 'http://localhost:'+port.__str__()+'/wallet/new'
    response = requests.get(url)
    print(name,response) # 200 == gut
    WALLET_CLIENTS[name] = response.json()

def sendTransaction(nodeName: str, senderClientName: str,  receiverClientName: str, amount: int):
    node_ip = IP_NODES[nodeName]['ip']
    node_port = IP_NODES[nodeName]['port']
    client_port = IP_CLIENTS[senderClientName]['port']
    client_wallet = WALLET_CLIENTS[senderClientName]
    receiver_wallet = WALLET_CLIENTS[receiverClientName]

    url = 'http://localhost:'+client_port.__str__()+'/generate/transaction'
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
    url_node = 'http://localhost:'+node_port.__str__()+'/transactions'
    response_node = requests.post(url_node, json=body_node)
    print("send transaction to node",response_node) # 201 == gut

# make a test transaction -> remove later
# sendTransaction('node-1', 'client-1', 'client-2', 100)

# some more transactions
for i in range(NUMBER_OF_TRANSACTIONS):
    random_node = random.choice(list(IP_NODES.keys()))
    clients = IP_CLIENTS.copy()
    random_sender = random.choice(list(clients.keys()))
    clients.pop(random_sender)
    random_receiver = random.choice(list(clients.keys()))
    amount = random.randint(1, 1000)
    print("Random Transaction", random_node, random_sender, random_receiver, amount)
    sendTransaction(random_node, random_sender, random_receiver, amount)
