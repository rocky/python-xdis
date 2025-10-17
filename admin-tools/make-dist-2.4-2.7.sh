#!/bin/bash
PACKAGE=xdis

# FIXME put some of the below in a common routine
function finish {
  cd $make_dist_24_owd
}
make_dist_24_owd=$(pwd)
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
if [[ ! -n $__version__ ]]; then
    echo "You need to set __version__ first"
    exit 1
fi
echo $__version__

for pyversion in $PYVERSIONS; do
    case ${pyversion:0:4} in
	"graa" )
	    echo "$pyversion - Graal does not get special packaging"
	    continue
	    ;;
	"jyth" )
	    echo "$pyversion - Jython does not get special packaging"
	    continue
	    ;;
	"pypy" )
	    echo "$pyversion - PyPy does not get special packaging"
	    continue
	    ;;
	"pyst" )
	    echo "$pyversion - Pyston does not get special packaging"
	    continue
	    ;;
    esac
    echo "*** Packaging ${PACKAGE_NAME} for version ${__version__} on Python ${pyversion} ***"
    if ! pyenv local $pyversion ; then
	exit $?
    fi

    rm -fr build
    python setup.py bdist_egg
    echo === $pyversion ===
done

echo "--- python 2.7 wheel ---"
pyenv local 2.7.18
python setup.py bdist_wheel
echo === $pyversion ===


python ./setup.py sdist
tarball=dist/${PACKAGE}-${__version__}.tar.gz
if [[ -f $tarball ]]; then
    mv -v $tarball dist/${PACKAGE}_24-${__version__}.tar.gz
fi
finish
