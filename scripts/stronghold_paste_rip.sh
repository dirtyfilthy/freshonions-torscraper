#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
LIST=`mktemp`
LIST2=`mktemp`
TEMP=`mktemp`
wget -r --level=1 --no-check-certificate -O $TEMP http://nzxj65x32vh2fkhk.onion/all
cat $TEMP | grep -E -o '[0-9a-zA_Z]+\.onion' > $LIST
$SCRIPTDIR/purify.sh $LIST > $LIST2
NUMBER=`wc -l $LIST2 | tr -s ' ' | cut -f 1 -d ' '`
echo "Harvested $NUMBER onion links..."
$SCRIPTDIR/push_list.sh $LIST2
rm $LIST $LIST2 $TEMP



