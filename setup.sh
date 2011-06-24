#!/bin/bash

cd -P ./
CURRENT_DIR=`pwd`
python ../../web2py.py --shell=$1 --run=$CURRENT_DIR/scripts/setup.py --import_models