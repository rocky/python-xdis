"""
Copyright (c) 2020-2025 by Rocky Bernstein

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import platform
import sys

PYTHON3 = sys.version_info >= (3, 0)

PYTHON_VERSION_TRIPLE = tuple(sys.version_info[:3])
PYTHON_VERSION_STR = "%s.%s" % (sys.version_info[0], sys.version_info[1])


class PythonImplementation(object):
    """
    Enumeration of Python interpreter implementations. Each member's value is the
    canonical string returned by platform.python_implementation() for that implementation.
    """

    CPython = "CPython"
    PyPy = "PyPy"
    Graal = "Graal"
    RustPython = "RustPython"
    Jython = "Jython"
    Other = "Other"

    def __init__(self, kind):
        self.kind = kind

    def __str__(self):
        """
        Return the string value of the implementation. This makes str(PythonImplemtation.*)
        return the underlying implementation string (e.g. "CPython", "Graal", ...).
        """
        return self.kind


def get_python_implementation(
    implementation: str = platform.python_implementation(),
) -> PythonImplementation:
    """
    Detect the current Python implementation and return the corresponding
    PlatformImplemtation enum member.
    """
    # Match common exact names first
    if implementation == "CPython":
        return PythonImplementation.CPython
    elif implementation == "PyPy":
        return PythonImplementation.PyPy
    elif implementation == "RustPython":
        return PythonImplementation.RustPython
    elif implementation == "Jython":
        return PythonImplementation.Jython
    # Graal may appear as "GraalVM" or include "Graal" in some environments
    elif "Graal" in implementation:
        return PythonImplementation.Graal
    # If nothing matched, return Other.
    return PythonImplementation.Other


PYTHON_IMPLEMENTATION = get_python_implementation()
IS_GRAAL = PYTHON_IMPLEMENTATION == PythonImplementation.Graal
IS_PYPY = PYTHON_IMPLEMENTATION == PythonImplementation.PyPy
IS_RUST = PYTHON_IMPLEMENTATION == PythonImplementation.RustPython


def version_tuple_to_str(
    version_tuple: tuple = PYTHON_VERSION_TRIPLE,
    start: int = 0,
    end: int = 3,
    delimiter: str = ".",
) -> str:
    """
    Turn a version tuple, e.g. (3,2,6), into a dotted string, e.g. "3.2.6".

    ``version_tuple`` is a tuple similar to what is might be returned in
    tuple(sys.version_info[:3]), however, the parts in the tuple could anything that
    has a str() method. By default, and often the length is 3, but in practice
    it could be other lengths.

    ``end`` is the length of version_tuple that you want to use.
    delimiter is what string to put in the between components.
    """
    return delimiter.join([str(v) for v in version_tuple[start:end]])


def version_str_to_tuple(python_version: str, length=2):
    return tuple([int(v) for v in python_version.split(".")[:length]])
