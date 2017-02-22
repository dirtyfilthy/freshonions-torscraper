#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
. $ETCDIR/deploy.cfg

# get version

echo "Updating schema.sql..."
ssh $FRONTEND_USER@$FRONTEND_HOST "cd $TOP_DIR/scripts/ && ./update_schema.sh"
scp $FRONTEND_USER@$FRONTEND_HOST:$TOP_DIR/schema.sql $BASEDIR/schema.sql



