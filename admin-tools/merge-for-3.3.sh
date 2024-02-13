#/bin/bash
# Setup for running Python 3.3 .. 3.5, merging Python 3.6-to-3.10 into this branch
set -e
function finish {
  cd $owd
}
owd=$(pwd)
trap finish EXIT

cd $(dirname ${BASH_SOURCE[0]})
if . ./setup-python-3.3.sh; then
    git merge python-3.6-to-3.10
fi
finish
