|CircleCI| |PyPI Installs| |Latest Version| |Supported Python Versions|

|packagestatus|

xdis
====

A Cross-Python bytecode disassembler, bytecode/wordcode and magic-number manipulation library/package.


.. contents:: Table of Contents
    :depth: 3


Introduction
------------

The Python dis_ module allows you to disassemble bytecode from the same
version of Python that you are running on. But what about bytecode from
different versions?

That's what this package is for. It can "marshal load" Python
bytecodes from different versions of Python. The command-line routine
*pydisasm* will show disassembly output using the most modern Python
disassembly conventions in a variety of user-specified formats.  Some
of these formats like ``extended`` and ``extended-format`` are the most
advanced of any Python disassembler I know of because they can show
expression-tree on operators. See the `Disassembler
Example`_ below.

Also, if you need to modify and write bytecode, the routines here can
be of help. There are routines to pack and unpack the read-only tuples
in Python's Code type. For interoperability between the changes over
the years to Python CodeType, provide our own versions of the Code
Type to allow interoperability, and we provide routines to reduce the
tedium in writing a bytecode file.

This package also has an extensive knowledge of Python bytecode magic
numbers, including PyPy and others, and how to translate from
``sys.sys_info`` major, minor, and release numbers to the corresponding
magic value.

So if you want to write a cross-version assembler, bytecode-level
analyzer, or optimizer this package may also be useful. In addition to
the kinds of instruction categorization that ``dis`` offers, we have
additional categories for things that would be useful in such a
bytecode assembler, optimizer, or decompiler.

The programs here accept bytecodes from Python version 1.0 to
3.13. The code requires Python 2.4 or later and has been tested on
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

   $ pip install -e .  # or pip install -e .[dev] to include testing package

A GNU makefile is also provided so ``make install`` (possibly as root or
sudo) will do the steps above.

Disassembler Example
--------------------

The cross-version disassembler that is packaged here, can produce
assembly listing that are superior to those typically found in
Python's dis module. Here is an example::

    pydisasm -S -F extended bytecode_3.8/pydisasm-example.pyc
    # pydisasm version 6.1.1.dev0
    # Python bytecode 3.8.0 (3413)
    # Disassembled from Python 3.11.8 (main, Feb 14 2024, 04:47:01) [GCC 13.2.0]
    # Timestamp in code: 1693155156 (2023-08-27 12:52:36)
    # Source code size mod 2**32: 320 bytes
    # Method Name:       <module>
    # Filename:          simple_source/pydisasm-example.py
    # Argument count:    0
    # Position-only argument count: 0
    # Keyword-only arguments: 0
    # Number of locals:  0
    # Stack size:        3
    # Flags:             0x00000040 (NOFREE)
    # First Line:        4
    # Constants:
    #    0: 0
    #    1: None
    #    2: ('version_info',)
    #    3: 1
    #    4: (2, 4)
    #    5: 'Is small power of two'
    # Names:
    #    0: sys
    #    1: version_info
    #    2: print
    #    3: version
    #    4: len
    #    5: major
    #    6: power_of_two
                 # import sys
      4:           0 LOAD_CONST           (0) ; TOS = 0
                   2 LOAD_CONST           (None) ; TOS = None
                   4 IMPORT_NAME          (sys) ; TOS = import_module(sys)
                   6 STORE_NAME           (sys) ; sys = import_module(sys)

                 # from sys import version_info
      5:           8 LOAD_CONST           (0) ; TOS = 0
                  10 LOAD_CONST           (('version_info',)) ; TOS = ('version_info',)
                  12 IMPORT_NAME          (sys) ; TOS = import_module(sys)
                  14 IMPORT_FROM          (version_info) ; TOS = from sys import version_info
                  16 STORE_NAME           (version_info) ; version_info = from sys import version_info
                  18 POP_TOP

                 # print(sys.version)
      7:          20 LOAD_NAME            (print) ; TOS = print
                  22 LOAD_NAME            (sys) ; TOS = sys
                  24 LOAD_ATTR            (version) ; TOS = sys.version
                  26 CALL_FUNCTION        (1 positional argument) ; TOS = print(sys.version)
                  28 POP_TOP

                 # print(len(version_info))
      8:          30 LOAD_NAME            (print) ; TOS = print
                  32 LOAD_NAME            (len) ; TOS = len
                  34 LOAD_NAME            (version_info) ; TOS = version_info
                  36 CALL_FUNCTION        (1 positional argument) ; TOS = len(version_info)
                  38 CALL_FUNCTION        (1 positional argument) ; TOS = print(len(version_info))
                  40 POP_TOP

                 # major = sys.version_info[0]
      9:          42 LOAD_NAME            (sys) ; TOS = sys
                  44 LOAD_ATTR            (version_info) ; TOS = sys.version_info
                  46 LOAD_CONST           (0) ; TOS = 0
                  48 BINARY_SUBSCR        TOS = sys.version_info[0]
                  50 STORE_NAME           (major) ; major = sys.version_info[0]

                 # power_of_two = major & (major - 1)
     10:          52 LOAD_NAME            (major) ; TOS = major
                  54 LOAD_NAME            (major) ; TOS = major
                  56 LOAD_CONST           (1) ; TOS = 1
                  58 BINARY_SUBTRACT      TOS = major - (1)
                  60 BINARY_AND           TOS = major & (major - (1))
                  62 STORE_NAME           (power_of_two) ; power_of_two = major & (major - (1))

                 # if power_of_two in (2, 4):
     11:          64 LOAD_NAME            (power_of_two) ; TOS = power_of_two
                  66 LOAD_CONST           ((2, 4)) ; TOS = (2, 4)
                  68 COMPARE_OP           (in) ; TOS = power_of_two in ((2, 4))
                  70 POP_JUMP_IF_FALSE    (to 80)

                 # print("Is small power of two")
     12:          72 LOAD_NAME            (print) ; TOS = print
                  74 LOAD_CONST           ("Is small power of two") ; TOS = "Is small power of two"
                  76 CALL_FUNCTION        (1 positional argument) ; TOS = print("Is small power of two")
                  78 POP_TOP
             >>   80 LOAD_CONST           (None) ; TOS = None
                  82 RETURN_VALUE         return None

Note in the above that some operand interpretation is done on items that are in the stack.
For example in ::

              24 LOAD_ATTR            (version) | sys.version

from the instruction see that ``sys.version`` is the resolved attribute that is loaded.

Similarly in::

              68 COMPARE_OP           (in) | power_of_two in (2, 4)

we see that we can resolve the two arguments of the ``in`` operation.
Finally in some ``CALL_FUNCTIONS`` we can figure out the name of the function and arguments passed to it.



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
.. |PyPI Installs| image:: https://static.pepy.tech/badge/xdis
.. |packagestatus| image:: https://repology.org/badge/vertical-allrepos/python:xdis.svg
		 :target: https://repology.org/project/python:xdis/versions
		 :alt: Packaging Status
.. _dis: https://docs.python.org/3/library/dis.html
