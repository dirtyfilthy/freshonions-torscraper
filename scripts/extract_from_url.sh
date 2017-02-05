#!/bin/sh
http_proxy="" https_proxy="" wget --no-check-certificate -O - $1 | grep -E -o '[0-9a-zA_Z]+\.onion' 
