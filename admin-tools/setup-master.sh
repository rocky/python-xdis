#!/bin/bash
PYTHON_VERSION=2.7.14

git checkout master && git pull && pyenv local $PYTHON_VERSION
