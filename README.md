# quantumsafe-blockchain-project
## Python blockchain implementation
### Setup
1. Install requirements:
    ````
    pip install -r requirements.txt
    ````
2. Start blockchain locally
   - First, configure your host and port in config.ini
   - For each system which runs a blockchain, define a different port to ensure they can communicate
       ````
       [HOST]
       host = 127.0.0.1
       port = 5000
       ````
   - Start the blockchain locally
       ````
       python -m blockchain
       ````
3. Start client locally on an unused port (e.g. 3000)
    ````
   python -m client <<port>>
    ````

### Usage
1. In the client frontend, create a wallet
   - You will get a private and public key (ECC Decryption)
   - save them to a private text editor
2. In client frontend, create a new transaction
   - Sender address is your private key
   - Receiver address is the recipient's private key
3. In blockchain frontend, mine a new block
   - The unmined transactions will be inserted into the mined block
   - The miner who serves the current chain will also get a reward from "THE BLOCKCHAIN" via transaction

### Decryption algorithms

- Block Hash
  - Block Dict >>> JSON >>> SHA256 >>> Convert to Hexadecimal
- Transaction
  - Sender/Receiver private and public key
    - ECC (P-256) >>> Convert to hexadecimal
  - Transaction Hash
    - Transaction Dict (like JSON) >>> SHA256 >>> Encode to utf-8
  - Signature
    - Digital Signature Standard (DSS) - fips-186-3 (randomized signature generation)
    - Takes Private Key of sender for signing
    - Transaction Hash >>> DSS Signature generation >> Convert to hexadecimal