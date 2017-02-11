#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
LIST=`mktemp`
LIST2=`mktemp`
$SCRIPTDIR/extract_from_url.sh $1 > $LIST
$SCRIPTDIR/purify.sh $LIST > $LIST2
NUMBER=`wc -l $LIST2 | tr -s ' ' | cut -f 1 -d ' '`
echo "Harvested $NUMBER onion links..."
(
cd $BASEDIR
scrapy crawl tor -a load_links=$LIST2 -a test=yes
)
rm $LIST $LIST2

