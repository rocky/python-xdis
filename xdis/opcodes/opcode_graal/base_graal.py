# (C) Copyright 2025 by Rocky Bernstein
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
Common routines for entering and classifying opcodes. Inspired by,
limited by, and somewhat compatible with the corresponding
Python opcode.py structures
"""


def get_optype_graal(opcode: int, opc) -> str:
    """Helper to determine what class of instructions ``opcode`` is in.
    Return is a string in:
       compare, const, free, jabs, jrel, local, name, nargs, or ??
    """
    if opcode in opc.BINARY_OPS:
        return "binary"
    elif opcode in opc.COLLECTION_OPS:
        return "collection"
    elif opcode in opc.CONST_OPS:
        return "const"
    elif opcode in opc.COMPARE_OPS:
        return "compare"
    elif opcode in opc.ENCODED_ARG_OPS:
        return "encoded_arg"
    elif opcode in opc.FREE_OPS:
        return "free"
    elif opcode in opc.JABS_OPS:
        return "jabs"
    elif opcode in opc.JREL_OPS:
        return "jrel"
    # elif opcode in opc.LOCAL_OPS:
    #     return "local"
    elif opcode in opc.NAME_OPS:
        return "name"
    elif opcode in opc.NARGS_OPS:
        return "nargs"
    # This has to come after NARGS_OPS. Some are in both?
    elif opcode in opc.VARGS_OPS:
        return "vargs"
    elif opcode in opc.UNARY_OPS:
        return "unary"

    return "??"


def findlabels(bytecode, opc):
    """Returns a list of instruction offsets in the supplied bytecode
    which are the targets of some sort of jump instruction.
    """
    offset = 0
    n = len(bytecode)
    offsets = []
    while offset < n:
        opcode = bytecode[offset]
        optype = get_optype_graal(opcode, opc)

        # opname = opc.opname[opcode]
        # print(
        #     f"offset: {offset} {hex(opcode)} {opname} optype: {optype}"
        # )

        jump_offset = -1
        if optype == "jrel":
            arg = bytecode[offset + 1]
            if opcode == opc.opmap["JUMP_BACKWARD"]:
                jump_offset = offset - arg
            else:
                jump_offset = offset + arg
        # elif op in opc.JABS_OPS:
        #     jump_offset = arg
        if jump_offset >= 0:
            if jump_offset not in offsets:
                offsets.append(jump_offset)
        inst_size = opc.arg_counts[opcode] + 1
        offset += inst_size

    return offsets


# FIXME: Use an enumeration? Or tuple?
BINARY_OPS = {
    0: "ADD",
    1: "INPLACE_ADD",
    2: "SUB",
    3: "INPLACE_SUB",
    4: "MUL",
    5: "INPLACE_MUL",
    6: "FLOORDIV",
    7: "INPLACE_FLOORDIV",
    8: "TRUEDIV",
    9: "INPLACE_TRUEDIV",
    10: "MOD",
    11: "INPLACE_MOD",
    12: "EQ",
    13: "NE",
    14: "LT",
    15: "LE",
    16: "GT",
    17: "GE",
    18: "LSHIFT",
    19: "INPLACE_LSHIFT",
    20: "RSHIFT",
    21: "INPLACE_RSHIFT",
    22: "AND",
    23: "INPLACE_AND",
    24: "OR",
    25: "INPLACE_OR",
    26: "XOR",
    27: "INPLACE_XOR",
    28: "POW",
    29: "INPLACE_POW",
    30: "IN",
    31: "IS",
    32: "MATMUL",
    33: "INPLACE_MATMUL",
}

COLLECTION_KIND_SHIFT = 5
COLLECTION_KIND_MASK = (1 << COLLECTION_KIND_SHIFT) - 1
COLLECTION_KIND = {
    0b001: "list",
    0b010: "tuple",  # Probably need to use a mask
    0b011: "set",
    0b100: "dict",
    0b101: "PKeyword",
    0b110: "Object",
    # #
    # 99: "tuple",  # probably need to use a mask
    # 160: "object",
    # 192: "object",
}

COLLECTION_KIND_ELEMENT = {
    0: "",
    1: "int",
    2: "long",
    3: "boolean",
    4: "double",
    5: "object"
}


UNARY_OPS = {
    0: "NOT",
    31: "IS",
    30: "IN",
}

def collection_to_str(collection_value: int) -> str:
    kind = collection_value >> COLLECTION_KIND_SHIFT
    kind_str = COLLECTION_KIND.get(kind, "??")
    element_type = collection_value & COLLECTION_KIND_MASK
    element_str = COLLECTION_KIND_ELEMENT.get(element_type, "??")
    return f"{kind_str}[{element_str}]"

def binary_op_graal(
    loc: dict,
    name: str,
    opcode: int,
    pop: int = 2,
    push: int = 1,
    arg_count: int = 1,
) -> None:
    """
    Put opcode in the class of instructions that are binary operations.
    """
    loc["binaryop"].add(opcode)
    def_op_graal(loc, name, opcode, pop, push, arg_count)


def def_op_graal(
    loc: dict,
    op_name: str,
    opcode: int,
    pop: int = -2,
    push: int = -2,
    arg_count: int = 0,
    fallthrough: bool = True,
) -> None:
    loc["opname"][opcode] = op_name
    loc["opmap"][op_name] = opcode
    loc["oppush"][opcode] = push
    loc["oppop"][opcode] = pop
    if not fallthrough:
        loc["nofollow"].append(opcode)
    loc["arg_counts"][opcode] = arg_count
    loc["operator_set"] = frozenset(loc["nullaryop"] | loc["unaryop"] | loc["binaryop"])


def call_op_graal(
    loc: dict,
    name: str,
    opcode: int,
    pop: int = -2,
    push: int = 1,
    fallthrough: bool = True,
) -> None:
    """
    Put opcode in the class of instructions that perform calls.
    """
    loc["callop"].add(opcode)
    nargs_op_graal(loc, name, opcode, pop, push, fallthrough)


def collection_op_graal(
    loc: dict, name: str, opcode: int, pop: int = 0, push: int = 1, arg_count: int = 1
) -> None:
    def_op_graal(loc, name, opcode, pop, push, arg_count)
    loc["collectionop"].add(opcode)


def const_op_graal(
    loc: dict, name: str, opcode: int, pop: int = 0, push: int = 1, arg_count: int = 1
) -> None:
    def_op_graal(loc, name, opcode, pop, push, arg_count)
    loc["hasconst"].append(opcode)
    loc["nullaryop"].add(opcode)


def free_op_graal(
    loc: dict, name: str, opcode: int, pop: int = 0, push: int = 1, arg_count: int = 1
) -> None:
    def_op_graal(loc, name, opcode, pop, push, arg_count)
    loc["hasfree"].append(opcode)


def jrel_op_graal(
    loc,
    name: str,
    opcode: int,
    pop: int = 0,
    push: int = 0,
    conditional=False,
    fallthrough=True,
    arg_count: int = 1,
) -> None:
    """
    Put opcode in the class of instructions that can perform a relative jump.
    """
    def_op_graal(loc, name, opcode, pop, push, arg_count)
    loc["hasjrel"].append(opcode)
    if conditional:
        loc["hascondition"].append(opcode)


def name_op_graal(
    loc: dict, op_name, opcode: int, pop=-2, push=-2, arg_count: int = 1
) -> None:
    """
    Put opcode in the class of instructions that index into the "name" table.
    """
    def_op_graal(loc, op_name, opcode, pop, push, arg_count)
    loc["hasname"].append(opcode)
    loc["nullaryop"].add(opcode)


def nargs_op_graal(
    loc,
    name: str,
    opcode: int,
    pop: int = -2,
    push: int = -1,
    arg_count: int = 0,
    fallthrough=True,
) -> None:
    """
    Put opcode in the class of instructions that have a variable number of (or *n*) arguments
    """
    def_op_graal(
        loc, name, opcode, pop, push, arg_count=arg_count, fallthrough=fallthrough
    )
    loc["hasnargs"].append(opcode)


def store_op_graal(
    loc: dict, name: str, op, pop=0, push=1, is_type="def", arg_count: int = 1
) -> None:
    if is_type == "name":
        name_op_graal(loc, name, op, pop, push, arg_count)
        loc["nullaryop"].remove(op)
    # elif is_type == "local":
    #     local_op(loc, name, op, pop, push)
    #     loc["nullaryop"].remove(op)
    # elif is_type == "free":
    #     free_op(loc, name, op, pop, push)
    else:
        assert is_type == "def"
        def_op_graal(loc, name, op, pop, push)
    loc["hasstore"].append(op)


def unary_op_graal(
    loc: dict,
    name: str,
    opcode: int,
    pop: int = 1,
    push: int = 1,
    arg_count: int = 1,
) -> None:
    """
    Put opcode in the class of instructions that are binary operations.
    """
    loc["unaryop"].add(opcode)
    def_op_graal(loc, name, opcode, pop, push, arg_count)


def update_sets(loc) -> None:
    """
    Updates various category sets all opcode have been defined.
    """

    loc["BINARY_OPS"] = frozenset(loc["binaryop"])
    loc["COLLECTION_OPS"] = frozenset(loc["collectionop"])
    loc["COMPARE_OPS"] = frozenset(loc["hascompare"])
    loc["CONDITION_OPS"] = frozenset(loc["hascondition"])
    loc["CONST_OPS"] = frozenset(loc["hasconst"])
    loc["EXTENDED_ARG"] = loc["opmap"]["EXTENDED_ARG"]
    loc["ENCODED_ARG_OPS"] = frozenset(loc["encoded_arg"])
    loc["FREE_OPS"] = frozenset(loc["hasfree"])
    loc["JREL_OPS"] = frozenset(loc["hasjrel"])
    loc["JABS_OPS"] = frozenset(loc["hasjabs"])
    loc["NAME_OPS"] = frozenset(loc["hasname"])
    loc["NARGS_OPS"] = frozenset(loc["hasnargs"])
    loc["VARGS_OPS"] = frozenset(loc["hasvargs"])
    loc["UNARY_OPS"] = frozenset(loc["unaryop"])
    loc["findlabels"] = findlabels
    loc["get_jump_targets"] = findlabels
