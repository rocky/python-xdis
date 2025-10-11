#!/bin/bash
# The name Python's import uses.
# It is reflected in the directory structure.
PACKAGE_MODULE="xdis"

# The name that PyPi sees this as.
# It is set in setup.py's name.
PACKAGE_NAME="xdis"

# Both the name an module name agree
PACKAGE=$PACKAGE_NAME

# FIXME put some of the below in a common routine
function finish {
  if [[ -n "$make_dist_xdis_36_owd" ]] then
     cd $make_dist_xdis_36_owd
  fi
  cd $make_dist_xdis_36_owd
}

make_dist_xdis_36_owd=$(pwd)
cd $(dirname ${BASH_SOURCE[0]})
trap finish EXIT

if ! source ./pyenv-3.6-3.10-versions ; then
    exit $?
fi
if ! source ./setup-python-3.6.sh ; then
    exit $?
fi

cd ..
source $PACKAGE/version.py
if [[ ! -n $__version__ ]]; then
    echo "Something is wrong: __version__ should have been set."
    exit 1
fi

for pyversion in $PYVERSIONS; do
    if [[ ${pyversion:0:4} == "pypy" ]] ; then
	echo "$pyversion - PyPy does not get special packaging"
	continue
    fi
    echo "*** Packaging ${PACKAGE_NAME} for version ${__version__} on Python ${pyversion} ***"
    if ! pyenv local $pyversion ; then
	exit $?
    fi
    # pip bdist_egg create too-general wheels. So
    # we narrow that by moving the generated wheel.

    # Pick out first two numbers of version, e.g. 3.5.1 -> 35
    first_two=$(echo $pyversion | cut -d'.' -f 1-2 | sed -e 's/\.//')
    rm -fr build
    pip wheel --wheel-dir=dist .
    mv -v dist/${PACKAGE_MODULE}-$__version__-{py3,py$first_two}-none-any.whl
done

python ./setup.py sdist
tarball=dist/${PACKAGE_NAME}-${__version__}.tar.gz
if [[ -f $tarball ]]; then
    twine check $tarball
fi

if [[ ! -d dist/${__version__} ]] ; then
    mkdir -v dist/${__version__}
fi

twine check dist/${PACKAGE}-${__version__}-py3*.whl
finish
