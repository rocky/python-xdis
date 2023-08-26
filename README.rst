|CircleCI| |PyPI Installs| |Latest Version| |Supported Python Versions|

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
*pydisasm* will show disassembly output using the most modern Python
disassembly conventions.

Also, if you need to modify and write bytecode, the routines here can
be of help. There are routines to pack and unpack the read-only tuples
in Python's Code type. For interoperability between Python 2 and 3 we
provide our own versions of the Code type, and we provide routines to
reduce the tedium in writing a bytecode file.

This package also has an extensive knowledge of Python bytecode magic
numbers, including Pypy and others, and how to translate from
``sys.sys_info`` major, minor, and release numbers to the corresponding
magic value.

So if you want to write a cross-version assembler, or a
bytecode-level optimizer this package may also be useful. In addition
to the kinds of instruction categorization that ``dis``` offers, we have
additional categories for things that would be useful in such a
bytecode assembler, optimizer, or decompiler.

The programs here accept bytecodes from Python version 1.0 to 3.11 or
so. The code requires Python 2.4 or later and has been tested on
Python running lots of Python versions.

When installing, except for the most recent versions of Python, use
the Python egg or wheel that matches that version, e.g. ``xdis-6.0.2-py3.3.egg``, ``xdis-6.0.2-py33-none-any.whl``.
Of course for versions that pre-date wheel's, like Python 2.6, you will have to use eggs.

To install older versions for from source in git use the branch
``python-2.4-to-2.7`` for Python versions from 2.4 to 2.7,
``python-3.1-to-3.2`` for Python versions from 3.1 to 3.2,
``python-3.3-to-3.5`` for Python versions from 3.3 to 3.5. The master
branch handles Python 3.6 and later.

Installation
------------

The standard Python routine:

::

    $ pip install -e .
    $ pip install -r requirements-dev.txt

A GNU makefile is also provided so ``make install`` (possibly as root or
sudo) will do the steps above.

Disassembler Example
--------------------

The cross-version disassembler that is packaged here, can produce
assembly listing that are superior to those typically found in
Python's dis module. Here is an example::

    pydisasm --show-source -F extended-bytes bytecode_3.10/pydisasm-example.pyc
    # pydisasm version 6.1.0.dev0
    # Python bytecode 3.10.0 (3439)
    # Disassembled from Python 3.9.17 (main, Jun 21 2023, 08:24:02)
    # [GCC 12.2.0]
    # Timestamp in code: 1692566016 (2023-08-20 17:13:36)
    # Source code size mod 2**32: 264 bytes
    # Method Name:       <module>
    # Filename:          simple_source/pydisasm-example.py
    # Argument count:    0
    # Position-only argument count: 0
    # Keyword-only arguments: 0
    # Number of locals:  0
    # Stack size:        3
    # Flags:             0x00000040 (NOFREE)
    # First Line:        1
    # Constants:
    #    0: 0
    #    1: None
    #    2: 1
    #    3: (2, 4)
    #    4: 'Is small power of two'
    # Names:
    #    0: sys
    #    1: print
    #    2: version
    #    3: version_info
    #    4: major
    #    5: power_of_two
                 # """An example to show off Python's extended disassembly.
      1:           0 |09 00| NOP

                 # """An example to show off Python's extended disassembly.
      1:           2 |64 00| LOAD_CONST           (0)
                   4 |64 01| LOAD_CONST           (None)
                   6 |6c 00| IMPORT_NAME          (sys)
                   8 |5a 00| STORE_NAME           (sys)

                 # import sys
      4:          10 |65 01| LOAD_NAME            (print)
                  12 |65 00| LOAD_NAME            (sys)
                  14 |6a 02| LOAD_ATTR            (sys.version)
                  16 |83 01| CALL_FUNCTION        (sys: 1 positional argument)
                  18 |01 00| POP_TOP

                 # print(sys.version)
      5:          20 |65 00| LOAD_NAME            (sys)
                  22 |6a 03| LOAD_ATTR            (sys.version_info)
                  24 |64 00| LOAD_CONST           (0)
                  26 |19 00| BINARY_SUBSCR        (version_info[0])
                  28 |5a 04| STORE_NAME           (major)

                 # major = sys.version_info[0]
      6:          30 |65 04| LOAD_NAME            (major)
                  32 |65 04| LOAD_NAME            (major)
                  34 |64 02| LOAD_CONST           (1)
                  36 |18 00| BINARY_SUBTRACT      (major - 1)
                  38 |40 00| BINARY_AND           (... & major - 1)
                  40 |5a 05| STORE_NAME           (power_of_two)

                 # power_of_two = major & (major -1)
      7:          42 |65 05| LOAD_NAME            (power_of_two)
                  44 |64 03| LOAD_CONST           ((2, 4))
                  46 |76 00| CONTAINS_OP          (power_of_two in (2, 4))
                  48 |72 1f| POP_JUMP_IF_FALSE    (to 62)

                 # if power_of_two in (2, 4):
      8:          50 |65 01| LOAD_NAME            (print)
                  52 |64 04| LOAD_CONST           ('Is small power of two')
                  54 |83 01| CALL_FUNCTION        (print: 1 positional argument)
                  56 |01 00| POP_TOP
                  58 |64 01| LOAD_CONST           (None)
                  60 |53 00| RETURN_VALUE         (return None)

                 # print("Is small power of two")
      9:     >>   62 |64 01| LOAD_CONST           (None)
                  64 |53 00| RETURN_VALUE         (return None)


Note in the above that some operand interpretation is done on items that are in the stack.
For example in ::

              14 |6a 02| LOAD_ATTR            (sys.version)

from the instruction see clean that ``sys.version`` is the resolved attribute that is loaded.

Similarly in::

              46 |76 00| CONTAINS_OP          (power_of_two in (2, 4))


we see that we can resolve the two arguments of the ``in`` operation.



Testing
-------

::

   $ make check

A GNU makefile has been added to smooth over setting running the right
command, and running tests from fastest to slowest.

If you have remake_ installed, you can see the list of all tasks
including tests via ``remake --tasks``.


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
find the ``xdis`` output more informative though.

See Also
--------

* https://pypi.org/project/uncompyle6/ : Python Bytecode Deparsing
* https://pypi.org/project/decompyle3/ : Python Bytecode Deparsing for Python 3.7 and 3.8
* https://pypi.org/project/xasm/ : Python Bytecode Assembler
* https://pypi.org/project/x-python/ : Python Bytecode Interpreter written in Python

.. _trepan: https://pypi.python.org/pypi/trepan
.. _debuggers: https://pypi.python.org/pypi/trepan3k
.. _remake: http://bashdb.sf.net/remake
.. |CircleCI| image:: https://circleci.com/gh/rocky/python-xdis.svg?style=svg
    :target: https://circleci.com/gh/rocky/python-xdis
.. |Supported Python Versions| image:: https://img.shields.io/pypi/pyversions/xdis.svg
.. |Latest Version| image:: https://badge.fury.io/py/xdis.svg
		 :target: https://badge.fury.io/py/xdis
.. |PyPI Installs| image:: https://pepy.tech/badge/xdis/month
.. |packagestatus| image:: https://repology.org/badge/vertical-allrepos/python:xdis.svg
		 :target: https://repology.org/project/python:xdis/versions
.. _dis: https://docs.python.org/3/library/dis.html
