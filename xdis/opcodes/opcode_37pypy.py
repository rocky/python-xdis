# (C) Copyright 2021-2022 by Rocky Bernstein
"""
PYPY 3.7 opcodes

This is a like Python 3.7's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import (
    format_CALL_FUNCTION_pos_name_encoded,
    def_op,
    extended_format_ATTR,
    extended_format_RAISE_VARARGS_older,
    extended_format_RETURN_VALUE,
    finalize_opcodes,
    format_RAISE_VARARGS_older,
    format_extended_arg,
    init_opdata,
    name_op,
    nargs_op,
    rm_op,
    store_op,
    varargs_op,
    update_pj3,
)

import xdis.opcodes.opcode_36 as opcode_36

version = 3.7
version_tuple = (3, 7)
python_implementation = "PyPy"

from xdis.opcodes.opcode_33 import extended_format_MAKE_FUNCTION
import xdis.opcodes.opcode_37 as opcode_37
from xdis.opcodes.opcode_37 import (
    format_MAKE_FUNCTION_flags,
)

oppush = {}
oppop = {}

l = locals()
init_opdata(l, opcode_37, version_tuple, is_pypy=True)


# FIXME: DRY common PYPY opcode additions

# fmt: off
rm_op(l, "BUILD_TUPLE_UNPACK_WITH_CALL", 158)
rm_op(l, "LOAD_METHOD",                  160)

nargs_op(l, "CALL_FUNCTION_KW",          141, 9, 1)  # #args + (#kwargs << 8)
nargs_op(l, "CALL_FUNCTION_EX",          142, -2, 1)

# The following were removed from 3.7 but still in Pypy 3.7

store_op(l,   'STORE_ANNOTATION',        127, 1, 0, is_type="name")

# PyPy only
# ----------

name_op(l, "LOOKUP_METHOD",              201, 1, 2)
l["hasvargs"].append(202)
nargs_op(l, "CALL_METHOD_KW",            204, -1, 1)


# Used only in single-mode compilation list-comprehension generators
varargs_op(l, "BUILD_LIST_FROM_ARG",     203)

# PyPy 3.6.1 (and 2.7.13) start to introduce LOAD_REVDB_VAR
import sys

if sys.version_info[:3] >= (3, 6, 1):
    def_op(l, "LOAD_REVDB_VAR",          205)

# FIXME remove (fix uncompyle6)
update_pj3(globals(), l)

# fmt: on
def extended_format_CALL_METHOD(opc, instructions):
    """argc has the number of positional arguments.
    TOS starts the positional arguments
    values for each keyword argument.
    After that is a slot to cache a method function
    Below that is the method attribute to that is looked up to find
    the method name."""
    call_method_inst = instructions[0]
    assert call_method_inst.opname == "CALL_METHOD"
    method_pos = call_method_inst.arg + 1
    assert len(instructions) >= method_pos + 1
    s = ""
    for i, inst in enumerate(instructions[1:]):
        if i == method_pos:
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
            method_pos += (oppop[opcode] - oppush[opcode]) + 1
        if inst.opname in ("LOOKUP_METHOD"):
            method_pos = i
            break
        pass

    if i == method_pos:
        if instructions[method_pos + 2].opname in ("LOAD_NAME", "LOAD_FAST"):
            s += "%s.%s(), " % (
                instructions[method_pos + 2].argrepr,
                instructions[method_pos + 1].argrepr,
            )
            pass
        pass
    s += format_CALL_METHOD(call_method_inst.arg)
    return s


def extended_format_CALL_METHOD_KW(opc, instructions):
    """argc has the number of positional plus keyword arguments.
    TOS is a tuple of keyword argument names and below that are
    values for each keyword argument.
    Below that are positional arguments.
    After that is a slot to cache a method function
    Below that is the method attribute to that is looked up to find
    the method name."""
    call_method_inst = instructions[0]
    assert call_method_inst.opname == "CALL_METHOD_KW"
    method_pos = call_method_inst.arg + 2
    assert len(instructions) >= method_pos + 1
    kw_names = instructions[1]
    assert isinstance(kw_names, tuple)
    kw_name_str = "=..., ".join(kw_names.argval) + "=..."
    s = ""
    for i, inst in enumerate(instructions[2:]):
        if i == method_pos:
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
            method_pos += (oppop[opcode] - oppush[opcode]) + 1
        if inst.opname in ("LOOKUP_METHOD"):
            method_pos = i
            break
        pass

    if i == method_pos:
        if instructions[method_pos + 3].opname in ("LOAD_NAME", "LOAD_FAST"):
            s += "%s.%s" % (
                instructions[method_pos + 3].argrepr,
                instructions[method_pos + 2].argrepr,
            )
            pass
        if call_method_inst.arg > len(kw_names.argval):
            s += "(..., %s), " % kw_name_str
        else:
            s += "(%s), " % kw_name_str
        pass
    s += format_CALL_METHOD_KW(call_method_inst.arg, len(kw_names.argval))
    return s


def format_CALL_METHOD(argc):
    """argc has the number of positional arguments.
    TOS starts the positional arguments
    After that is a slot to cache a method function
    Below that is the method attribute to that is looked up to find
    the method name."""
    return "%d positional" % (argc)


def format_CALL_METHOD_KW(argc, kwarg_count=None):
    """argc has the number of positional plus keyword arguments.
    TOS is a tuple of keyword argument names and below that are
    values for each keyword argument.
    Below that are positional arguments.
    After that is a slot to cache a method function
    Below that is the method attribute to that is looked up to find
    the method name."""
    if isinstance(kwarg_count, int):
        positional_argc = argc - kwarg_count
        return "%d positional, %d keyword" % (positional_argc, kwarg_count)
    else:
        return "%d positional + keyword" % (argc)


opcode_arg_fmt = {
    "CALL_FUNCTION": format_CALL_FUNCTION_pos_name_encoded,
    "CALL_FUNCTION_KW": opcode_36.format_CALL_FUNCTION_KW,
    "CALL_FUNCTION_EX": opcode_36.format_CALL_FUNCTION_EX,
    "CALL_METHOD": format_CALL_METHOD,
    "CALL_METHOD_KW": format_CALL_METHOD_KW,
    "EXTENDED_ARG": format_extended_arg,
    "MAKE_FUNCTION": format_MAKE_FUNCTION_flags,
    "RAISE_VARARGS": format_RAISE_VARARGS_older,
}

opcode_extended_fmt = {
    "CALL_FUNCTION": opcode_36.extended_format_CALL_FUNCTION,
    "CALL_METHOD": extended_format_CALL_METHOD,
    "CALL_METHOD_KW": extended_format_CALL_METHOD_KW,
    "LOAD_ATTR": extended_format_ATTR,
    "MAKE_FUNCTION": extended_format_MAKE_FUNCTION,
    "RAISE_VARARGS": extended_format_RAISE_VARARGS_older,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
    "STORE_ATTR": extended_format_ATTR,
}


finalize_opcodes(l)
