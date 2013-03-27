#!/bin/bash
PACKAGE_LIST_FILE=virtualenv_package_list.txt
if [ -f  $PACKAGE_LIST_FILE ]; then
    source env/bin/activate && pip install -r virtualenv_package_list.txt
else
    echo Missing package list file $PACKAGE_LIST_FILE.
fi
