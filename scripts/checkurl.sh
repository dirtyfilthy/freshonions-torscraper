#!/bin/sh
#if curl --socks5 localhost:9050 --silent $1 &>/dev/null; then
echo "Checking $1"
if curl --connect-timeout 20 --socks5-hostname localhost:9050 -I --silent $1 > /dev/null; then
echo "OK $1"
exit 0
fi;
echo "ERR $1"
exit 1
