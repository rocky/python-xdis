# (C) Copyright 2021, 2023-2024 by Rocky Bernstein
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
CPython 3.10 bytecode opcodes

This is like Python 3.10's opcode.py with some classification
of stack usage and information for formatting instructions.
"""

import xdis.opcodes.opcode_39 as opcode_39
from xdis.opcodes.base import def_op, finalize_opcodes, init_opdata, rm_op, update_pj3
from xdis.opcodes.opcode_39 import opcode_arg_fmt39, opcode_extended_fmt39

version_tuple = (3, 10)
python_implementation = "CPython"

loc = locals()

init_opdata(loc, opcode_39, version_tuple)

# fmt: off

# These are removed since 3.9...
rm_op(loc,  "RERAISE",                  48)

# These are added since 3.9...
#         OP NAME                   OPCODE  POP PUSH
#------------------------------------------------
def_op(loc, "GET_LEN",                  30,   0, 1)
def_op(loc, "MATCH_MAPPING",            31,   0, 1)
def_op(loc, "MATCH_SEQUENCE",           32,   0, 1)
def_op(loc, "MATCH_KEYS",               33,   0, 2)
def_op(loc, "COPY_DICT_WITHOUT_KEYS",   34,   2, 2)
def_op(loc, "ROT_N",                    99,   0, 0)
def_op(loc, "RERAISE",                 119,   3, 0)
def_op(loc, "GEN_START",               129,   1, 0)
def_op(loc, "MATCH_CLASS",             152,   2, 1)
# fmt: on


opcode_arg_fmt = opcode_arg_fmt310 = opcode_arg_fmt39.copy()
opcode_extended_fmt = opcode_extended_fmt310 = opcode_extended_fmt39.copy()

# fmt: on

# lnotab format changed in 3.10.
# Using pre 3.10 code, some line numbers can come out negative.

# From 3.10 https://github.com/python/cpython/blob/main/Objects/lnotab_notes.txt

# Description of the internal format of the line number table in Python 3.10
# and earlier.

# (For 3.11 onwards, see Objects/locations.md)

# Conceptually, the line number table consists of a sequence of triples:
#     start-offset (inclusive), end-offset (exclusive), line-number.

# Note that not all byte codes have a line number so we need handle
# `None` for the line-number.

# However, storing the above sequence directly would be very
# inefficient as we would need 12 bytes per entry.

# First, note that the end of one entry is the same as the start of
# the next, so we can overlap entries.  Second, we don't really need
# arbitrary access to the sequence, so we can store deltas.

# We just need to store (end - start, line delta) pairs. The start
# offset of the first entry is always zero.

# Third, most deltas are small, so we can use a single byte for each
# value, as long we allow several entries for the same line.

# Consider the following table
#      Start    End     Line
#       0       6       1
#       6       50      2
#       50      350     7
#       350     360     No line number
#       360     376     8
#       376     380     208

# Stripping the redundant ends gives:

#    End-Start  Line-delta
#       6         +1
#       44        +1
#       300       +5
#       10        No line number
#       16        +1
#       4         +200


# Note that the end - start value is always positive.

# Finally, in order to fit into a single byte we need to convert start
# deltas to the range 0 <= delta <= 254, and line deltas to the range
# -127 <= delta <= 127.
#
# A line delta of -128 is used to indicate no line number.  Also note
# that a delta of zero indicates that there are no bytecodes in the
# given range, which means we can use an invalid line number for that
# range.

# Final form:

#    Start delta   Line delta
#     6               +1
#     44              +1
#     254             +5
#     46              0
#     10              -128 (No line number, treated as a delta of zero)
#     16              +1
#     0               +127 (line 135, but the range is empty as no bytecodes are
#                           at line 135)
#     4               +73

# Iterating over the table.
# -------------------------

# For the `co_lines` attribute we want to emit the full form, omitting
# the (350, 360, No line number) and empty entries.

NO_LINE_NUMBER = -128


def findlinestarts(code, dup_lines=False):
    """Find the offsets in a byte code which are start of lines in the source.

    Generate pairs (offset, lineno) as described in Python/compile.c.
    """
    lineno_table = code.co_lnotab
    byte_increments = list(lineno_table[0::2])

    # line_deltas is an array of 8-bit *signed* integers
    lineno_deltas = []
    # Treat lineno_table bytes has *signed* 8 bit integers
    for x in lineno_table[1::2]:
        x = ord(x)
        if x >= 0x80:
            x -= 0x100
        lineno_deltas.append(x)

    lineno = code.co_firstlineno
    end_offset = 0  # highest offset seen so far
    yield 0, lineno
    for byte_incr, lineno_delta in zip(byte_increments, lineno_deltas):
        if lineno_delta == 0:
            # No change to line number, just accumulate changes to "end_offset"
            # This allows us to accrue offset deltas larger than 254 or so.
            end_offset += ord(byte_incr)
            continue
        start_offset = end_offset
        end_offset = start_offset + ord(byte_incr)
        if lineno_delta == NO_LINE_NUMBER:
            # No line number -- omit reporting lineno table entry
            continue
        lineno += lineno_delta
        if end_offset == start_offset:
            # Empty range, omit reporting lineno table entry.
            # This allows us to accrue line number deltas larger than 254 or so.
            continue
        yield start_offset, lineno


opcode_arg_fmt = opcode_arg_fmt10 = opcode_arg_fmt39.copy()

update_pj3(globals(), loc)
finalize_opcodes(loc)
