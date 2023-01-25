#!/bin/bash
VERSION=v6

docker build --platform=linux/amd64 -t blockchain-server:latest -f Dockerfile.server .
docker tag blockchain-server quantumsafeblockchain.azurecr.io/blockchain-server:${VERSION}
docker push quantumsafeblockchain.azurecr.io/blockchain-server:${VERSION}