#!/bin/sh
kill `ps aux | grep $1 | tr -s ' ' | cut -f 2 -d ' '`
