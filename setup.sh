#!/bin/bash
ENV_DIR=.env

if [ ! -d $ENV_DIR ]; then
    echo Creating virtualenv for project.
    virtualenv $ENV_DIR 
    if [ $? != 0 ]; then
        echo Missing virtualenv.
        exit -1
    fi
    echo Done.
fi

PACKAGE_LIST_FILE=requirements.txt
if [ -f  $PACKAGE_LIST_FILE ]; then
    echo Installing required python modules.
    source $ENV_DIR/bin/activate && pip install -r $PACKAGE_LIST_FILE
    echo Done.
else
    echo Missing package list file $PACKAGE_LIST_FILE.
fi
