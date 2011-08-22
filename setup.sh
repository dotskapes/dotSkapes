#!/bin/bash

DIR=$(pwd)
WD=${DIR}/${0}
OIFS=$IFS
IFS=/
INDEX=0
for path in ${WD}; do
    if [ "$path" != "." ]; then
	S[$INDEX]=$path
	INDEX=$(($INDEX + 1))
    fi
done
INDEX=$(($INDEX - 2))
IFS=$OIFS

SHELL=${S[$INDEX]}

while [ $INDEX -gt -1 ]; do
    WEB2PY=${S[$INDEX]}/$WEB2PY
    INDEX=$(($INDEX - 1))
    done

python ${WEB2PY}../../web2py.py --shell=$SHELL --run=applications/${SHELL}/scripts/setup.py --import_models

#$cd -P ./
#CURRENT_DIR=`pwd`
#python ../../web2py.py --shell=$1 --run=$CURRENT_DIR/scripts/setup.py --import_models