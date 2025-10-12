#!/bin/bash
# Setup for running Python 3.0 .. 3.2, merging 3.3-3.5 into this branch
xdis_30_owd=$(pwd)
PYTHON_VERSION=3.0
pyenv local $PYTHON_VERSION
cd $(dirname ${BASH_SOURCE[0]})
(cd .. && PYTHON_VERSION=3.1 && pyenv local $PYTHON_VERSION)
if . ./setup-python-3.0.sh; then
    git merge python-3.3-to-3.5
fi
cd $xdis_30_owd
