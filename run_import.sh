#!/bin/bash

export HANDLER_TYPE="couch"
export COUCH_URL="couchbase://192.168.99.100/default"

python3 py/importer.py $HANDLER_TYPE
