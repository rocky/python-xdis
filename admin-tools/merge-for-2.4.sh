#/bin/bash
# Setup for running Python 2.4 .. 2.7, merging python-3.0-to-3.2 into this branch
xdis_24_owd=$(pwd)
cd $(dirname ${BASH_SOURCE[0]})
(cd .. && PYTHON_VERSION=2.4 && pyenv local $PYTHON_VERSION)
if . ./setup-python-2.4.sh; then
    git merge python-3.0-to-3.2
fi
cd $xdis_24_owd
