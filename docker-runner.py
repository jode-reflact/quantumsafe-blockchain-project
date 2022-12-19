import docker
import requests
import time
client = docker.from_env()

NUMBER_OF_NODES = 5
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

# make sure all nodes are fresh / running / up to date
for node_i in range(NUMBER_OF_NODES):
    node_index = node_i + 1
    node_name = 'node-' + node_index.__str__()
    node_port = STANDARD_PORT_NODE + node_index
    listFilter = {"name": node_name}
    containerList = client.containers.list(filters=listFilter,all=True)
    if len(containerList) > 0:
        container = containerList[0]
        if container.image.tags[0] == IMAGE_NODE:
            container.restart()
            IP_NODES[node_name] = {'ip': getIPFromContainer(container), 'port': node_port}
            continue
        else:
            container.remove()
    client.containers.run(image=IMAGE_NODE, detach=True, name=node_name, ports={'80/tcp': node_port})
    container = client.containers.get(node_name)
    IP_NODES[node_name] = {'ip': getIPFromContainer(container), 'port': node_port}
print("IP_NODES", IP_NODES)

# make sure all clients are fresh / running / up to date
for client_i in range(NUMBER_OF_CLIENTS):
    client_index = client_i + 1
    client_name = 'client-' + client_index.__str__()
    client_port = STANDARD_PORT_CLIENT + client_index
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
    client.containers.run(image=IMAGE_CLIENT, detach=True, name=client_name, ports={'80/tcp': client_port})
    time.sleep(1)
    container = client.containers.get(client_name)
    IP_CLIENTS[client_name] = {'ip' :getIPFromContainer(container), 'port': client_port}
print("IP_CLIENTS", IP_CLIENTS)

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
    url = 'http://localhost:'+port.__str__()+'/nodes/register'
    ips = getIPOfOtherNodes('node-1')
    form_data = {'nodes': ','.join(ips)}
    response = requests.post(url, data=form_data)
    print(name,response) #201 == gut

# create client wallets
for name, value in IP_CLIENTS.items():
    ip: str = value['ip']
    port: int = value['port']
    url = 'http://localhost:'+port.__str__()+'/wallet/new'
    print("port", port)
    print("url", url)
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
    print("generate transaction",response) # 200 == gut

    #delete private key before sending to node
    form_data.pop('sender_private_key', None)
    #adding signature
    form_data['signature'] = jsonBody['signature']

    url_node = 'http://localhost:'+node_port.__str__()+'/transactions/new'
    response_node = requests.post(url_node, data=form_data)
    print("send transaction to node",response_node) # 201 == gut

# make a test transaction -> remove later
sendTransaction('node-1', 'client-1', 'client-2', 100)
# mine genesis block on a random node (node transmits new block to all nodes --> mine battle begins)

# run speed_test with random nodes and random transactions