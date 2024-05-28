#!/bin/bash
# Check out master branch and dependent development master branches
if [[ $0 == $${BASH_SOURCE[0]} ]] ; then
    echo "This script should be *sourced* rather than run directly through bash"
    exit 1
fi

PYTHON_VERSION=3.12
pyenv local $PYTHON_VERSION

git checkout master && git pull && pyenv local $PYTHON_VERSION
