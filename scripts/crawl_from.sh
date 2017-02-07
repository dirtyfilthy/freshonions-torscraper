#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
cd $BASEDIR
scrapy crawl tor -a test=no -a passed_url=$1
