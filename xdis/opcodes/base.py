# (C) Copyright 2017, 2019-2023 by Rocky Bernstein
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
Common routines for entering and classifiying opcodes. Inspired by,
limited by, and somewhat compatible with the corresponding
Python opcode.py structures
"""

import sys
from copy import deepcopy
from typing import Optional, Tuple

from xdis import wordcode
from xdis.cross_dis import findlabels, findlinestarts, get_jump_target_maps
from xdis.version_info import IS_PYPY, PYTHON_VERSION_TRIPLE

cmp_op = (
    "<",
    "<=",
    "==",
    "!=",
    ">",
    ">=",
    "in",
    "not-in",
    "is",
    "is-not",
    "exception-match",
    "BAD",
)

# Opcodes greater than 90 take an instruction operand or "argument"
# as opcode.py likes to call it.
HAVE_ARGUMENT = 90

fields2copy = """
binaryop
hascompare hascondition
hasconst hasfree hasjabs hasjrel haslocal
hasname hasnargs hasstore hasvargs oppop oppush
nofollow unaryop
""".split()


def init_opdata(loc, from_mod, version_tuple=None, is_pypy=False):
    """Sets up a number of the structures found in Python's
    opcode.py. Python opcode.py routines assign attributes to modules.
    In order to do this in a modular way here, the local dictionary
    for the module is passed.
    """

    if version_tuple is None:
        version_tuple = sys.version_info[:2]
    if version_tuple:
        loc["python_version"] = version_tuple
    loc["is_pypy"] = is_pypy
    loc["cmp_op"] = cmp_op
    loc["HAVE_ARGUMENT"] = HAVE_ARGUMENT
    loc["findlinestarts"] = findlinestarts
    if version_tuple <= (3, 5):
        loc["findlabels"] = findlabels
        loc["get_jump_targets"] = findlabels
        loc["get_jump_target_maps"] = get_jump_target_maps
    else:
        loc["findlabels"] = wordcode.findlabels
        loc["get_jump_targets"] = wordcode.findlabels
        loc["get_jump_target_maps"] = wordcode.get_jump_target_maps

    loc["opmap"] = deepcopy(from_mod.opmap)
    loc["opname"] = deepcopy(from_mod.opname)

    for field in fields2copy:
        loc[field] = list(getattr(from_mod, field))


def binary_op(loc: dict, name: str, opcode: int, pop: int = 2, push: int = 1):
    loc["binaryop"].append(opcode)
    def_op(loc, name, opcode, pop, push)


def compare_op(loc: dict, name: str, opcode: int, pop: int = 2, push: int = 1):
    def_op(loc, name, opcode, pop, push)
    loc["hascompare"].append(opcode)
    loc["binaryop"].append(opcode)


def conditional_op(loc: dict, name: str, opcode: int):
    loc["hascompare"].append(opcode)


def const_op(loc: dict, name: str, opcode: int, pop: int = 0, push: int = 1):
    def_op(loc, name, opcode, pop, push)
    loc["hasconst"].append(opcode)


def def_op(
    loc: dict,
    op_name: str,
    opcode: int,
    pop: int = -2,
    push: int = -2,
    fallthrough: bool = True,
):
    loc["opname"][opcode] = op_name
    loc["opmap"][op_name] = opcode
    loc["oppush"][opcode] = push
    loc["oppop"][opcode] = pop
    if not fallthrough:
        loc["nofollow"].append(opcode)


def free_op(loc: dict, name: str, opcode: int, pop: int = 0, push: int = 1):
    def_op(loc, name, opcode, pop, push)
    loc["hasfree"].append(opcode)


def jabs_op(
    loc: dict,
    name: str,
    opcode: int,
    pop: int = 0,
    push: int = 0,
    conditional: bool = False,
    fallthrough: bool = True,
):
    def_op(loc, name, opcode, pop, push, fallthrough=fallthrough)
    loc["hasjabs"].append(opcode)
    if conditional:
        loc["hascondition"].append(opcode)


def jrel_op(loc, name, opcode, pop=0, push=0, conditional=False, fallthrough=True):
    def_op(loc, name, opcode, pop, push)
    loc["hasjrel"].append(opcode)
    if conditional:
        loc["hascondition"].append(opcode)


def local_op(loc, name, op, pop=0, push=1):
    def_op(loc, name, op, pop, push)
    loc["haslocal"].append(op)


def name_op(loc, op_name, op_code, pop=-2, push=-2):
    def_op(loc, op_name, op_code, pop, push)
    loc["hasname"].append(op_code)


def nargs_op(loc, name, op, pop=-2, push=-2, fallthrough=True):
    def_op(loc, name, op, pop, push, fallthrough=fallthrough)
    loc["hasnargs"].append(op)


def rm_op(loc, name, op):
    """Remove an opcode. This is used when basing a new Python release off
    of another one, and there is an opcode that is in the old release
    that was removed in the new release.
    We are pretty aggressive about removing traces of the op.
    """

    # opname is an array, so we need to keep the position in there.
    loc["opname"][op] = "<%s>" % op

    if op in loc["hascompare"]:
        loc["hascompare"].remove(op)
    if op in loc["hascondition"]:
        loc["hascondition"].remove(op)
    if op in loc["hasconst"]:
        loc["hasconst"].remove(op)
    if op in loc["hasfree"]:
        loc["hasfree"].remove(op)
    if op in loc["hasjabs"]:
        loc["hasjabs"].remove(op)
    if op in loc["hasjrel"]:
        loc["hasjrel"].remove(op)
    if op in loc["haslocal"]:
        loc["haslocal"].remove(op)
    if op in loc["hasname"]:
        loc["hasname"].remove(op)
    if op in loc["hasnargs"]:
        loc["hasnargs"].remove(op)
    if op in loc["hasstore"]:
        loc["hasstore"].remove(op)
    if op in loc["hasvargs"]:
        loc["hasvargs"].remove(op)
    if op in loc["nofollow"]:
        loc["nofollow"].remove(op)

    if loc["opmap"][name] != op:
        print(name, loc["opmap"][name], op)
    assert loc["opmap"][name] == op
    del loc["opmap"][name]


def store_op(loc, name, op, pop=0, push=1, is_type="def"):
    if is_type == "name":
        name_op(loc, name, op, pop, push)
    elif is_type == "local":
        local_op(loc, name, op, pop, push)
    elif is_type == "free":
        free_op(loc, name, op, pop, push)
    else:
        assert is_type == "def"
        def_op(loc, name, op, pop, push)
    loc["hasstore"].append(op)


def unary_op(loc, name: str, op, pop=1, push=1):
    loc["unaryop"].append(op)
    def_op(loc, name, op, pop, push)


# This is not in Python. The operand indicates how
# items on the pop from the stack. BUILD_TUPLE_UNPACK
# is line this.
def varargs_op(loc, op_name, op_code, pop=-1, push=1):
    def_op(loc, op_name, op_code, pop, push)
    loc["hasvargs"].append(op_code)


# Some of the convoluted code below reflects some of the
# many Python idiocies over the years.


def finalize_opcodes(loc):
    # Not sure why, but opcode.py address has opcode.EXTENDED_ARG
    # as well as opmap['EXTENDED_ARG']
    loc["EXTENDED_ARG"] = loc["opmap"]["EXTENDED_ARG"]

    # In Python 3.6+ this is 8, but we expect
    # those opcodes to set that
    if "EXTENDED_ARG_SHIFT" not in loc:
        loc["EXTENDED_ARG_SHIFT"] = 16

    loc["ARG_MAX_VALUE"] = (1 << loc["EXTENDED_ARG_SHIFT"]) - 1
    loc["EXTENDED_ARG"] = loc["opmap"]["EXTENDED_ARG"]

    loc["opmap"] = fix_opcode_names(loc["opmap"])

    # Now add in the attributes into the module
    for op in loc["opmap"]:
        loc[op] = loc["opmap"][op]
    loc["JUMP_OPs"] = frozenset(loc["hasjrel"] + loc["hasjabs"])
    loc["NOFOLLOW"] = frozenset(loc["nofollow"])
    opcode_check(loc)
    return


def fix_opcode_names(opmap):
    """
    Python stupidly named some OPCODES with a + which prevents using opcode name
    directly as an attribute, e.g. SLICE+3. So we turn that into SLICE_3 so we
    can then use opcode_23.SLICE_3.  Later Python's fix this.
    """
    return dict([(k.replace("+", "_"), v) for (k, v) in opmap.items()])


def update_pj3(g, loc):
    if loc["version_tuple"] < (3, 11):
        g.update({"PJIF": loc["opmap"]["POP_JUMP_IF_FALSE"]})
        g.update({"PJIT": loc["opmap"]["POP_JUMP_IF_TRUE"]})
    update_sets(loc)


def update_pj2(g, loc):
    g.update({"PJIF": loc["opmap"]["JUMP_IF_FALSE"]})
    g.update({"PJIT": loc["opmap"]["JUMP_IF_TRUE"]})
    update_sets(loc)


def update_sets(loc):
    loc["COMPARE_OPS"] = frozenset(loc["hascompare"])
    loc["CONDITION_OPS"] = frozenset(loc["hascondition"])
    loc["CONST_OPS"] = frozenset(loc["hasconst"])
    loc["FREE_OPS"] = frozenset(loc["hasfree"])
    loc["JREL_OPS"] = frozenset(loc["hasjrel"])
    loc["JABS_OPS"] = frozenset(loc["hasjabs"])
    if loc["python_version"] < (3, 11):
        loc["JUMP_UNCONDITONAL"] = frozenset(
            [loc["opmap"]["JUMP_ABSOLUTE"], loc["opmap"]["JUMP_FORWARD"]]
        )
    else:
        loc["JUMP_UNCONDITONAL"] = frozenset([loc["opmap"]["JUMP_FORWARD"]])
    if PYTHON_VERSION_TRIPLE < (3, 8, 0) and loc["python_version"] < (3, 8):
        loc["LOOP_OPS"] = frozenset([loc["opmap"]["SETUP_LOOP"]])
    else:
        loc["LOOP_OPS"] = frozenset()

    loc["LOCAL_OPS"] = frozenset(loc["haslocal"])
    loc["JUMP_OPS"] = (
        loc["JABS_OPS"] | loc["JREL_OPS"] | loc["LOOP_OPS"] | loc["JUMP_UNCONDITONAL"]
    )
    loc["NAME_OPS"] = frozenset(loc["hasname"])
    loc["NARGS_OPS"] = frozenset(loc["hasnargs"])
    loc["VARGS_OPS"] = frozenset(loc["hasvargs"])
    loc["STORE_OPS"] = frozenset(loc["hasstore"])
    loc["STORE_OPS"] = frozenset(loc["hasstore"])


def extended_format_binary_op(
    opc, instructions, fmt_str: str, reverse_args=False
) -> Tuple[str, Optional[int]]:
    i = 1
    # 3.11+ has CACHE instructions
    while instructions[i].opname == "CACHE":
        i += 1
    stack_arg1 = instructions[i]
    arg1 = None
    if stack_arg1.formatted is not None:
        arg1 = stack_arg1.formatted
    if (
        arg1 is not None
        or stack_arg1.opcode in opc.NAME_OPS | opc.CONST_OPS | opc.LOCAL_OPS
    ):
        if arg1 is None:
            arg1 = instructions[1].argrepr
        arg1_start_offset = instructions[1].start_offset
        if arg1_start_offset is not None:
            for i in range(1, len(instructions)):
                if instructions[i].offset == arg1_start_offset:
                    break
        j = i + 1
        # 3.11+ has CACHE instructions
        while instructions[j].opname == "CACHE":
            j += 1
        if (
            instructions[j].opcode in opc.NAME_OPS | opc.CONST_OPS | opc.LOCAL_OPS
            and instructions[i].opcode in opc.NAME_OPS | opc.CONST_OPS | opc.LOCAL_OPS
        ):
            arg2 = (
                instructions[j].formatted
                if instructions[j].formatted is not None
                else instructions[j].argrepr
            )
            if reverse_args:
                args = (arg1, arg2)
            else:
                args = (arg2, arg1)

            start_offset = instructions[j].start_offset
            return fmt_str % args, start_offset
        elif instructions[j].start_offset is not None:
            start_offset = instructions[j].start_offset
            arg2 = (
                instructions[j].formatted
                if instructions[j].formatted is not None
                else instructions[j].argrepr
            )
            if arg2 == "":
                arg2 = "..."
            return fmt_str % (arg2, arg1), start_offset
        else:
            return fmt_str % ("...", arg1), None
    return "", None


def extended_format_unary_op(
    opc, instructions, fmt_str: str
) -> Tuple[str, Optional[int]]:
    stack_arg = instructions[1]
    if stack_arg.formatted is not None:
        return fmt_str % stack_arg.formatted, instructions[1].start_offset
    if stack_arg.opcode in opc.NAME_OPS | opc.CONST_OPS | opc.LOCAL_OPS:
        return fmt_str % stack_arg.argrepr, None
    return "", None


def extended_format_ATTR(opc, instructions) -> Optional[Tuple[str, int]]:
    if instructions[1].opcode in opc.NAME_OPS | opc.CONST_OPS | opc.LOCAL_OPS:
        return (
            "%s.%s" % (instructions[1].argrepr, instructions[0].argrepr),
            instructions[1].offset,
        )


def extended_format_BINARY_ADD(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s + %s")


def extended_format_BINARY_AND(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s & %s")


def extended_format_BINARY_FLOOR_DIVIDE(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s // %s")


def extended_format_BINARY_LSHIFT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s << %s")


def extended_format_BINARY_MODULO(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s %% %s")


def extended_format_BINARY_MULTIPLY(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s * %s")


def extended_format_BINARY_OR(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s | %s")


def extended_format_BINARY_POWER(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s ** %s")


def extended_format_BINARY_RSHIFT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s >> %s")


def extended_format_BINARY_SUBSCR(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(
        opc,
        instructions,
        "%s[%s]",
    )


def extended_format_BINARY_SUBTRACT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s - %s")


def extended_format_BINARY_TRUE_DIVIDE(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s / %s")


def extended_format_BINARY_XOR(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s ^ %s")


def extended_format_COMPARE_OP(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(
        opc,
        instructions,
        f"%s {instructions[0].argval} %s",
    )


def extended_format_CALL_FUNCTION(opc, instructions) -> Tuple[str, Optional[int]]:
    """call_function_inst should be a "CALL_FUNCTION_KW" instruction. Look in
    `instructions` to see if we can find a method name.  If not we'll
    return None.
    """
    # From opcode description: argc indicates the total number of positional
    # and keyword arguments.  Sometimes the function name is in the stack arg
    # positions back.
    call_function_inst = instructions[0]
    call_opname = call_function_inst.opname
    assert call_opname in (
        "CALL_FUNCTION",
        "CALL_FUNCTION_KW",
        "CALL_FUNCTION_VAR",
        "CALL_FUNCTION_VAR_KW",
    )
    argc = call_function_inst.arg
    (
        name_default,
        pos_args,
    ) = divmod(argc, 256)
    function_pos = pos_args + name_default * 2 + 1
    if call_opname in ("CALL_FUNCTION_VAR", "CALL_FUNCTION_KW"):
        function_pos += 1
    elif call_opname == "CALL_FUNCTION_VAR_KW":
        function_pos += 2
    assert len(instructions) >= function_pos + 1
    i = -1
    for i, inst in enumerate(instructions[1:]):
        if i + 1 == function_pos:
            i += 1
            break
        if inst.is_jump_target:
            i += 1
            break
        # Make sure we are in the same basic block
        # and ... ?
        opcode = inst.opcode
        if inst.optype in ("nargs", "vargs"):
            break
        if inst.opname == "LOAD_ATTR" or inst.optype != "name":
            function_pos += (opc.oppop[opcode] - opc.oppush[opcode]) + 1
        if inst.opname in ("CALL_FUNCTION", "CALL_FUNCTION_KW", "CALL_FUNCTION_VAR"):
            break
        pass

    s = ""
    start_offset = None
    if i == function_pos:
        opname = instructions[function_pos].opname
        if opname in (
            "LOAD_CONST",
            "LOAD_GLOBAL",
            "LOAD_ATTR",
            "LOAD_NAME",
        ):
            if not (
                opname == "LOAD_CONST"
                and isinstance(instructions[function_pos].argval, (int, str))
            ):
                s, start_offset = resolved_attrs(instructions[function_pos:])
                s += ": "
            start_offset = call_function_inst.offset
    s += format_CALL_FUNCTION_pos_name_encoded(call_function_inst.arg)
    return s, start_offset


def extended_format_INPLACE_ADD(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s += %s")


def extended_format_INPLACE_AND(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s &= %s")


def extended_format_INPLACE_FLOOR_DIVIDE(
    opc, instructions
) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s //= %s")


def extended_format_INPLACE_LSHIFT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s <<= %s")


def extended_format_INPLACE_MODULO(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s %%= %s")


def extended_format_INPLACE_MULTIPLY(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s *= %s")


def extended_format_INPLACE_OR(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s |= %s")


def extended_format_INPLACE_POWER(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s **= %s")


def extended_format_INPLACE_TRUE_DIVIDE(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s /= %s")


def extended_format_INPLACE_RSHIFT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s >>= %s")


def extended_format_INPLACE_SUBTRACT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s -= %s")


def extended_format_INPLACE_XOR(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(opc, instructions, "%s ^= %s")


def extended_format_IS_OP(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(
        opc,
        instructions,
        f"%s {format_IS_OP(instructions[0].arg)} %s",
    )


def extended_format_RAISE_VARARGS_older(opc, instructions):
    raise_inst = instructions[0]
    assert raise_inst.opname == "RAISE_VARARGS"
    assert len(instructions) >= 1
    if instructions[1].opcode in opc.NAME_OPS | opc.CONST_OPS:
        s, _ = resolved_attrs(instructions[1:])
        return resolved_attrs(instructions[1:])
    return format_RAISE_VARARGS_older(raise_inst.argval)


def extended_format_RETURN_VALUE(opc, instructions: list) -> Tuple[str, Optional[int]]:
    return extended_format_unary_op(opc, instructions, "return %s")


def extended_format_UNARY_NEGATIVE(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_unary_op(opc, instructions, "-(%s)")


def extended_format_UNARY_NOT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_unary_op(opc, instructions, "not (%s)")


def format_extended_arg(arg):
    return str(arg * (1 << 16))


def format_CALL_FUNCTION_pos_name_encoded(argc):
    """Encoded positional and named args. Used to
    up to about 3.6 where wordcodes are used and
    a different encoding occurs. Pypy36 though
    sticks to this encoded version though."""
    name_default, pos_args = divmod(argc, 256)
    return "%d positional, %d named" % (pos_args, name_default)


def format_IS_OP(arg: int) -> str:
    return "is" if arg == 0 else "is not"


# Up until 3.7
def format_RAISE_VARARGS_older(argc):
    assert 0 <= argc <= 3
    if argc == 0:
        return "reraise"
    elif argc == 1:
        return "exception"
    elif argc == 2:
        return "exception, parameter"
    elif argc == 3:
        return "exception, parameter, traceback"


def opcode_check(loc):
    """When the version of Python we are running happens
    to have the same opcode set as the opcode we are
    importing, we perform checks to make sure our opcode
    set matches exactly.
    """
    if (PYTHON_VERSION_TRIPLE[:2] == loc["python_version"][:2]) and IS_PYPY == loc[
        "is_pypy"
    ]:
        try:
            import dis

            opmap = fix_opcode_names(dis.opmap)
            # print(set(opmap.items()) - set(loc['opmap'].items()))
            # print(set(loc['opmap'].items()) - set(opmap.items()))

            assert all(item in opmap.items() for item in loc["opmap"].items())
            assert all(item in loc["opmap"].items() for item in opmap.items())
        except Exception:
            pass


def resolved_attrs(instructions: list) -> Tuple[str, int]:
    """ """
    # we can probably speed up using the "formatted" field.
    resolved = []
    start_offset = 0
    for inst in instructions:
        name = inst.argrepr
        if name:
            if name[0] == "'" and name[-1] == "'":
                name = name[1:-1]
        else:
            name = ""
        resolved.append(name)
        if inst.opname != "LOAD_ATTR":
            start_offset = inst.offset
            break
    return ".".join(reversed(resolved)), start_offset


def dump_opcodes(opmap):
    """Utility for dumping opcodes"""
    op2name = {}
    for k in opmap.keys():
        op2name[opmap[k]] = k
    for i in sorted(op2name.keys()):
        print("%-3s %s" % (str(i), op2name[i]))


# fmt: off
opcode_arg_fmt_base = opcode_arg_fmt34 = {
    "CALL_FUNCTION": format_CALL_FUNCTION_pos_name_encoded,
    "CALL_FUNCTION_KW": format_CALL_FUNCTION_pos_name_encoded,
    "CALL_FUNCTION_VAR_KW": format_CALL_FUNCTION_pos_name_encoded,
    "EXTENDED_ARG": format_extended_arg,
    "RAISE_VARARGS": format_RAISE_VARARGS_older,
}

# The below are roughly Python 3.3 based. Python 3.11 removes some of these.
opcode_extended_fmt_base = {
    "BINARY_ADD":            extended_format_BINARY_ADD,
    "BINARY_AND":            extended_format_BINARY_AND,
    "BINARY_FLOOR_DIVIDE":   extended_format_BINARY_FLOOR_DIVIDE,
    "BINARY_MODULO":         extended_format_BINARY_MODULO,
    "BINARY_MULTIPLY":       extended_format_BINARY_MULTIPLY,
    "BINARY_RSHIFT":         extended_format_BINARY_RSHIFT,
    "BINARY_SUBSCR":         extended_format_BINARY_SUBSCR,
    "BINARY_SUBTRACT":       extended_format_BINARY_SUBTRACT,
    "BINARY_TRUE_DIVIDE":    extended_format_BINARY_TRUE_DIVIDE,
    "BINARY_LSHIFT":         extended_format_BINARY_LSHIFT,
    "BINARY_OR":             extended_format_BINARY_OR,
    "BINARY_POWER":          extended_format_BINARY_POWER,
    "BINARY_XOR":            extended_format_BINARY_XOR,
    "COMPARE_OP":            extended_format_COMPARE_OP,
    "INPLACE_ADD":           extended_format_INPLACE_ADD,
    "INPLACE_AND":           extended_format_INPLACE_AND,
    "INPLACE_FLOOR_DIVIDE":  extended_format_INPLACE_FLOOR_DIVIDE,
    "INPLACE_LSHIFT":        extended_format_INPLACE_LSHIFT,
    "INPLACE_MODULO":        extended_format_INPLACE_MODULO,
    "INPLACE_MULTIPLY":      extended_format_INPLACE_MULTIPLY,
    "INPLACE_OR":            extended_format_INPLACE_OR,
    "INPLACE_POWER":         extended_format_INPLACE_POWER,
    "INPLACE_RSHIFT":        extended_format_INPLACE_RSHIFT,
    "INPLACE_SUBTRACT":      extended_format_INPLACE_SUBTRACT,
    "INPLACE_TRUE_DIVIDE":   extended_format_INPLACE_TRUE_DIVIDE,
    "INPLACE_XOR":           extended_format_INPLACE_XOR,
    "IS_OP":                 extended_format_IS_OP,
    "LOAD_ATTR":             extended_format_ATTR,
    "RETURN_VALUE":          extended_format_RETURN_VALUE,
    "STORE_ATTR":            extended_format_ATTR,
    "UNARY_NEGATIVE":        extended_format_UNARY_NEGATIVE,
    "UNARY_NOT":             extended_format_UNARY_NOT,
}


# fmt: on
