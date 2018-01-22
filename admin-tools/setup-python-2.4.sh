#!/bin/bash
PYTHON_VERSION=2.4.6

git checkout python-2.4  && git pull && pyenv local $PYTHON_VERSION
