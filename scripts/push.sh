#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
cd $BASEDIR
URL=$1
if echo $1 | grep -q -v -E "^http:"; then
	URL=http://$1/
fi;
echo "Pushing $URL"
scrapy crawl tor -a passed_url=$URL -a test=yes
