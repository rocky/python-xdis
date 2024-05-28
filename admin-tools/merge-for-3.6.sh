#/bin/bash
# Setup for running Python 3.6 .. 3.10, merging master into this branch
xdis_36_owd=$(pwd)
cd $(dirname ${BASH_SOURCE[0]})
(cd .. && PYTHON_VERSION=3.6 && pyenv local $PYTHON_VERSION)
if . ./setup-python-3.6.sh; then
    git merge master
fi
cd $xdis_36_owd
