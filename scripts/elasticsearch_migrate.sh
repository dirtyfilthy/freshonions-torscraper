#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
$SCRIPTDIR/elasticsearch_migrate.py


