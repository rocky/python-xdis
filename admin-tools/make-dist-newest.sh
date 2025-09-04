#!/bin/bash
PACKAGE=xdis

# FIXME put some of the below in a common routine
function finish {
  if [[ -n "$make_dist_xdis_newest_owd" ]] then
     cd $make_dist_xdis_newest_owd
  fi
}

make_dist_xdis_newest_owd=$(pwd)
cd $(dirname ${BASH_SOURCE[0]})
trap finish EXIT

if ! source ./pyenv-newest-versions ; then
    exit $?
fi
if ! source ./setup-master.sh ; then
    exit $?
fi

cd ..
source $PACKAGE/version.py
echo $__version__

rm -fr build
pip wheel --wheel-dir=dist .
python -m build --sdist
finish
