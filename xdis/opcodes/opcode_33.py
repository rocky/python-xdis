# (C) Copyright 2017, 2020-2021, 2023 by Rocky Bernstein
"""
CPython 3.3 bytecode opcodes

This is a like Python 3.3's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import (
    def_op,
    extended_format_CALL_FUNCTION,
    extended_format_RAISE_VARARGS_older,
    extended_format_RETURN_VALUE,
    finalize_opcodes,
    format_CALL_FUNCTION_pos_name_encoded,
    format_RAISE_VARARGS_older,
    format_extended_arg,
    init_opdata,
    rm_op,
    update_pj3,
)

import xdis.opcodes.opcode_3x as opcode_3x

version = 3.3
version_tuple = (3, 3)
python_implementation = "CPython"

l = locals()
init_opdata(l, opcode_3x, version_tuple)

# Below are opcode changes since Python 3.2

# fmt: off
rm_op(l,  "STOP_CODE",   0)
def_op(l, "YIELD_FROM", 72, 1, 0)
# fmt: on


update_pj3(globals(), l)

finalize_opcodes(l)


def extended_format_ATTR(opc, instructions):
    if instructions[1].opname in (
        "LOAD_CONST",
        "LOAD_GLOBAL",
        "LOAD_ATTR",
        "LOAD_NAME",
    ):
        return "%s.%s " % (instructions[1].argrepr, instructions[0].argrepr)


def extended_format_MAKE_FUNCTION(opc, instructions):
    """make_function_inst should be a "MAKE_FUNCTION" or "MAKE_CLOSURE" instruction. TOS
    should have the function or closure name.
    """
    # From opcode description: argc indicates the total number of positional and keyword arguments.
    # Sometimes the function name is in the stack arg positions back.
    assert len(instructions) >= 2
    inst = instructions[0]
    assert inst.opname in ("MAKE_FUNCTION", "MAKE_CLOSURE")
    s = ""
    name_inst = instructions[1]
    if name_inst.opname in ("LOAD_CONST",):
        s += "%s: " % name_inst.argrepr
        pass
    pos_args, name_pair_args, annotate_args = parse_fn_counts(
        inst.argval
        )
    s += "%d positional, %d keyword only, %d annotated" % (
        pos_args,
        name_pair_args,
        annotate_args,
    )
    return s


def format_MAKE_FUNCTION_default_pos_arg(argc):
    pos_args, name_pair_args, annotate_args = parse_fn_counts(argc)

    s = "%d positional, %d keyword only, %d annotated" % (
        pos_args,
        name_pair_args,
        annotate_args
    )
    return s


def parse_fn_counts(argc):
    annotate_count = (argc >> 16) & 0x7FFF
    # For some reason that I don't understand, annotate_args is off by one
    # when there is an EXENDED_ARG instruction from what is documented in
    # https://docs.python.org/3.4/library/dis.html#opcode-MAKE_CLOSURE
    if annotate_count > 1:
        annotate_count -= 1
    return ((argc & 0xFF), (argc >> 8) & 0xFF, annotate_count)


opcode_arg_fmt = {
    "CALL_FUNCTION": format_CALL_FUNCTION_pos_name_encoded,
    "EXTENDED_ARG": format_extended_arg,
    "MAKE_CLOSURE": format_MAKE_FUNCTION_default_pos_arg,
    "MAKE_FUNCTION": format_MAKE_FUNCTION_default_pos_arg,
    "RAISE_VARARGS": format_RAISE_VARARGS_older,
}

opcode_extended_fmt = {
    "CALL_FUNCTION": extended_format_CALL_FUNCTION,
    "LOAD_ATTR": extended_format_ATTR,
    "MAKE_CLOSURE": extended_format_MAKE_FUNCTION,
    "MAKE_FUNCTION": extended_format_MAKE_FUNCTION,
    "RAISE_VARARGS": extended_format_RAISE_VARARGS_older,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
    "STORE_ATTR": extended_format_ATTR,
}
