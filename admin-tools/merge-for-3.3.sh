#/bin/bash
# Setup for running Python 3.3 .. 3.5, merging Python 3.6-to-3.10 into this branch
xdis_33_owd=$(pwd)
cd $(dirname ${BASH_SOURCE[0]})
(cd .. && PYTHON_VERSION=3.3 && pyenv local $PYTHON_VERSION)
if . ./setup-python-3.3.sh; then
    git merge python-3.6-to-3.10
fi
cd $xdis_33_owd
