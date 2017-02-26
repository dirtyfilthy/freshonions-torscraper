#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
. $ETCDIR/deploy.cfg

$SCRIPTDIR/update_and_pull_schema.sh

echo "rsyncing to upstream hosts..."
(
	cd $BASEDIR/..
	rsync -a -i --exclude=.git $TOP_DIR/ $BACKEND_USER@$BACKEND_HOST:$TOP_DIR
)




