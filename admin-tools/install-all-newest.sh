#!/usr/bin/bash
PACKAGE="xdis"
xdis_owd=$(pwd)
bs=${BASH_SOURCE[0]}
mydir=$(dirname $bs)
xdis_fulldir=$(readlink -f $mydir)
cd $xdis_fulldir

pyenv_file="pyenv-newest-versions"
if ! source $pyenv_file ; then
    echo "Having trouble reading ${pyenv_file} version $(pwd)"
    exit 1
fi

source ../${PACKAGE}/version.py
if [[ ! $__version__ ]] ; then
    echo "Something is wrong: __version__ should have been set."
    exit 1
fi

cd ../dist/

install_check_command="pydisasm --version"
install_file="xdis-${__version__}.tar.gz"
for pyversion in $PYVERSIONS; do
    echo "*** Installing ${install_file} for Python ${pyversion} ***"
    pyenv local $pyversion
    pip install $install_file
    $install_check_command
    echo "----"
done
