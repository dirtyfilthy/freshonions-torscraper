#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
$SCRIPTDIR/add_domains_to_elasticsearch.py
