# Automated crossversion testing
This testing suite is used for automatic testing of differences found between xdis and dis.
This is done by having a way to identically "serialize" important attributes in xdis and dis bytecodes.
We then can check a diff between a serialized xdis and dis bytecode to find if xdis is parsing something incorrectly.
Most tests should be ran using the makefile.

# Parsing results
When running `make test`, tox will serialize bytecode to be put into text form. Given a bytecode compiled in 3.11 and natively disassembled, we go through each of our test versions, say 3.9 ... 3.14, and disassemble the same 3.11 bytecode.
Given the 3.11 serialized disasembly, disassembled from 3.11, we take the diff between that and a serialized 3.11 disassembled from any of our test versions.
This lets us see if there are any differences in how xdis handles native vs cross version.

This is repeated for every test version.
```
test_vers = (3.9, 3.10, 3.11, 3.12, 3.13)

for native in test_vers:
    for v in test_vers:
        assert disasm(native) == disasm(v)
```

`make test` will run a series of pytests. If there is a failure, the left hand side is the native dis, and the right hand side is the xdis cross version. You will also see `case = 3.*`, this shows which version of python is being ran for that test.

Pytest will fail early, so not all tests may be ran.

# System Requirements
- `uv`
    - uv will handle everything on its own

---OR---

- `pyenv` and `pyenv-virtualenv`
    - Each version needing to be tested should be installed with pyenv
- `tox`

# Usage
## Makefile
Run `make` or `make help` to show the help menu for running and preparing tests, or with `remake`, `remake --tasks`.

To simply run tests, `make test` will copy some sources, prepare template files, and run tests.
