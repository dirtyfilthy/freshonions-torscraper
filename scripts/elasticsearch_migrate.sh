#!/bin/sh
DIR=$( cd "$(dirname "$0")" ; pwd -P )
. $DIR/env.sh
read -r -p "Are you sure? This will delete any existing index [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY]) 
        $SCRIPTDIR/elasticsearch_migrate.py
        ;;
    *)
        echo "Fair enough"
        exit(1)
        ;;
esac

