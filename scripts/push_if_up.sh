#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
if $DIR/checkurl.sh http://$1/; then
$DIR/push.sh http://$1/
fi
