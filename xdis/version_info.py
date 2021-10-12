"""
  Copyright (c) 2020-2021 by Rocky Bernstein

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

  NB. This is not a masterpiece of software, but became more like a hack.
  Probably a complete rewrite would be sensefull. hG/2000-12-27
"""

import sys

PYTHON3 = sys.version_info >= (3, 0)

# We do this crazy way to support Python 2.6 which
# doesn't support version_major, and has a bug in
# floating point so we can't divide 26 by 10 and get
# 2.6
PYTHON_VERSION = sys.version_info[0] + (sys.version_info[1] / 10.0)
PYTHON_VERSION_TRIPLE = tuple(sys.version_info[:3])
PYTHON_VERSION_STR = "%s.%s" % (sys.version_info[0], sys.version_info[1])

IS_PYPY = "__pypy__" in sys.builtin_module_names
