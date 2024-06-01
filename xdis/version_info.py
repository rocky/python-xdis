"""
  Copyright (c) 2020-2024 by Rocky Bernstein

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

IS_PYPY = "__pypy__" in sys.builtin_module_names
IS_GRAAL = "Graal" in platform.python_implementation()


def version_tuple_to_str(
    version_tuple=PYTHON_VERSION_TRIPLE, start=0, end=3, delimiter="."
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


def version_str_to_tuple(python_version: str, length=2) -> tuple:
    return tuple([int(v) for v in python_version.split(".")[:length]])
