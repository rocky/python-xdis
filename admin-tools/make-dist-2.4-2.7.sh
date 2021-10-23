#!/bin/bash
PACKAGE=xdis

# FIXME put some of the below in a common routine
function finish {
  cd $owd
}
owd=$(pwd)
trap finish EXIT

cd $(dirname ${BASH_SOURCE[0]})
if ! source ./pyenv-2.4-2.7-versions ; then
    exit $?
fi
if ! source ./setup-python-2.4.sh ; then
    exit $?
fi

cd ..
source $PACKAGE/version.py
echo $__version__

for pyversion in $PYVERSIONS; do
    if ! pyenv local $pyversion ; then
	exit $?
    fi

    rm -fr build
    python setup.py bdist_egg
done

python ./setup.py sdist

tarball=dist/${PACKAGE}-${__version__}-tar.gz
if [[ -f $tarball ]]; then
    mv -v $tarball dist/${PACKAGE}_24-${__version__}.tar.gz
fi
