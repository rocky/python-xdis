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
CPython 3.7 bytecode opcodes

This is a like Python 3.7's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import(
    finalize_opcodes,
    format_extended_arg36,
    init_opdata, nargs_op,
    name_op, rm_op,
    update_pj3
    )

import xdis.opcodes.opcode_36 as opcode_36

version = 3.7

l = locals()

init_opdata(l, opcode_36, version)

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

# These are removed since 3.6...
# and STORE_ANNOTATION introduced in 3.6!
rm_op(l, 'STORE_ANNOTATION', 127)

# These are new since Python 3.7
name_op(l, 'LOAD_METHOD', 160)
nargs_op(l, 'CALL_METHOD', 161)

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
