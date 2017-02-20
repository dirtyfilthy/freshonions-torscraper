#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh

mysqldump -d -h $DB_HOST -u $DB_USER --password=$DB_PASS $DB_BASE > $BASEDIR/schema.sql
