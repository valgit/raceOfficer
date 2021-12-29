#! /bin/bash

# this is a convenience script that first sources the venv (assumed to be in
# ../venv) and then executes manage.py with whatever arguments you supply the
# script with. this is useful if you need to execute the manage.py from
# somewhere where the venv isn't sourced (e.g. system scripts)

# get the script's location
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# source venv <- UPDATE THE PATH HERE WITH YOUR VENV's PATH
source $DIR/../.ro2venv/bin/activate

# run manage.py script
$DIR/bot.py "$@"
