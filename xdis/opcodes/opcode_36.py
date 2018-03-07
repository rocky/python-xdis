# (C) Copyright 2016-2017 by Rocky Bernstein
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
CPython 3.6 bytecode opcodes

This is a like Python 3.6's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import(
    def_op, finalize_opcodes,
    format_extended_arg36,
    init_opdata, jrel_op, name_op,
    nargs_op, rm_op, varargs_op,
    update_pj3
    )

import xdis.opcodes.opcode_35 as opcode_35

# When we use EXTENDED_ARG, by how much do we
# shift (or what power of two do we multiply) the operand value?
# Note: this changes in Python 3.6
EXTENDED_ARG_SHIFT = 8

version = 3.6

l = locals()

init_opdata(l, opcode_35, version)

# These are removed since Python 3.6
rm_op(l, 'MAKE_CLOSURE',         134)
rm_op(l, 'CALL_FUNCTION_VAR',    140)
rm_op(l, 'CALL_FUNCTION_VAR_KW', 142)

### Opcodes that have changed drastically ####


# BUILD_MAP_UNPACK_WITH_CALL oparg

# oparg is the number of unpacked mappings which no longer limited by
# 255. As in BUILD_MAP_UNPACK.The location of the function is `oparg +
# 2`.


# CALL_FUNCTION oparg

# oparg is the number of positional arguments on the stack which no
# longer limited by 255.


# CALL_FUNCTION_KW oparg

# This is a different opcode from before, with the name of a similar
# opcode as before. It s like CALL_FUNCTION but values of keyword
# arguments are pushed on the stack after values of positional
# arguments, and then a constant tuple of keyword names is pushed on
# the top of the stack.  *oparg* is the sum of numbers of positional
# and keyword arguments.  The number of keyword arguments is
# determined by the length of the tuple of keyword names.

# CALL_FUNCTION_EX** takes 2 to 3 arguments on the stack: the
# function, the tuple of positional arguments, and optionally the dict
# of keyword arguments if bit 0 of *oparg* is 1.


# MAKE_FUNCTION oparg

# This is a different opcode from before.

# The tuple of default values for positional-or-keyword parameters,
# the dict of default values for keyword-only parameters, the dict of
# annotations and the closure are pushed on the stack if corresponding
# bit (0-3) is set. They are followed by the code object and the
# qualified name of the function.


# These are new since Python 3.6
name_op(l,  'STORE_ANNOTATION', 127) # Index in name list
jrel_op(l,  'SETUP_ASYNC_WITH', 154)
def_op(l,   'FORMAT_VALUE',     155)
varargs_op(l, 'BUILD_CONST_KEY_MAP', 156, -1, 1) # TOS is count of kwargs
nargs_op(l, 'CALL_FUNCTION_EX', 142, -1, 1)
def_op(l,   'SETUP_ANNOTATIONS', 85)
def_op(l,   'BUILD_STRING',     157)
def_op(l,   'BUILD_TUPLE_UNPACK_WITH_CALL', 158)

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
