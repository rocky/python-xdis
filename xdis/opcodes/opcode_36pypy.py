# (C) Copyright 2019-2021, 2023-2024 by Rocky Bernstein
"""
PYPY 3.6 opcodes

This is a like PyPy 3.6's opcode.py with some classification
of stack usage and information for formatting instructions.
"""

import sys
from typing import List, Optional, Tuple

import xdis.opcodes.opcode_36 as opcode_36
from xdis.opcodes.base import (
    call_op,
    def_op,
    finalize_opcodes,
    init_opdata,
    jrel_op,
    name_op,
    rm_op,
    update_pj3,
    varargs_op,
)
from xdis.opcodes.opcode_36 import opcode_arg_fmt36, opcode_extended_fmt36

version_tuple = (3, 6)
python_implementation = "PyPy"

# oppush[op] => number of stack entries pushed
oppush: List[int] = [0] * 256

# oppop[op] => number of stack entries popped
oppop: List[int] = [0] * 256

loc = locals()
init_opdata(loc, opcode_36, version_tuple, is_pypy=True)

## FIXME: DRY common PYPY opcode additions

# Opcodes removed from 3.6.

# fmt: off
rm_op(loc,    "CALL_FUNCTION_EX",             142)
rm_op(loc,    "BUILD_TUPLE_UNPACK_WITH_CALL", 158)

# The following were removed from 3.6 but still in Pypy 3.6
def_op(loc,   "MAKE_CLOSURE",                 134, 9, 1)  # TOS is number of items to pop
call_op(loc, "CALL_FUNCTION_VAR",             140, 9, 1)  # #args + (#kwargs << 8)
call_op(loc, "CALL_FUNCTION_KW",              141, 9, 1)  # #args + (#kwargs << 8)
call_op(loc, "CALL_FUNCTION_VAR_KW",          142, 9, 1)  # #args + (#kwargs << 8)

# PyPy only
# ----------

# See:
# https://doc.pypy.org/en/latest/interpreter-optimizations.html#lookup-method-call-method
name_op(loc, "LOOKUP_METHOD",                 201, 1, 2)
call_op(loc, "CALL_METHOD",                  202, -1, 1)
loc["hasvargs"].append(202)


# Used only in single-mode compilation list-comprehension generators
varargs_op(loc, "BUILD_LIST_FROM_ARG",        203)

# Used only in assert statements
jrel_op(loc, "JUMP_IF_NOT_DEBUG", 204, conditional=True)
# fmt: on

# PyPy 3.6.1 (and 2.7.13) start to introduce LOAD_REVDB_VAR

if sys.version_info[:3] >= (3, 6, 1):
    def_op(loc, "LOAD_REVDB_VAR", 205)


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
    i = -1
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

    if i == method_pos and len(instructions) > method_pos + 2:
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
    i = -1
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


def extended_format_LOOKUP_METHOD(opc, instructions: list) -> Tuple[str, Optional[int]]:
    if instructions[1].opcode in opc.NAME_OPS | opc.CONST_OPS | opc.LOCAL_OPS:
        return (
            f"{instructions[1].argrepr}.{instructions[0].argrepr}",
            instructions[1].offset,
        )
    return "", None


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


opcode_arg_fmt = opcode_arg_fmt36pypy = {
    **opcode_arg_fmt36,
}

opcode_extended_fmt = opcode_extended_fmt36pypy = {
    **opcode_extended_fmt36,
}

# FIXME remove (fix uncompyle6)
update_pj3(globals(), loc)
finalize_opcodes(loc)
