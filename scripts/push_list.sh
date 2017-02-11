#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
(
cd $BASEDIR
scrapy crawl tor -a load_links=$1 -a test=yes
)
