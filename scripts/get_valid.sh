#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
LIST=`mktemp`
$SCRIPTDIR/extract_from_url.sh https://www.reddit.com/r/darknetmarkets/wiki/superlist.json  > $LIST
echo "VALID LIST:"
cat $LIST
$SCRIPTDIR/make_genuine.py $LIST
rm $LIST
