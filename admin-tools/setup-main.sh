#!/bin/bash
# Check out main branch and dependent development main branches
if [[ $0 == $${BASH_SOURCE[0]} ]] ; then
    echo "This script should be *sourced* rather than run directly through bash"
    exit 1
fi

PYTHON_VERSION=3.12
pyenv local $PYTHON_VERSION

git checkout main && git pull && pyenv local $PYTHON_VERSION
