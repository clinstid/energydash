#!/bin/bash
PACKAGE_LIST_FILE=requirements.txt
pip freeze > $PACKAGE_LIST_FILE
