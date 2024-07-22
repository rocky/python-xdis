#!/bin/bash
if [[ $0 == $${BASH_SOURCE[0]} ]] ; then
    echo "This script should be *sourced* rather than run directly through bash"
    exit 1
fi

PYTHON_VERSION=3.6
pyenv local $PYTHON_VERSION

git checkout python-3.6-to-3.10 && git pull && pyenv local $PYTHON_VERSION
