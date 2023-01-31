#!/bin/bash
VERSION=v4

docker build --platform=linux/amd64 -t blockchain-client:latest -f Dockerfile.client .
docker tag blockchain-client quantumsafeblockchain.azurecr.io/blockchain-client:${VERSION}
docker push quantumsafeblockchain.azurecr.io/blockchain-client:${VERSION}