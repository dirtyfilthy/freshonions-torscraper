#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
links2 --http-proxy $TOR_PROXY_HOST:$TOR_PROXY_PORT $1

