#!/bin/sh
BASEDIR=$DIR/..
BASEDIR=$( cd "$BASEDIR" ; pwd -P )
export BASEDIR
export SCRIPTDIR=$BASEDIR/scripts
export ETCDIR=$BASEDIR/etc
export VARDIR=$BASEDIR/var
export PYTHONPATH=$PYTHONPATH:$BASEDIR/lib

. $ETCDIR/proxy
export HIDDEN_SERVICE_PROXY_HOST
export HIDDEN_SERVICE_PROXY_PORT

. $ETCDIR/database
export DB_HOST
export DB_USER
export DB_PASS
export DB_BASE

. $ETCDIR/elasticsearch
export ELASTICSEARCH_ENABLED
export ELASTICSEARCH_HOST
export ELASTICSEARCH_TIMEOUT

. $ETCDIR/limits
export RESULT_LIMIT
export MAX_RESULT_LIMIT

. $ETCDIR/site
export SITE_PATH
export SITE_DOMAIN

. $ETCDIR/private/flask.secret
export FLASK_SECRET
