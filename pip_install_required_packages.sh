#!/bin/bash
ENV_DIR=.env

if [ ! -d $ENV_DIR ]; then
    virtualenv $ENV_DIR
fi

PACKAGE_LIST_FILE=requirements.txt
if [ -f  $PACKAGE_LIST_FILE ]; then
    source $ENV_DIR/bin/activate && pip install -r $PACKAGE_LIST_FILE
else
    echo Missing package list file $PACKAGE_LIST_FILE.
fi
