#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
TEMP1=`mktemp`
TEMP2=`mktemp`
cat $1 | grep -E -o '[0-9a-zA_Z]+\.onion' | sort | uniq | sort -R > $TEMP1
$SCRIPTDIR/dont_have.sh $TEMP1 > $TEMP2
cat $TEMP2
rm $TEMP1 $TEMP2
