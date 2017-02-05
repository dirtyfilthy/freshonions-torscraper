#!/bin/bash
DIR=$( cd "$(dirname "$0")" ; pwd -P )
BASEDIR=$DIR/..
DELEGATED=/home/scraper/delegate9.9.13/src/delegated
base_socks_port=9050
base_http_port=3128 # leave 3128 for HAProxy
base_control_port=8119
# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    mkdir "data"
fi
 
#for i in {0..10}
for i in {1..4}
do
    j=$((i+1))
    socks_port=$((base_socks_port+i))
    control_port=$((base_control_port+i))
    http_port=$((base_http_port+i))
    if [ ! -d "data/tor$i" ]; then
        echo "Creating directory data/tor$i"
        mkdir "data/tor$i"
    fi
    # Take into account that authentication for the control port is disabled. Must be used in secure and controlled environments
 
    echo "Running: tor --RunAsDaemon 1  --PidFile tor$i.pid --SocksPort $socks_port --DataDirectory $BASEDIR/var/tor$1"
 
    tor --RunAsDaemon 1  --PidFile tor$i.pid --SocksPort $socks_port --DataDirectory $BASEDIR/var/tor$i
 
    echo    "Running: ./delegate/src/delegated -P$http_port SERVER=http SOCKS=localhost:$socks_port"
 
    $DELEGATED -P$http_port CONNECT=s SERVER=http SOCKS=localhost:$socks_port RELAY=vhost
done
 
haproxy -f $BASEDIR/etc/rotating-tor-proxies.cfg
