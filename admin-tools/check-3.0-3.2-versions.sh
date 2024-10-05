#!/bin/bash
# FIXME put some of the below in a common routine
check_xdis_30_owd=$(pwd)

cd $(dirname ${BASH_SOURCE[0]})
if ! source ./pyenv-3.0-3.2-versions ; then
    exit $?
fi
if ! source ./setup-python-3.0.sh ; then
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
cd $check_xdis_30_owd
