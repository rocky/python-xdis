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
     cd $make_dist_xdis_33_owd
  fi
}

make_dist_xdis_33_owd=$(pwd)
cd $(dirname ${BASH_SOURCE[0]})
trap finish EXIT

if ! source ./pyenv-3.3-3.5-versions ; then
    exit $?
fi
if ! source ./setup-python-3.3.sh ; then
    exit $?
fi

cd ..
source $PACKAGE/version.py
if [[ ! -n $__version__ ]]; then
    echo "Something is wrong: __version__ should have been set."
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
    # pip bdist_egg create too-general wheels. So
    # we narrow that by moving the generated wheel.

    # Pick out first two numbers of version, e.g. 3.5.1 -> 35
    first_two=$(echo $pyversion | cut -d'.' -f 1-2 | sed -e 's/\.//')
    rm -fr build
    python setup.py bdist_egg bdist_wheel
    if [[ $first_two =~ py* ]]; then
	if [[ $first_two =~ pypy* ]]; then
	    # For PyPy, remove the what is after the dash, e.g. pypy37-none-any.whl instead of pypy37-7-none-any.whl
	    first_two=${first_two%-*}
	fi
	mv -v dist/${PACKAGE}-$__version__-{py3,$first_two}-none-any.whl
    else
	mv -v dist/${PACKAGE}-$__version__-{py3,py$first_two}-none-any.whl
    fi
    echo === $pyversion ===
done

python ./setup.py sdist

tarball=dist/${PACKAGE}-${__version__}.tar.gz
if [[ -f $tarball ]]; then
    version_specific_tarball=dist/${PACKAGE_NAME}_33-${__version__}.tar.gz
    mv -v $tarball $version_specific_tarball
    twine check $version_specific_tarball
fi
finish
