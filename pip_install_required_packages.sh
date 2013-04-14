#!/bin/bash
PACKAGE_LIST_FILE=requirements.txt
if [ -f  $PACKAGE_LIST_FILE ]; then
    source .env/bin/activate && pip install -r $PACKAGE_LIST_FILE
else
    echo Missing package list file $PACKAGE_LIST_FILE.
fi
