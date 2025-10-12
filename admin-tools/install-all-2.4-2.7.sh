#!/usr/bin/bash
PACKAGE="xdis"
xdis_owd=$(pwd)
bs=${BASH_SOURCE[0]}
mydir=$(dirname $bs)
xdis_fulldir=$(readlink -f $mydir)
cd $xdis_fulldir

source ../${PACKAGE}/version.py
if [[ ! $__version__ ]] ; then
    echo "Something is wrong: __version__ should have been set."
    exit 1
fi

pyenv_file="pyenv-2.4-2.7-versions"
if ! source $pyenv_file ; then
    echo "Having trouble reading ${pyenv_file} version $(pwd)"
    exit 1
fi

cd ../dist/

install_check_command="pydisasm --version"
for pyversion in $PYVERSIONS; do
    echo "*** Installing ${install_file} for Python ${pyversion} ***"
    pyenv local $pyversion
    # Pick out first two numbers of version, e.g. 3.5.1 -> 35
    first_two=$(echo $pyversion | cut -d'.' -f 1-2)
    easy_install xdis-${__version__}-py${first_two}.egg
    $install_check_command
    echo "----"
done
