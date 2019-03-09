# (C) Copyright 2019 by Rocky Bernstein
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
CPython 3.8 bytecode opcodes

This is a like Python 3.8's opcode.py
"""

from xdis.opcodes.base import(
    finalize_opcodes,
    format_extended_arg36,
    init_opdata, nargs_op,
    def_op, jrel_op, rm_op,
    update_pj3
    )

import xdis.opcodes.opcode_37 as opcode_37

version = 3.8

l = locals()

init_opdata(l, opcode_37, version)

# These are removed since 3.7...
rm_op(l, 'BREAK_LOOP', 80)
rm_op(l, 'CONTINUE_LOOP', 119)
rm_op(l, 'SETUP_LOOP', 120)
rm_op(l, 'SETUP_EXCEPT', 121)

# These are new since Python 3.7

#          OP NAME            OPCODE POP PUSH
#--------------------------------------------
def_op(l, 'ROT_FOUR',           6,   4, 4)
def_op(l, 'BEGIN_FINALLY',     53,   0, 1)
def_op(l, 'END_ASYNC_FOR',     54,   7, 0)  # POP is 0, when not 7
def_op(l, 'END_FINALLY',       88,   1, 0)  # POP is 6, when not 1
jrel_op(l, 'CALL_FINALLY',     162,   0, 1)
nargs_op(l, 'POP_FINALLY',    163,   0, 0)  # PUSH/POP vary

MAKE_FUNCTION_FLAGS = tuple("default keyword-only annotation closure".split())

def format_MAKE_FUNCTION_arg(flags):
    pattr = ''
    for flag in MAKE_FUNCTION_FLAGS:
        bit = flags & 1
        if bit:
            if pattr:
                pattr += ", " + flag
            else:
                pattr = flag
                pass
            pass
        flags >>= 1
    return pattr

def format_value_flags(flags):
    if (flags & 0x03) == 0x00:
        return ''
    elif (flags & 0x03) == 0x01:
        return '!s'
    elif (flags & 0x03) == 0x02:
        return '!r'
    elif (flags & 0x03) == 0x03:
        return '!a'
    elif (flags & 0x04) == 0x04:
        # pop fmt_spec from the stack and use it, else use an
        # empty fmt_spec.
        return ''

opcode_arg_fmt = {
    'MAKE_FUNCTION': format_MAKE_FUNCTION_arg,
    'FORMAT_VALUE': format_value_flags,
    'EXTENDED_ARG': format_extended_arg36
}

update_pj3(globals(), l)

finalize_opcodes(l)
