#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
python $SCRIPTDIR/create_flask_secret.py
