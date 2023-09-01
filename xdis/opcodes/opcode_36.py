# (C) Copyright 2016-2017, 2019-2021, 2023 by Rocky Bernstein
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

This is like Python 3.6's opcode.py with some classification
of stack usage.
"""

from typing import Tuple

import xdis.opcodes.opcode_35 as opcode_35
from xdis.opcodes.base import (
    def_op,
    finalize_opcodes,
    init_opdata,
    jrel_op,
    nargs_op,
    rm_op,
    store_op,
    update_pj3,
    varargs_op,
)
from xdis.opcodes.format import (
    extended_format_ATTR,
    extended_format_RAISE_VARARGS_older,
    format_RAISE_VARARGS_older,
    get_arglist,
    short_code_repr,
)
from xdis.opcodes.opcode_35 import opcode_arg_fmt35, opcode_extended_fmt35

oppush = {}
oppop = {}

# When we use EXTENDED_ARG, by how much do we
# shift (or what power of two do we multiply) the operand value?
# Note: this changes in Python 3.6
EXTENDED_ARG_SHIFT = 8

version_tuple = (3, 6)
python_implementation = "CPython"

loc = locals()

init_opdata(loc, opcode_35, version_tuple)

# fmt: off
# These are removed since Python 3.6
rm_op(loc, 'MAKE_CLOSURE',         134)
rm_op(loc, 'CALL_FUNCTION_VAR',    140)
rm_op(loc, 'CALL_FUNCTION_VAR_KW', 142)

# -- Opcodes that have changed drastically --#


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


# fmt: off
# These are new since Python 3.6
#          OP NAME                OPCODE POP PUSH
# -----------------------------------------------
store_op(loc,    'STORE_ANNOTATION', 127,  1,  0, is_type="name") # Stores TOS index in
                                                                   # name list;
jrel_op(loc,     'SETUP_ASYNC_WITH', 154,  2,  8)  # pops __aenter__ and __aexit__;
                                                   # pushed results on stack
def_op(loc,      'FORMAT_VALUE',     155,  1,  1)
varargs_op(loc,  'BUILD_CONST_KEY_MAP', 156, -2, 1) # TOS is count of kwargs
nargs_op(loc,    'CALL_FUNCTION_EX', 142, -2,  1)
def_op(loc,      'SETUP_ANNOTATIONS', 85,  1,  1)
varargs_op(loc,  'BUILD_STRING',     157, -2,  2)
varargs_op(loc,  'BUILD_TUPLE_UNPACK_WITH_CALL', 158)
# fmt: on

MAKE_FUNCTION_FLAGS = tuple("default keyword-only annotation closure".split())


# Can combine with extended_format_MAKE_FUNCTION_10_27?
def extended_format_MAKE_FUNCTION_36(opc, instructions) -> Tuple[str, int]:
    assert len(instructions) >= 2
    inst = instructions[0]
    assert inst.opname in ("MAKE_FUNCTION", "MAKE_CLOSURE")
    s = ""
    name_inst = instructions[1]
    code_inst = instructions[2]
    start_offset = code_inst.offset
    if name_inst.opname in ("LOAD_CONST",):
        s += f"make_function({name_inst.argval}, {short_code_repr(code_inst.argval)})"
        return s, start_offset
    return s, start_offset


def format_MAKE_FUNCTION(flags) -> str:
    if flags == 0:
        return "Neither defaults, keyword-only args, annotations, nor closures"
    pattr = ""
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
        return ""
    elif (flags & 0x03) == 0x01:
        return "!s"
    elif (flags & 0x03) == 0x02:
        return "!r"
    elif (flags & 0x03) == 0x03:
        return "!a"
    elif (flags & 0x04) == 0x04:
        # pop fmt_spec from the stack and use it, else use an
        # empty fmt_spec.
        return ""


def format_extended_arg36(arg):
    return str(arg * (1 << 8))


def format_CALL_FUNCTION(argc):
    """argc indicates the number of positional arguments"""
    if argc == 1:
        plural = ""
    else:
        plural = "s"
    return "%d positional argument%s" % (argc, plural)


def format_CALL_FUNCTION_EX(flags):
    str = ""
    if flags & 0x01:
        str = "keyword and positional arguments"
    else:
        str = "positional arguments only"
    return str


def format_CALL_FUNCTION_KW(argc):
    return "%d total positional and keyword args" % argc


# The meaning of argc changes from 3.5 where this was introduced.
def format_BUILD_MAP_UNPACK_WITH_CALL(count):
    """The lowest byte of oparg is the count of mappings, the relative
    position of the corresponding callable f is encoded in the second byte
    of oparg."""
    return "%d mappings" % count


opcode_arg_fmt36 = opcode_arg_fmt = {
    "BUILD_MAP_UNPACK_WITH_CALL": format_BUILD_MAP_UNPACK_WITH_CALL,
    "CALL_FUNCTION": format_CALL_FUNCTION,
    "CALL_FUNCTION_EX": format_CALL_FUNCTION_EX,
    "CALL_FUNCTION_KW": format_CALL_FUNCTION_KW,
    "EXTENDED_ARG": format_extended_arg36,
    "FORMAT_VALUE": format_value_flags,
    "MAKE_FUNCTION": format_MAKE_FUNCTION,
    "RAISE_VARARGS": format_RAISE_VARARGS_older,
}


update_pj3(globals(), loc)

finalize_opcodes(loc)

# Extended formatting routines
# This should be called after updating globals and finalizing opcodes
# since they make use of the information there.


def extended_format_CALL_METHOD(opc, instructions) -> str:
    """Inst should be a "LOAD_METHOD" instruction. Looks in `instructions`
    to see if we can find a method name.  If not we'll return "".

    """
    # From opcode description: Loads a method named co_names[namei] from the TOS object.
    # Sometimes the method name is in the stack arg positions back.
    call_method_inst = instructions[0]
    assert call_method_inst.opname == "CALL_METHOD"
    method_pos = call_method_inst.arg + 1
    assert len(instructions) >= method_pos
    s = ""
    for inst in instructions[1:method_pos]:
        # Make sure we are in the same basic block
        # and ... ?
        if inst.opname in ("CALL_METHOD",) or inst.is_jump_target:
            break
        pass
    else:
        if instructions[method_pos].opname == "LOAD_METHOD":
            s += "%s: " % instructions[method_pos].argrepr
            pass
        pass
    s += format_CALL_FUNCTION(call_method_inst.arg)
    return s


def extended_format_CALL_FUNCTION36(opc, instructions):
    """call_function_inst should be a "CALL_FUNCTION" instruction. Look in
    `instructions` to see if we can find a method name.  If not we'll
    return None.

    """
    # From opcode description: arg_count indicates the total number of
    # positional and keyword arguments.

    call_inst = instructions[0]
    arg_count = call_inst.argval
    s = ""

    arglist, arg_count, i = get_arglist(instructions, arg_count)

    if arg_count != 0:
        return "", None

    assert i is not None
    fn_inst = instructions[i + 1]
    if fn_inst.opcode in opc.operator_set:
        start_offset = fn_inst.offset
        if instructions[1].opname == "MAKE_FUNCTION":
            arglist[0] = instructions[2].argval

        fn_name = fn_inst.tos_str if fn_inst.tos_str else fn_inst.argrepr
        s = f'{fn_name}({", ".join(reversed(arglist))})'
        return s, start_offset
    return "", None


def extended_format_CALL_FUNCTION_KW(opc, instructions):
    """call_function_inst should be a "CALL_FUNCTION_KW" instruction. Look in
    `instructions` to see if we can find a method name.  If not we'll
    return None.

    """
    # From opcode description: argc indicates the total number of
    # positional and keyword arguments.  Sometimes the function name
    # is in the stack arg positions back.
    call_function_inst = instructions[0]
    assert call_function_inst.opname == "CALL_FUNCTION_KW"
    function_pos = call_function_inst.arg
    assert len(instructions) >= function_pos + 1
    load_const = instructions[1]
    if load_const.opname == "LOAD_CONST" and isinstance(load_const.argval, tuple):
        function_pos += len(load_const.argval) + 1
        s = ""
        i = -1
        for i, inst in enumerate(instructions[2:]):
            if i == function_pos:
                break
            if inst.is_jump_target:
                i += 1
                break
            # Make sure we are in the same basic block
            # and ... ?
            opcode = inst.opcode
            if inst.optype in ("nargs", "vargs"):
                break
            if inst.optype != "name":
                function_pos += (oppop[opcode] - oppush[opcode]) + 1
            if inst.opname in ("CALL_FUNCTION", "CALL_FUNCTION_KW"):
                break
            pass

        if i == function_pos:
            if instructions[function_pos].opname in opc.NAME_OPS | opc.CONST_OPS:
                if instructions[function_pos].opname == "LOAD_ATTR":
                    s += "."
                s += "%s() " % instructions[function_pos].argrepr
                pass
            pass
        s += format_CALL_FUNCTION(call_function_inst.arg)
        return s


opcode_arg_fmt = opcode_arg_fmt36 = {
    **opcode_arg_fmt35,
    **{
        "BUILD_MAP_UNPACK_WITH_CALL": format_BUILD_MAP_UNPACK_WITH_CALL,
        "CALL_FUNCTION": format_CALL_FUNCTION,
        "CALL_FUNCTION_KW": format_CALL_FUNCTION_KW,
        "CALL_FUNCTION_EX": format_CALL_FUNCTION_EX,
        "CALL_METHOD": format_CALL_FUNCTION,
        "MAKE_FUNCTION": format_MAKE_FUNCTION,
        "FORMAT_VALUE": format_value_flags,
        "EXTENDED_ARG": format_extended_arg36,
        "RAISE_VARARGS": format_RAISE_VARARGS_older,
    },
}

opcode_extended_fmt36 = opcode_extended_fmt = {
    **opcode_extended_fmt35,
    **{
        "CALL_FUNCTION_KW": extended_format_CALL_FUNCTION_KW,
        # "CALL_FUNCTION_VAR": extended_format_CALL_FUNCTION,
        "CALL_METHOD": extended_format_CALL_METHOD,
        "MAKE_FUNCTION": extended_format_MAKE_FUNCTION_36,
        "RAISE_VARARGS": extended_format_RAISE_VARARGS_older,
        "STORE_ATTR": extended_format_ATTR,
    },
}
