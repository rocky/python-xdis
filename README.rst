|TravisCI| |CircleCI| |PyPI Installs| |Latest Version| |Supported Python Versions|

|packagestatus|

xdis
====

A Cross-Python bytecode disassembler, bytecode/wordcode and magic-number manipulation library/package.


Introduction
------------

The Python dis_ module allows you to disassemble bytecode from the same
version of Python that you are running on. But what about bytecode from
different versions?

That's what this package is for. It can "marshal load" Python
bytecodes from different versions of Python. The command-line routine
*pydisasm* will show disassembly output using Python 3.8 disassembly
conventions.

Also, if you need to modify and write bytecode, the routines here can
be of help. There are routines to pack and unpack the read-only tuples
in Python's Code type. For interoperability between Python 2 and 3 we
provide our own versions of the Code type, and we provide routines to
reduce the tedium in writing a bytecode file.

This package also has an extensive knowledge of Python bytecode magic
numbers, including Pypy and others, and how to translate from
`sys.sys_info` major, minor, and release numbers to the corresponding
magic value.

So If you want to write a cross-version assembler, or a
bytecode-level optimizer this package may also be useful. In addition
to the kinds of instruction categorization that `dis` offers, we have
additional categories for things that would be useful in such a
bytecode optimizer.

The programs here accept bytecodes from Python version 1.0 to 3.8 or
so. The code requires Python 2.4 or later and has been tested on
Python running lots of Python versions.

To install versions for Python before 2.6 install via eggs or
use the python-2.4 branch of git in github.


Installation
------------

The standard Python routine:

::

    $ pip install -e .
    $ pip install -r requirements-dev.txt

A GNU makefile is also provided so :code:`make install` (possibly as root or
sudo) will do the steps above.

Testing
-------

::

   $ make check

A GNU makefile has been added to smooth over setting running the right
command, and running tests from fastest to slowest.

If you have remake_ installed, you can see the list of all tasks
including tests via :code:`remake --tasks`.


Usage
-----

Run

::

     $ ./bin/pydisasm -h

for usage help.


As a drop-in replacement for dis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`xdis` also provides some support as a drop in replacement for the
the Python library `dis <https://docs.python.org/3/library/dis.html>`_
module. This is may be desirable when you want to use the improved API
from Python 3.4 or later from an earlier Python version.

For example:

>>> # works in Python 2 and 3
>>> import xdis.std as dis
>>> [x.opname for x in dis.Bytecode('a = 10')]
['LOAD_CONST', 'STORE_NAME', 'LOAD_CONST', 'RETURN_VALUE']

There may some small differences in output produced for formatted
disassembly or how we show compiler flags. We expect you'll
find the `xdis` output more informative though.

See Also
--------

* https://pypi.org/project/uncompyle6/ : Python Bytecode Deparsing
* https://pypi.org/project/xasm/ : Python Bytecode Assembler
* https://pypi.org/project/x-python/ : Python Bytecode Interpreter written in Python

.. _trepan: https://pypi.python.org/pypi/trepan
.. _debuggers: https://pypi.python.org/pypi/trepan3k
.. _remake: http://bashdb.sf.net/remake
.. |TravisCI| image:: https://travis-ci.org/rocky/python-xdis.svg?branch=master
		 :target: https://travis-ci.org/rocky/python-xdis
.. |CircleCI| image:: https://circleci.com/gh/rocky/python-xdis.svg?style=svg
    :target: https://circleci.com/gh/rocky/python-xdis
.. |Supported Python Versions| image:: https://img.shields.io/pypi/pyversions/xdis.svg
.. |Latest Version| image:: https://badge.fury.io/py/xdis.svg
		 :target: https://badge.fury.io/py/xdis
.. |PyPI Installs| image:: https://pepy.tech/badge/xdis/month
.. |packagestatus| image:: https://repology.org/badge/vertical-allrepos/python:xdis.svg
		 :target: https://repology.org/project/python:xdis/versions
.. _dis: https://docs.python.org/3/library/dis.html
