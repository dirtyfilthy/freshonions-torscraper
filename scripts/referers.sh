#!/bin/sh
cat /var/log/nginx/access.log | cut -f 4 -d '"' | grep -E -v '^-' | sort | uniq
