#!/bin/bash

owd=$(pwd)

cd $(dirname ${BASH_SOURCE[0]})
if ! source ./pyenv-3.6-3.10-versions ; then
    exit $?
fi
if ! source ./setup-python-3.6.sh ; then
    exit $?
fi
cd ..
for version in $PYVERSIONS; do
    echo --- $version ---
    if ! pyenv local $version ; then
	exit $?
    fi
    make clean && pip install -e .
    if ! make check; then
	exit $?
    fi
    echo === $version ===
done
cd $owd
