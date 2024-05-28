#/bin/bash
# Setup for running Python 3.6 .. 3.10, merging master into this branch
xdis_36_owd=$(pwd)
PYTHON_VERSION=3.6
pyenv local $PYTHON_VERSION
cd $(dirname ${BASH_SOURCE[0]})
if . ./setup-python-3.6.sh; then
    git merge master
fi
cd $xdis_36_owd
