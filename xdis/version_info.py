"""
  Copyright (c) 2020-2022 by Rocky Bernstein

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

import sys

PYTHON3 = sys.version_info >= (3, 0)

# NOTE: PYTHON_VERSION is going away
# We do this crazy way to support Python 2.6 which
# doesn't support version_major, and has a bug in
# floating point so we can't divide 26 by 10 and get
# 2.6
PYTHON_VERSION = sys.version_info[0] + (sys.version_info[1] / 10.0)


PYTHON_VERSION_TRIPLE = tuple(sys.version_info[:3])
PYTHON_VERSION_STR = "%s.%s" % (sys.version_info[0], sys.version_info[1])

IS_PYPY = "__pypy__" in sys.builtin_module_names


def version_tuple_to_str(
    version_tuple=PYTHON_VERSION_TRIPLE, start=0, end=3, delimiter="."
) -> str:
    """
    Turn a version tuple, e.g. (3,2,6), into a dotted string, e.g. "3.2.6".

    version_tuple is a tuple similar to what is might be returned in
    tuple(sys.version_info[:3]), however, the parts in their could anything that
    has a str() method. By defaul, and often the length is 3 but in in practice
    it could be other lengths

    end is the length of version_tuple that you want to use.
    delimiter is what string to put in the between components.
    """
    return delimiter.join([str(v) for v in version_tuple[start:end]])


def version_str_to_tuple(python_version: str, len=2) -> tuple:
    return tuple([int(v) for v in python_version.split(".")[:len]])
