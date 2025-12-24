# (C) Copyright 2017-2018, 2020-2021, 2023-2025
# by Rocky Bernstein
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
CPython 3.2 bytecode opcodes to be used as a base for other opcodes including 3.2.

This is used in bytecode disassembly among other things. This is
similar to the opcodes in Python's opcode.py library.

If this file changes the other opcode files may have to be adjusted accordingly.
"""

from xdis.opcodes.format.extended import opcode_extended_fmt_base, short_code_repr


def extended_format_MAKE_FUNCTION_30_35(opc, instructions):
    """make_function_inst should be a "MAKE_FUNCTION" or "MAKE_CLOSURE" instruction. TOS
    should have the function or closure name.
    """
    # From opcode description: argc indicates the total number of
    # positional and keyword arguments.  Sometimes the function name
    # is in the stack arg positions back.
    assert len(instructions) >= 2
    inst = instructions[0]
    assert inst.opname in ("MAKE_FUNCTION", "MAKE_CLOSURE")
    s = ""
    name_inst = instructions[1]
    start_offset = name_inst.offset
    if name_inst.opname in ("LOAD_CONST",):
        s += "make_function(%s)" % short_code_repr(name_inst.argval)
        return s, start_offset
    s += format_MAKE_FUNCTION_30_35(inst.argval)
    return s, start_offset


def format_MAKE_FUNCTION_30_35(argc):
    pos_args, name_pair_args, annotate_args = parse_fn_counts_30_35(argc)
    if (pos_args, name_pair_args, annotate_args) == (0, 0, 0):
        return "No arguments"

    s = "%d positional, %d keyword only, %d annotated" % (
        pos_args,
        name_pair_args,
        annotate_args,
    )
    return s


def parse_fn_counts_30_35(argc):
    """
    In Python 3.0 to 3.5 MAKE_CLOSURE and MAKE_FUNCTION encode
    arguments counts of positional, default + named, and annotation
    arguments a particular kind of encoding where each of
    the entry is a packed byte value of the lower 24 bits
    of ``argc``.  The high bits of argc may have come from
    an EXTENDED_ARG instruction. Here, we unpack the values
    from the ``argc`` int and return a triple of the
    positional args, named_args, and annotation args.
    """
    annotate_count = (argc >> 16) & 0x7FFF
    # For some reason that I don't understand, annotate_args is off by one
    # when there is an EXENDED_ARG instruction from what is documented in
    # https://docs.python.org/3.4/library/dis.html#opcode-MAKE_CLOSURE
    if annotate_count > 1:
        annotate_count -= 1
    return ((argc & 0xFF), (argc >> 8) & 0xFF, annotate_count)


opcode_extended_fmt_base3x = opcode_extended_fmt_base.copy()
