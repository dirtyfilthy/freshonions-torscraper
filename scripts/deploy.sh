#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
. $ETCDIR/deploy.cfg

# get version

VERSION=`cat $ETCDIR/version`
echo $VERSION

# get and update revision

REVISION=`cat $ETCDIR/revision`
REVISION=$((REVISION+1))
echo $REVISION > $ETCDIR/revision

DATE=`date +%Y%m%d%H%M`

VERSION_STRING="${VERSION}r${REVISION}-${DATE}"

echo $VERSION_STRING > $ETCDIR/version_string

echo "### Deploying $VERSION_STRING: ###"

$SCRIPTDIR/update_and_pull_schema.sh

echo "Removing old source files.."
(
	cd $BASEDIR/web/static
	rm torscraper*.tar.gz
)

echo "Creating source file..."
# make src file

DIST_TAR="$BASEDIR/web/static/torscraper-$VERSION_STRING.tar.gz"
(
	cd $BASEDIR/..
	tar czf $DIST_TAR --exclude='*.tar.gz' --exclude=private --exclude=etc/private --exclude=./$TOP_DIR/.git ./$TOP_DIR
)

# rsync upstream
echo "rsyncing to upstream hosts..."
(
	cd $BASEDIR/..
	rsync -a -i --exclude=.git --exclude=var --delete-after $TOP_DIR/ $BACKEND_USER@$BACKEND_HOST:$TOP_DIR
	rsync -a -i --exclude=.git --exclude=var --delete-after $TOP_DIR/ $FRONTEND_USER@$FRONTEND_HOST:$TOP_DIR
)
# kick the service
echo "Restarting $SERVICE_NAME frontend service..."

ssh root@$FRONTEND_HOST "service $SERVICE_NAME restart"




