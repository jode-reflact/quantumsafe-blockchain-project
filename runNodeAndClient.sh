#!/bin/bash

PORT=$1

exec python -m node $PORT &
exec python -m miner $PORT