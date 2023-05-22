# quantumsafe-blockchain-project

## Build and install OpenQuantumSafe library (liboqs)

### liboqs
This project uses liboqs for quantum-safe algorithms, which needs to be build before.
This can be done following these steps: https://github.com/open-quantum-safe/liboqs#quickstart
### liboqs-python
To use the C library liboqs, a python-wrapper for this lib needs to be installed.
Depending on the OS, the manual can be found here: https://github.com/open-quantum-safe/liboqs-python#installation

## Python blockchain implementation
### Implemented ciphers
Dilithium-3, RSA 3072, ECC P-256
### Setup
1. Install requirements:
    ````
    pip install -r requirements.txt
    ````
2. Start docker service
3. Start test via docker-runny script or through the Node application
    ````
   python docker-runner.py CIPHER N_TRANSACTIONS USE_CACHE_BOOLEAN BLOCK_SIZE
   e.g. python docker-runner.py dilithium 1000 false 9
    ````

### Architecture overview
![The blockchain architecture](architecture-diagram.png)

- 1 container is responsible for hosting a blockchain node, a mining node and a relational database for data sharing. This represents a blockchain container, which is started N times -> resulting in a network of N participants.
- 1 container is responsible for hosting a client node with a private and public key, which creates, signs and sends transactions to one of the blockchain containers.
- The mining node mines concurrently and continuous, while fetching recent transactions from the database
- The blockchain node verifies and adds new blocks (coming from the mining node or other blockchain nodes), as well as propagates them through the network and updates the database properly
- The database has 4 tables, being "Chains", "Blocks", "Confirmed tx", "Pending tx"
    - Chains -> Containing the active blockchain element (For abstraction purpose)
    - Blocks -> Containing the current blocks which are validated and propagated
    - Confirmed Tx -> Containing the verified and added transactions, which are in the current distributed chain
    - Pending Tx -> Containing the verified transactions, which are used by the mining node for finding the next block nonce
- The client node is a simple simulation of an end user, who places transactions which are signed using a public and private key, as well as the addressee's public key
