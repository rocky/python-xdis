# (C) Copyright 2023, 2025 by Rocky Bernstein
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
Bytecode opcode modules with some classification
of stack usage and information for formatting instructions.
This covers information from the Python stdlib opcodes.py.
"""

from xdis.opcodes.opcode_1x import (
    opcode_10,
    opcode_11,
    opcode_12,
    opcode_13,
    opcode_14,
    opcode_15,
    opcode_16,
)
from xdis.opcodes.opcode_2x import (
    opcode_20,
    opcode_21,
    opcode_22,
    opcode_23,
    opcode_24,
    opcode_25,
    opcode_26,
    opcode_27,
)
from xdis.opcodes.opcode_3x import (
    opcode_30,
    opcode_31,
    opcode_32,
    opcode_33,
    opcode_34,
    opcode_35,
    opcode_36,
    opcode_37,
    opcode_38,
    opcode_39,
    opcode_310,
    opcode_311,
    opcode_312,
    opcode_313,
    opcode_314,
)
from xdis.opcodes.opcode_pypy import (
    opcode_26pypy,
    opcode_27pypy,
    opcode_32pypy,
    opcode_33pypy,
    opcode_35pypy,
    opcode_36pypy,
    opcode_37pypy,
    opcode_38pypy,
    opcode_39pypy,
    opcode_310pypy,
    opcode_311pypy,
)
from xdis.opcodes.opcode_rust import opcode_313rust  # opcode_312rust,

# from xdis.opcodes.opcode_graal import (
#     opcode_310graal,
#     opcode_311graal,
#     opcode_312graal,
#     opcode_38graal,
#     )



__all__ = [
    "opcode_10",
    "opcode_11",
    "opcode_12",
    "opcode_13",
    "opcode_14",
    "opcode_15",
    "opcode_16",
    "opcode_20",
    "opcode_21",
    "opcode_22",
    "opcode_23",
    "opcode_24",
    "opcode_25",
    "opcode_26",
    "opcode_26pypy",
    "opcode_27",
    "opcode_27pypy",
    "opcode_30",
    "opcode_31",
    "opcode_310",
    "opcode_311",
    "opcode_312",
    "opcode_313",
    "opcode_314",
    "opcode_32",
    "opcode_33",
    "opcode_34",
    "opcode_35",
    "opcode_36",
    "opcode_37",
    "opcode_38",
    "opcode_39",
    "opcode_310pypy",
    "opcode_311pypy",
    "opcode_32pypy",
    "opcode_33pypy",
    "opcode_35pypy",
    "opcode_36pypy",
    "opcode_37pypy",
    "opcode_38pypy",
    "opcode_39pypy",
    # "opcode_310graal",
    # "opcode_311graal",
    # "opcode_312graal",
    "opcode_38graal",
    # "opcode_312rust",
    "opcode_313rust",

]
