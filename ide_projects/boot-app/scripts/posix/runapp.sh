#!/bin/bash

#set -x

export FORCE_PYTHON=1

SCRIPT_LOCATION=$0
# Step through symlinks to find where the script really is
while [ -L "$SCRIPT_LOCATION" ]; do
  SCRIPT_LOCATION=`readlink -e "$SCRIPT_LOCATION"`
done

if [ -f "$SCRIPT_LOCATION" ]; then
  SCRIPT_LOCATION=`dirname "$SCRIPT_LOCATION"`
fi

EXEC_PATH=""
EXEC=""

if [ -n "$FORCE_PYTHON" ]; then
  
  EXEC_PATH="$SCRIPT_LOCATION/python/runapp.py"
  EXEC=`which python`
else
  EXEC_PATH="$SCRIPT_LOCATION/bash/runapp.sh"
  EXEC="exec"
fi

eval "$EXEC $EXEC_PATH $@"
