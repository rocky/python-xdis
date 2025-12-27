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
Common routines for entering and classifying rust opcodes. Inspired by,
limited by, and somewhat compatible with the corresponding
Python opcode.py structures
"""

from xdis.opcodes.base import (
    VARYING_STACK_INT,
    binary_op,
    call_op,
    compare_op,
    conditional_op,
    const_op,
    def_op,
    free_op,
    init_opdata,
    jabs_op,
    jrel_op,
    local_op,
    name_op,
    nargs_op,
    store_op,
    ternary_op,
    unary_op,
    varargs_op,
)

# RustPython compare operation enumerations are different from CPythons
# From bytecode.rs:
#    be intentional with bits so that we can do eval_ord with just a bitwise and
#    bits: | Equal | Greater | Less |

cmp_op = (
    "==",  # 0
    "<",  # 1
    ">",  # 2
    "!=",  # 3
    "==",  # 4
    ">",  # 5
    "<=",  # 5
    ">=",  # 6
)

test_op = (
    "in",  # 0
    "not-in",  # 1
    "is",  # 2
    "is-not",  # 3
    "exception-match",  # 4
)

def init_opdata_rust(loc, from_mod, version_tuple) -> None:
    """Sets up a number of the structures found in Python's
    opcode.py. Python opcode.py routines assign attributes to modules.
    In order to do this in a modular way here, the local dictionary
    for the module is passed.
    """
    init_opdata(loc, from_mod, version_tuple, False)
    loc["cmp_op"] = cmp_op

def inc_opcode(loc):
    loc["_opcode"] += 1

def binary_op_graal(loc: dict, name: str, pop: int = 2, push: int = 1) -> None:
    """
    Put opcode in the class of instructions that are binary operations.
    """
    binary_op(loc, name, loc["_opcode"], pop, push)
    inc_opcode(loc)


def call_op_graal(
    loc: dict, name: str, pop: int = -2, push: int = 1, fallthrough: bool=True
) -> None:
    """
    Put opcode in the class of instructions that perform calls.
    """
    call_op(loc, name, loc["_opcode"], pop, push, fallthrough)
    inc_opcode(loc)


def compare_op_graal(loc: dict, name: str, pop: int = 2, push: int = 1) -> None:
    compare_op(loc, name, loc["_opcode"], pop, push)
    inc_opcode(loc)


def conditional_op_graal(loc: dict, name: str) -> None:
    conditional_op(loc, name, loc["_opcode"])
    inc_opcode(loc)


def const_op_graal(loc: dict, name: str, pop: int = 0, push: int = 1) -> None:
    const_op(loc, name, loc["_opcode"], pop, push)
    inc_opcode(loc)


def def_op_graal(
    loc: dict,
    op_name: str,
    pop: int = -2,
    push: int = -2,
    fallthrough: bool = True,
) -> None:
    def_op(loc, op_name, loc["_opcode"], pop, push, fallthrough)
    inc_opcode(loc)


def free_op_graal(loc: dict, op_name: str, pop: int = 0, push: int = 1) -> None:
    free_op(loc, op_name, loc["_opcode"], pop, push)
    inc_opcode(loc)


def jabs_op_graal(
    loc: dict,
    op_name: str,
    pop: int = 0,
    push: int = 0,
    conditional: bool = False,
    fallthrough: bool = True,
) -> None:
    """
    Put opcode in the class of instructions that can perform an absolute jump.
    """
    jabs_op(loc, op_name, loc["_opcode"], pop, push, conditional, fallthrough)
    inc_opcode(loc)


def jrel_op_graal(loc, op_name: str, pop: int=0, push: int=0, conditional=False, fallthrough=True) -> None:
    """
    Put opcode in the class of instructions that can perform a relative jump.
    """
    jrel_op(loc, op_name, loc["_opcode"], pop, push, conditional, fallthrough)
    inc_opcode(loc)


def local_op_graal(loc, op_name, pop=0, push=1) -> None:
    local_op(loc, op_name, loc["_opcode"], pop, push)
    inc_opcode(loc)


def name_op_graal(loc: dict, op_name, pop=-2, push=-2) -> None:
    """
    Put opcode in the class of instructions that index into the "name" table.
    """
    name_op(loc, op_name, loc["_opcode"], pop, push)
    inc_opcode(loc)


def nargs_op_graal(
    loc, op_name: str, pop: int = -2, push: int = -1, fallthrough=True
) -> None:
    """
    Put opcode in the class of instructions that have a variable number of (or *n*) arguments
    """
    nargs_op(loc, op_name, loc["_opcode"], pop, push, fallthrough)
    inc_opcode(loc)


def store_op_graal(loc: dict, op_name: str, pop=0, push=1, is_type="def") -> None:
    store_op(loc, op_name, loc["_opcode"], pop, push, is_type)
    inc_opcode(loc)


def ternary_op_graal(loc: dict, op_name: str, pop: int = 3, push: int = 1) -> None:
    """
    Put opcode in the class of instructions that are ternary operations.
    """
    ternary_op(loc, op_name, loc["_opcode"], pop, push)
    inc_opcode(loc)


def unary_op_graal(loc, op_name: str, pop: int=1, push: int=1) -> None:
    unary_op(loc, op_name, loc["_opcode"], pop, push)
    inc_opcode(loc)


def varargs_op_graal(loc, op_name, pop: int=-1, push: int=1) -> None:
    varargs_op(loc, op_name, loc["_opcode"], pop, push)
    inc_opcode(loc)



# See RustPython/compiler/core/src/bytecode.rs Instruction
# fmt: off

def make_opcodes(loc: dict, magic_int: int):
    #            OP NAME                        POP PUSH
    #----------------------------------------------------------
    def_op_graal(loc,    "NOP",             0, 0)
    name_op_graal(loc,   "IMPORT_NAME")
    def_op_graal(loc,    "IMPORT_NAMELESS",     0, 1)
    name_op_graal(loc,   "IMPORT_FROM")

    local_op_graal(loc,  "LOAD_FAST")
    name_op_graal(loc,   "LOAD_NAME")
    name_op_graal(loc,   "LOAD_GLOBAL")
    free_op_graal(loc,   "LOAD_DEREF")

    def_op_graal(loc,    "LOAD_CLASS_DEREF")

    store_op_graal(loc,  "STORE_FAST",         1, 0, is_type="local")  # Local variable
    store_op_graal(loc,  "STORE_LOCAL",        0)
    name_op_graal(loc,   "STORE_GLOBAL")                                    # ""
    store_op_graal(loc,  "STORE_DEREF",        1, 0, is_type="free")

    local_op_graal(loc,  "DELETE_FAST",        0, 0) # Local variable number is in operand
    local_op_graal(loc,  "DELETE_LOCAL",       0, 0)
    name_op_graal(loc,   "DELETE_GLOBAL")            # ""
    free_op_graal(loc,   "DELETE_DEREF",       0, 0)
    free_op_graal(loc,   "LOAD_CLOSURE")
    binary_op_graal(loc, "BINARY_SUBSCR")

    def_op_graal(loc,    "STORE_SUBSCR",       0, 0)
    def_op_graal(loc,    "DELETE_SUBSCR",      0, 0)
    name_op_graal(loc,   "STORE_ATTR")               # Index in name list
    name_op_graal(loc,   "DELETE_ATTR")              # ""

    # Operand is in const list
    const_op_graal(loc,  "LOAD_CONST",         0, 1)
    unary_op_graal(loc,  "UNARY_OP",           1, 1)
    binary_op_graal(loc, "BINARY_OP")
    binary_op_graal(loc, "BINARY_OP_INPLACE")
    if magic_int in (12897,):
        name_op_graal(loc,   "LOAD_ATTR")
    compare_op_graal(loc, "TEST_OP",           2, 1)  # test operator
    if magic_int in (24881,):
        def_op_graal(loc,     "CopyItem")
        binary_op_graal(loc, "BINARY_SUBCR")
    compare_op_graal(loc, "COMPARE_OP",        2, 1)  # Comparison operator
    if magic_int in (24881,):
        def_op_graal(loc,     "SWAP",          1, 1)
    def_op_graal(loc,     "POP_TOP",           1, 0)
    if magic_int in (24881,):
        def_op_graal(loc,     "TO_BOOL",       1, 1)
        def_op_graal(loc,     "Unknown1")
    def_op_graal(loc,     "ROT_TWO",           2, 2)
    def_op_graal(loc,     "ROT_THREE",         3, 3)
    def_op_graal(loc,     "DUP_TOP",           0, 1)
    def_op_graal(loc,     "Duplicate2")
    def_op_graal(loc,     "GET_ITER")

    if magic_int in (24881,):
        def_op_graal(loc,     "GetLen")
        def_op_graal(loc,     "CallIntrinsic1")
        def_op_graal(loc,     "CallIntrinsic2")
    def_op_graal(loc,     "Continue")
    def_op_graal(loc,     "Break")

    # In contrast to CPython and others Rust does not seem to use relative jumps,
    # but only absolute jumps.
    jabs_op_graal(loc, "JUMP")    # Number of words to skip

    jabs_op_graal(loc, "POP_JUMP_IF_TRUE")
    jabs_op_graal(loc, "POP_JUMP_IF_FALSE")
    jabs_op_graal(loc, "JUMP_IF_TRUE_OR_POP") # Number of words to skip
    jabs_op_graal(loc, "JUMP_IF_FALSE_OR_POP") # "

    nargs_op_graal(loc, "MAKE_FUNCTION", VARYING_STACK_INT)    # Flags

    if magic_int in (24881,):
        def_op_graal(loc, "SET_FUNCTION_ATTR")

    call_op_graal(loc, "CALL_FUNCTION")
    call_op_graal(loc, "CALL_FUNCTION_KW")
    call_op_graal(loc, "CALL_FUNCTION_EX")  # Flags
    def_op_graal(loc, "LOAD_METHOD")
    call_op_graal(loc, "CALL_METHOD")
    call_op_graal(loc, "CALL_METHOD_KW")
    call_op_graal(loc, "CALL_METHOD_EX")

    jrel_op_graal(loc, "FOR_ITER")
    def_op_graal(loc, "RETURN_VALUE")
    const_op_graal(loc, "RETURN_CONST")
    def_op_graal(loc, "YIELD")
    def_op_graal(loc, "YIELD_FROM")
    if magic_int in (24881,):
        def_op_graal(loc, "RESUME", 0, 0)

    def_op_graal(loc, "SETUP_ANNOTATIONS")
    jrel_op_graal(loc, "SETUP_LOOP", 0,  0, conditional=True)
    def_op_graal(loc, "SETUP_FINALLY", 0, 1)

    if magic_int in (12897,):
        def_op_graal(loc,  "EnterFinally")
        def_op_graal(loc,  "EndFinally")

    if magic_int in (24881,):
        def_op_graal(loc, "GET_YIELD_FROM_ITER")
    def_op_graal(loc,  "SETUP_EXCEPT")
    def_op_graal(loc, "SETUP_WITH")
    def_op_graal(loc,  "SETUP_CLEANUP")
    def_op_graal(loc,  "WithCleanupStart")
    if magic_int in (24881,):
        def_op_graal(loc,  "WithCleanupFinish")

    def_op_graal(loc, "POP_BLOCK")
    def_op_graal(loc, "RAISE")

    if magic_int in (24881,):
        def_op_graal(loc, "LIST_TO_TUPLE")

    if magic_int in (12897,):
        varargs_op_graal(loc, "BUILD_STRING", 1, VARYING_STACK_INT)      # Number of tuple items

    varargs_op_graal(loc, "BUILD_TUPLE", 1, VARYING_STACK_INT)      # Number of tuple items

    if magic_int in (12897,):
        varargs_op_graal(loc, "BUILD_TUPLE_UNPACK", 1, VARYING_STACK_INT)      # Number of tuple items

    if magic_int in (24881,):
        varargs_op_graal(loc, "BUILD_TUPLE_FROM_TUPLES", 1, VARYING_STACK_INT)      # Number of tuple items
        varargs_op_graal(loc, "BUILD_TUPLE_FROM_ITER", 1, VARYING_STACK_INT)      # Number of tuple items
    varargs_op_graal(loc, "BUILD_LIST", VARYING_STACK_INT)       # Number of list items

    if magic_int in (12897,):
        varargs_op_graal(loc, "BUILD_LIST_UNPACK", 1, VARYING_STACK_INT)       # Number of list items
    if magic_int in (24881,):
        varargs_op_graal(loc, "BUILD_LIST_FROM_TUPLES", 1, VARYING_STACK_INT)       # Number of list items
    varargs_op_graal(loc, "BUILD_SET", 1, VARYING_STACK_INT)        # Number of set items
    if magic_int in (12897,):
        varargs_op_graal(loc, "BUILD_SET", 1, VARYING_STACK_INT)        # Number of set items
    if magic_int in (24881,):
        varargs_op_graal(loc, "BUILD_SET_FROM_TUPLES", 1, VARYING_STACK_INT)       # Number of list items
    varargs_op_graal(loc, "BUILD_MAP", 1, VARYING_STACK_INT)        # Number of dict entries
    varargs_op_graal(loc, "BUILD_MAP_FOR_CALL", 1, VARYING_STACK_INT)        # Number of dict entries
    varargs_op_graal(loc, "DICT_UPDATE")        # Number of dict entries
    def_op_graal(loc, "BUILD_SLICE")
    def_op_graal(loc, "LIST_APPEND")
    def_op_graal(loc, "SET_ADD")
    def_op_graal(loc, "MAP_ADD")
    def_op_graal(loc, "PRINT_EXPR")
    def_op_graal(loc, "LOAD_BUILD_CLASS")
    varargs_op_graal(loc, "UNPACK_SEQUENCE", 1, VARYING_STACK_INT)   # Number of tuple items
    def_op_graal(loc, "UNPACK_EX", VARYING_STACK_INT, VARYING_STACK_INT)
    def_op_graal(loc, "FORMAT_VALUE", VARYING_STACK_INT, VARYING_STACK_INT)
    def_op_graal(loc, "POP_EXCEPT")
    def_op_graal(loc, "REVERSE")
    def_op_graal(loc, "GET_AWAITABLE")

    if magic_int in (12897,):
        def_op_graal(loc, "BeforeAsyncWith")
        def_op_graal(loc, "SetupAsyncWith")
        def_op_graal(loc, "GET_AITER", 0, 1)
        def_op_graal(loc, "GET_ANEXT")
        def_op_graal(loc, "EndAsyncFor")

    if magic_int in (24881,):
        def_op_graal(loc, "END_ASYNC_FOR")
        def_op_graal(loc, "MATCH_MAPPING")
        def_op_graal(loc, "MATCH_SEQUENCE")
        def_op_graal(loc, "MATCH_CLASS")

    def_op_graal(loc, "EXTENDED_ARG")

    if magic_int in (12897,):
        def_op_graal(loc, "TypeVar")
        def_op_graal(loc, "TypeVarWithBound")
        def_op_graal(loc, "TypeVarWithConstraint")
        def_op_graal(loc, "TypeAlias")
