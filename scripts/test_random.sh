#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
cd $BASEDIR
RAND_LIST=`mktemp`
$SCRIPTDIR/gen_random.sh $1 > $RAND_LIST
scrapy crawl tor -a test=yes -a load_links=$RAND_LIST -a only_success=yes
rm $RAND_LIST
