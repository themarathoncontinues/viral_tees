#!/bin/bash
source $PWD/.env

rm -rf $PWD/data/
rm -rf $PWD/logs/
rm -f $PWD/static/images/*
mongo --port $MONGO_PORT $MONGO_DATABASE --eval "db.dropDatabase()"