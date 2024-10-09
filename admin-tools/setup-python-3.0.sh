#!/bin/bash
bs=${BASH_SOURCE[0]}
if [[ $0 == $bs ]] ; then
    echo "This script should be *sourced* rather than run directly through bash"
    exit 1
fi

PYTHON_VERSION=3.0

export PATH=$HOME/.pyenv/bin/pyenv:$PATH
xdis_owd=$(pwd)
mydir=$(dirname $bs)
mydir=$(dirname $bs)
cd $mydir

cd $pytracer_owd
rm -v */.python-version 2>/dev/null || true

git checkout python-3.0-to-3.2  && git pull && pyenv local $PYTHON_VERSION
