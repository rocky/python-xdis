#!/bin/bash

check_xdis_33_owd=$(pwd)

cd $(dirname ${BASH_SOURCE[0]})
if ! source ./pyenv-3.3-3.5-versions ; then
    exit $?
fi
if ! source ./setup-python-3.3.sh ; then
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
cd $check_xdis_33_owd
