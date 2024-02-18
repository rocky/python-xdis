#/bin/bash
# Setup for running Python 3.6 .. 3.10, merging master into this branch
cd $(dirname ${BASH_SOURCE[0]})
if . ./setup-python-3.6.sh; then
    git merge master
fi
