# Automated crossversion testing
This testing suite is used for automatic testing of differences found between xdis and dis.
This is done by having a way to identically "serialize" important attributes in xdis and dis bytecodes.
We then can check a diff between a serialized xdis and dis bytecode to find if xdis is parsing something incorrectly.
Most tests should be ran using the makefile.

# System Requirements
- `pyenv` and `pyenv-virtualenv`
    - Each version needing to be tested should be installed with pyenv.
- `tox`

# Usage
## Makefile
Run `make` or `make help` to show the help menu for running and preparing tests.

To simply run tests, `make test` will copy some sources, prepare template files, and run tests.
