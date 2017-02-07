#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
. $ETCDIR/database
SQL="SELECT COUNT(DISTINCT d1.host, d2.host) FROM domain AS d1 LEFT JOIN page AS p1 ON p1.domain=d1.id LEFT JOIN page_link AS pl ON pl.link_from=p1.id LEFT JOIN page AS p2 ON pl.link_to=p2.id LEFT JOIN domain AS d2 ON d2.id=p2.domain WHERE d1.id IS NOT NULL AND d2.id IS NOT NULL"
echo $SQL | mysql -u $DB_USER  -h $DB_HOST --password=$DB_PASS $DB_BASE
