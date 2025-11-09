# (C) 2024-2025 by Rocky Bernstein
"""
Python Graal 3.8 (graal-23.0.0) bytecode opcodes

See com.oracle.graal.python/src/com/oracle/graal/python/compiler/OpCodes.java
"""

from typing import Dict, Set

from xdis.opcodes.base import init_opdata
from xdis.version_info import PythonImplementation

loc = opc = locals()
python_implementation = PythonImplementation("Graal")
version_tuple = (3, 8, 5)

init_opdata(opc, None, None)

arg_counts: Dict[int, int] = {}

# opcodes that perform some sort of call
callop: Set[int] = set([])

loc = locals()


## FIXME put this common define code in a graal_base.
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
    arg_counts[opcode] = arg_count


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


def update_sets(loc) -> None:
    """
    Updates various category sets all opcode have been defined.
    """

    loc["COMPARE_OPS"] = frozenset(loc["hascompare"])
    loc["CONDITION_OPS"] = frozenset(loc["hascondition"])
    loc["CONST_OPS"] = frozenset(loc["hasconst"])
    loc["ENCODED_ARG_OPS"] = frozenset(loc["encoded_arg"])
    loc["FREE_OPS"] = frozenset(loc["hasfree"])
    loc["JREL_OPS"] = frozenset(loc["hasjrel"])
    loc["JABS_OPS"] = frozenset(loc["hasjabs"])
    loc["NAME_OPS"] = frozenset(loc["hasname"])
    loc["NARGS_OPS"] = frozenset(loc["hasnargs"])
    loc["VARGS_OPS"] = frozenset(loc["hasvargs"])


# Instruction opcodes for compiled code
# Blank lines correspond to available opcodes

# If the POP field is -1 and the opcode is a var args operation
# then the operand holds the size.
#
# If the POP field is negative and the opcode is a nargs operation
# then pop the operand amount plus the negative of the POP amount.

# Pop a single item from the stack.
def_op_graal(opc, "POP_TOP", 0x0, 0, 1, 0)

# Exchange two top stack items.
def_op_graal(opc, "ROT_TWO", 0x1, 0, 2, 2)

# Exchange three top stack items. [a, b, c] (a is top) becomes [b, c, a]
def_op_graal(opc, "ROT_THREE", 0x2, 0, 3, 3)

# Exchange N top stack items. [a, b, c, ..., N] (a is top) becomes [b, c, ..., N, a].
def_op_graal(
    opc, "ROT_N", 0x3, -1, -1
)  #  (oparg, followingArgs, withJump) -> oparg, (oparg, followingArgs, withJump) -> oparg)

# Duplicates the top stack item.
def_op_graal(opc, "DUP_TOP", 0x4, 0, 1, 2)

# Does nothing. Might still be useful to maintain a line number.
def_op_graal(opc, "NOP", 0x5, 0, 0, 0)

# Performs a unary operation specified by the immediate operand. It
# has to be the ordinal of one of {@link UnaryOps} constants.
#  Pops: operand
#  Pushes: result
def_op_graal(opc, "UNARY_OP", 0x6, 1, 1, 1)

# Performs a binary operation specified by the immediate operand. It has to be the ordinal of
# one of {@link BinaryOps} constants.
#   Pops: right operand, then left operand
#   Pushes: result
def_op_graal(opc, "BINARY_OP", 0x7, 1, 2, 1)

# Performs subscript get operation - {@code a[b]}.
#   Pops: {@code b}, then {@code a}
#   Pushes: result
def_op_graal(opc, "BINARY_SUBSCR", 0x8, 0, 2, 1)

# Performs subscript set operation - {@code a[b] = c}.
#   Pops: {@code b}, then {@code a}, then {@code c}
def_op_graal(opc, "STORE_SUBSCR", 0x9, 0, 3, 0)

# Performs subscript delete operation - {@code del a[b]}.
#   Pops: {@code b}, then {@code a}
#
def_op_graal(opc, "DELETE_SUBSCR", 0xA, 0, 2, 0)

# Gets an iterator of an object.
#   Pops: object
#   Pushes: iterator
def_op_graal(opc, "GET_ITER", 0xB, 0, 1, 1)

# Gets an iterator of an object, does nothing for a generator iterator or a coroutine.
#   Pops: object
#   Pushes: iterator
def_op_graal(opc, "GET_YIELD_FROM_ITER", 0xC, 0, 1, 1)

# Gets an awaitable of an object.
#   Pops: object
#   Pushes: awaitable
def_op_graal(opc, "GET_AWAITABLE", 0xD, 0, 1, 1)

# Pushes: {@code __build_class__} builtin
# def_op_graal(opc, "LOAD_BUILD_CLASS", 0xe, 0, 0, 1)
def_op_graal(opc, "LOAD_BUILD_CLASS", 0x12, 0, 0, 1)  # This is wrong

# Pushes: {@code AssertionError} builtin exception type
def_op_graal(opc, "LOAD_ASSERTION_ERROR", 0x11, 0, 0, 1)

# Returns the value to the caller. In generators, performs generator return.
#   Pops: return value
# def_op_graal(opc, "RETURN_VALUE", 0x10, 0, 1, 0)
def_op_graal(opc, "RETURN_VALUE", 0xE, 0, 1, 0)  # This is observed
#
# Reads a name from locals dict, globals or builtins determined by the
# immediate operand which indexes the names array ({@code co_names}).
#  Pushes: read object
name_op_graal(opc, "LOAD_NAME", 0x0F, 1, 0, 0)
opc["nullaryloadop"].add(19)


# Writes the stack top into a name in locals dict or globals
# determined by the immediate operand which indexes the names array
# ({@code co_names}).
#  Pops: object to be written
store_op_graal(opc, "STORE_NAME", 0x10, 1, 1, "name", 1)
# observed

# Deletes the name in locals dict or globals determined by the
# immediate operand which indexes the names array ({@code co_names}).
name_op_graal(opc, "DELETE_NAME", 0x13, 1, 0, 1)

# Reads an attribute - {@code a.b}. {@code b} is determined by the immediate operand which
# indexes the names array ({@code co_names}).
#  Pops: {@code a}
#  Pushes: read attribute
name_op_graal(opc, "LOAD_ATTR", 0x14, 1, 1, 1)
#
# Reads method on an object. The method name is determined by the
# first immediate operand which indexes the names array ({@code
# co_names}).
#   Pushes: read method
name_op_graal(opc, "LOAD_METHOD", 0x15, 1, 1, 2)

# Writes an attribute - {@code a.b = c}. {@code b} is determined by
# the immediate operand which indexes the names array ({@code
# co_names}).
#  Pops: {@code c}, then {@code a}
name_op_graal(opc, "STORE_ATTR", 0x16, 1, 2, 0)

# Deletes an attribute - {@code del a.b}. {@code b} is determined by
# the immediate operand which indexes the names array ({@code
# co_names}).
#  Pops: {@code a}
name_op_graal(opc, "DELETE_ATTR", 0x17, 1, 1, 0)

# Reads a global variable. The name is determined by the immediate
# operand which indexes the names array ({@code co_names}).
#   Pushes: read object
name_op_graal(opc, "LOAD_GLOBAL", 0x18, 1, 0, 1)
opc["nullaryloadop"].add(26)


# Writes a global variable. The name is determined by the immediate
# operand which indexes the names array ({@code co_names}).
#  Pops: value to be written
name_op_graal(opc, "STORE_GLOBAL", 0x19, 1, 1, 0)

# Deletes a global variable. The name is determined by the immediate operand which indexes the
# names array ({@code co_names}).
name_op_graal(opc, "DELETE_GLOBAL", 0x1A, 1, 0, 0)

# Reads a constant object from constants array ({@code co_consts}). Performs no conversion.
#   Pushes: read constant
const_op_graal(opc, "LOAD_CONST", 0x1B, 1, 0, 1)
opc["nullaryloadop"].add(29)

# Reads a local variable determined by the immediate operand which indexes a stack slot and a
# variable name in varnames array ({@code co_varnames}).
#   Pushes: read value
def_op_graal(opc, "LOAD_FAST", 0x1C, 1, 0, 1)
opc["nullaryloadop"].add(30)


# Writes a local variable determined by the immediate operand which indexes a stack slot and a
# variable name in varnames array ({@code co_varnames}).
#  Pops: value to be written
def_op_graal(opc, "STORE_FAST", 0x1D, 1, 1, 0)

# Deletes a local variable determined by the immediate operand which indexes a stack slot and a
# variable name in varnames array ({@code co_varnames}).
def_op_graal(opc, "DELETE_FAST", 0x1E, 1, 0, 0)

# Reads a local cell variable determined by the immediate operand
# which indexes a stack slot after celloffset and a variable name in
# cellvars or freevars array ({@code co_cellvars}, {@code
# co_freevars}).
#  Pushes: cell contents
free_op_graal(opc, "LOAD_DEREF", 0x1F, 1, 0, 1)

# Writes a local cell variable determined by the immediate operand
# which indexes a stack slot after celloffset and a variable name in
# cellvars or freevars array ({@code co_cellvars}, {@code
# co_freevars}).
#  Pops: value to be written into the cell contents
# FIXME: this should be tagged as both a "free" and as "store" op.
free_op_graal(opc, "STORE_DEREF", 0x20, 1, 1, 0)

# Deletes a local cell variable determined by the immediate operand
# which indexes a stack slot after celloffset and a variable name in
# cellvars or freevars array ({@code co_cellvars}, {@code
# co_freevars}). Note that it doesn't delete the cell, just its
# contents.
free_op_graal(opc, "DELETE_DEREF", 0x21, 1, 0, 0)

# TODO not implemented
def_op_graal(opc, "LOAD_CLASSDEREF", 0x22, 1, 0, 1)

# Raises an exception. If the immediate operand is 0, it pops nothing
# and is equivalent to {@code raise} without arguments. If the
# immediate operand is 1, it is equivalent to {@code raise e} and it
# pops {@code e}. If the immediate operand is 2, it is equivalent to
# {@code raise e from c} and it pops {@code c}, then {@code e}. Other
# immediate operand values are illegal.
def_op_graal(
    opc, "RAISE_VARARGS", 0x23, 1
)  # , (oparg, followingArgs, withJump) -> oparg, 0)

# Creates a slice object. If the immediate argument is 2, it is equivalent to a slice
# {@code a:b}. It pops {@code b}, then {@code a}. If the immediate argument is 3, it is
# equivalent to a slice {@code a:b:c}. It pops {@code c}, then {@code b}, then {@code a}. Other
# immediate operand values are illegal.
#   Pushes: the created slice object
def_op_graal(
    opc, "BUILD_SLICE", 0x24, 1
)  # (oparg, followingArgs, withJump) -> oparg, 1)

# Formats a value. If the immediate argument contains flag {@link FormatOptions#FVS_HAVE_SPEC},
# it is equivalent to {@code format(conv(v), spec)}. It pops {@code spec}, then {@code v}.
# Otherwise, it is equivalent to {@code format(conv(v), None)}. It pops {@code v}. {@code conv}
# is determined by the immediate operand which contains one of the {@code FVC} options in
# {@link FormatOptions}.
#  Pushes: the formatted value
def_op_graal(
    opc, "FORMAT_VALUE", 0x25, 1
)  # , (oparg, followingArgs, withJump) -> (oparg & FormatOptions.FVS_MASK) == FormatOptions.FVS_HAVE_SPEC ? 2 : 1, 1)

# Extends the immediate operand of the following instruction by its own operand shifted left by
# a byte.
def_op_graal(opc, "EXTENDED_ARG", 0x26, 1, 0, 0)

# Imports a module by name determined by the immediate operand which
# indexes the names array ({@code co_names}).
#  Pops: fromlist (must be a constant {@code TruffleString[]}), then level (must be {@code int})
#  Pushes: imported module
name_op_graal(opc, "IMPORT_NAME", 0x27, 1, 2, 1)
opc["nullaryloadop"].add(41)


# Imports a name from a module. The name determined by the immediate operand which indexes the
# names array ({@code co_names}).
#  Pops: module object
#   Pushes: module object, imported object
name_op_graal(opc, "IMPORT_FROM", 0x28, 1, 1, 2)

# Imports all names from a module of name determined by the immediate operand which indexes the
# names array ({@code co_names}). The imported names are written to locals dict (can only be
# invoked on module level).
#   Pops: level (must be {@code int})
def_op_graal(opc, "IMPORT_STAR", 0x29, 1, 1, 0)

# Prints the top of the stack. Used by "single" parsing mode to echo
# expressions.
#   Pops: the value to print
def_op_graal(opc, "PRINT_EXPR", 0x2A, 0, 1, 0)

# Creates annotations dict in locals
def_op_graal(opc, "SETUP_ANNOTATIONS", 0x2B, 0, 0, 0)

# Determines if a python object is a sequence.
def_op_graal(opc, "MATCH_SEQUENCE", 0x2C, 0, 0, 1)

# Determines if a Python object is a mapping.
def_op_graal(opc, "MATCH_MAPPING", 0x2D, 0, 0, 1)

# Determines if a Python object is of a particular type.
def_op_graal(opc, "MATCH_CLASS", 0x2E, 1, 3, 2)

# Matches the keys (stack top) in a dict (stack second). On successful
# match pushes the values and True, otherwise None and False.
def_op_graal(opc, "MATCH_KEYS", 0x2F, 0, 2, 4)

# Creates a copy of a dict (stack second) without elements matching a
# tuple of keys (stack top).
def_op_graal(opc, "COPY_DICT_WITHOUT_KEYS", 0x30, 0, 1, 1)

# Retrieves the length of a Python object and stores it on top.
def_op_graal(opc, "GET_LEN", 0x31, 0, 0, 1)

# -------------------------------------
# load bytecodes for special constants
# -------------------------------------

def_op_graal(opc, "LOAD_NONE", 0x32, 0, 0, 1)
opc["nullaryloadop"].add(0x32)

def_op_graal(opc, "LOAD_ELLIPSIS", 0x33, 0, 0, 1)
def_op_graal(opc, "LOAD_TRUE", 0x34, 0, 0, 1)
opc["nullaryloadop"].add(0x32)

def_op_graal(opc, "LOAD_FALSE", 0x35, 0, 0, 1)
opc["nullaryloadop"].add(0x33)

# Loads signed byte from immediate operand.
#
# def_op_graal(opc, "LOAD_BYTE", 0x36, 1, 0, 1)
def_op_graal(opc, "LOAD_BYTE", 0x5F, 1, 0, 1)  # this is observed
#
# Loads {@code int} from primitiveConstants array indexed by the immediate operand.
#
def_op_graal(opc, "LOAD_INT", 0x37, 1, 0, 1)
#
# Loads {@code long} from primitiveConstants array indexed by the immediate operand.
#
def_op_graal(opc, "LOAD_LONG", 0x38, 1, 0, 1)
#
# Loads {@code double} from primitiveConstants array indexed by the immediate operand
# (converted from long).
#
def_op_graal(opc, "LOAD_DOUBLE", 59, 1, 0, 1)
#
# Creates a {@link PInt} from a {@link BigInteger} in constants array indexed by the immediate
# operand.
#
const_op_graal(opc, "LOAD_BIGINT", 60, 1, 0, 1)
#
# Currently the same as {@link #LOAD_CONST}.
#
const_op_graal(opc, "LOAD_STRING", 61, 0, 1)

#
# Creates python {@code bytes} from a {@code byte[]} array in constants array indexed by the
# immediate operand.
#
const_op_graal(opc, "LOAD_BYTES", 62, 0, 1)
#
# Creates python {@code complex} from a {@code double[]} array of size 2 in constants array
# indexed by the immediate operand.
#
def_op_graal(opc, "LOAD_COMPLEX", 63, 1, 0, 1)

# Creates a collection out of a Java array in constants array indexed by the immediate operand.
# The second immediate operand determines the array type and kind, using values from {@link
# CollectionBits}. The only allowed kinds are list and tuple.
#
const_op_graal(opc, "LOAD_CONST_COLLECTION", 64, 2, 0, 1)

# -------
# calling
# -------

#
# Calls method on an object using an array as args. The receiver is taken from the first
# element of the array. The method name is determined by the immediate operand which indexes
# the names array ({@code co_names}).
#
# Pops: args ({@code Object[]} of size >= 1)
#
# Pushes: call result
#
call_op_graal(opc, "CALL_METHOD_VARARGS", 65, 1, 1, 1)
#
# Calls method on an object using a number of stack args determined by the first immediate
# operand.
#
# Pops: multiple arguments depending on the first immediate operand, then the method and the
# receiver
#
# Pushes: call result
#
call_op_graal(
    opc, "CALL_METHOD", 66, 1
)  # , (oparg, followingArgs, withJump) -> oparg + 2, 1)
#
# Calls a callable using a number of stack args determined by the immediate operand.
#
# Pops: multiple arguments depending on the immediate operand (0 - 4), then the callable
#
# Pushes: call result
#
call_op_graal(
    opc, "CALL_FUNCTION", 0x39, 2, 1, 1
)  # , (oparg, followingArgs, withJump) -> oparg + 1, 1)
#
# Calls a comprehension function with a single iterator argument. Comprehension functions have
# to always have the same call target at given calls site. The instruction makes use of this
# fact and bypasses function object inline caching which would otherwise slow down warmup since
# comprehensions functions are always created anew and thus the cache would always miss.
#
# Pops: iterator, then the function
#
# Pushes: call result
#
call_op_graal(opc, "CALL_COMPREHENSION", 68, 0, 2, 1)
#
# Calls a callable using an arguments array and keywords array.
#
# Pops: keyword args ({@code PKeyword[]}), then args ({@code Object[]}), then callable
#
# Pushes: call result
#
call_op_graal(opc, "CALL_FUNCTION_KW", 69, 0, 3, 1)
#
# Calls a callable using an arguments array. No keywords are passed.
#
# Pops: args ({@code Object[]}), then callable
#
# Pushes: call result
#
def_op_graal(opc, "CALL_FUNCTION_VARARGS", 70, 0, 2, 1)

# ----------------------
# destructuring bytecodes
# ----------------------

# Unpacks an iterable into multiple stack items.
#
# Pops: iterable
#
# Pushed: unpacked items, the count is determined by the immediate operand
#
def_op_graal(
    opc, "UNPACK_SEQUENCE", 71, 1, 1
)  # , (oparg, followingArgs, withJump) -> oparg)

# Unpacks an iterable into multiple stack items with a star item that gets the rest. The first
# immediate operand determines the count before the star item, the second determines the count
# after.
#
# Pops: iterable
#
# Pushed: unpacked items (count = first operand), star item, unpacked items (count = second
# operand)
#
def_op_graal(
    opc, "UNPACK_EX", 73, 2, 1
)  #  (oparg, followingArgs, withJump) -> oparg + 1 + Byte.toUnsignedInt(followingArgs[0]))

# jumps

#
# Get next value from an iterator. If the iterable is exhausted, jump forward by the offset in
# the immediate argument.
#
# Pops: iterator
#
# Pushes (only if not jumping): the iterator, then the next value
#
def_op_graal(
    opc, "FOR_ITER", 74, 1, 1
)  # (, (oparg, followingArgs, withJump) -> withJump ? 0 : 2)
#
# Jump forward by the offset in the immediate operand.
#
def_op_graal(opc, "JUMP_FORWARD", 75, 1, 0, 0)

# Jump backward by the offset in the immediate operand. May trigger OSR compilation.
#
def_op_graal(opc, "JUMP_BACKWARD", 76, 1, 0, 0)

# Jump forward by the offset in the immediate operand if the top of the stack is false (in
# Python sense).
#
# Pops (if not jumping): top of the stack
def_op_graal(
    opc, "JUMP_IF_FALSE_OR_POP", 77, 3
)  # , (oparg, followingArgs, withJump) -> withJump ? 0 : 1, 0)

# Jump forward by the offset in the immediate operand if the top of the stack is true (in
# Python sense).
#
# Pops (if not jumping): top of the stack
#
def_op_graal(
    opc, "JUMP_IF_TRUE_OR_POP", 78, 3
)  # , (oparg, followingArgs, withJump) -> withJump ? 0 : 1, 0)
#
# Jump forward by the offset in the immediate operand if the top of the stack is false (in
# Python sense).
#
# Pops: top of the stack
#
def_op_graal(opc, "POP_AND_JUMP_IF_FALSE", 79, 3, 1, 0)
#
# Jump forward by the offset in the immediate operand if the top of the stack is true (in
# Python sense).
#
# Pops: top of the stack
#
def_op_graal(opc, "POP_AND_JUMP_IF_TRUE", 80, 3, 1, 0)


# ----------------
# making callables
# ----------------

#
# Like {@link #LOAD_DEREF}, but loads the cell itself, not the contents.
#
# Pushes: the cell object
#
free_op_graal(opc, "LOAD_CLOSURE", 81, 1, 0, 1)
#
# Reduces multiple stack items into an array of cell objects.
#
# Pops: multiple cells (count = immediate argument)
#
# Pushes: cell object array ({@code PCell[]})
#
def_op_graal(
    opc, "CLOSURE_FROM_STACK", 82, 1
)  # , (oparg, followingArgs, withJump) -> oparg, 1)
#
# Creates a function object. The first immediate argument is an index to the constants array
# that determines the {@link CodeUnit} object that will provide the function's code.
#
# Pops: The second immediate arguments contains flags (defined in {@link CodeUnit}) that
# determine whether it will need to pop (in this order): closure, annotations, keyword only
# defaults, defaults.
#
# Pushes: created function
#
nargs_op_graal(
    opc, "MAKE_FUNCTION", 0x47, 1, 2, 2
)  # , (oparg, followingArgs, withJump) -> Integer.bitCount(followingArgs[0]), 1)
# observed.

# -------------------
# collection literals
# -------------------

#
# Creates a collection from multiple elements from the stack. Collection type is determined by
# {@link CollectionBits} in immediate operand.
#
# Pops: items for the collection (count = immediate argument)
#
# Pushes: new collection
#
def_op_graal(
    opc, "COLLECTION_FROM_STACK", 84, 1
)  # , (oparg, followingArgs, withJump) -> CollectionBits.elementCount(oparg), 1)
#
# Add multiple elements from the stack to the collection below them. Collection type is
# determined by {@link CollectionBits} in immediate operand. Tuple is not supported.
#
# Pops: items to be added (count = immediate argument)
#
def_op_graal(
    opc, "COLLECTION_ADD_STACK", 85, 1
)  # , (oparg, followingArgs, withJump) -> CollectionBits.elementCount(oparg) + 1, 1)
#
# Concatenates two collection of the same type. Collection type is determined by
# {@link CollectionBits} in immediate operand. Tuple is not supported.
#
# Pops: second collection, first collection
#
# Pushes: concatenated collection
#
def_op_graal(opc, "COLLECTION_ADD_COLLECTION", 86, 1, 2, 1)
#
# Converts collection to another type determined by {@link CollectionBits} in immediate
# operand. The converted collection is expected to be an independent copy (they don't share
# storage).
#
# Pops: original collection
#
# Pushes: converted collection
#
def_op_graal(opc, "COLLECTION_FROM_COLLECTION", 87, 1, 1, 1)
#
# Converts list to tuple by reusing the underlying storage.
#
# Pops: list
#
# Pushes: tuple
#
def_op_graal(opc, "TUPLE_FROM_LIST", 88, 0, 1, 1)
#
# Converts list to frozenset.
#
# Pops: list
#
# Pushes: frozenset
#
def_op_graal(opc, "FROZENSET_FROM_LIST", 89, 0, 1, 1)
#
# Adds an item to a collection that is multiple items deep under the top of the stack,
# determined by the immediate argument.
#
# Pops: item to be added
#
def_op_graal(
    opc, "ADD_TO_COLLECTION", 90, 1
)  #  (oparg, followingArgs, withJump) -> CollectionBits.collectionKind(oparg) == CollectionBits.KIND_DICT ? 2 : 1, 0)
#
# Like {@link #COLLECTION_ADD_COLLECTION} for dicts, but with checks for duplicate keys
# necessary for keyword arguments merge. Note it works with dicts. Keyword arrays need to be
# converted to dicts first.
#
def_op_graal(opc, "KWARGS_DICT_MERGE", 91, 0, 2, 1)
#
# Create a single {@link PKeyword} object. The name is determined by the immediate operand
# which indexes the names array ({@code co_names})
#
# Pops: keyword value
#
# Pushes: keyword object
#
const_op_graal(opc, "MAKE_KEYWORD", 92, 1, 1, 1)

# -----------
# exceptions
# -----------

#
# Jump forward by the offset in the immediate argument if the exception doesn't match the
# expected type. The exception object is {@link PException}, not a python exception.
#
# Pops: expected type, then exception
#
# Pushes (if jumping): the exception
#
def_op_graal(opc, "MATCH_EXC_OR_JUMP", 93, 3, 2, 1)
#
# Save the current exception state on the stack and set it to the exception on the stack. The
# exception object is {@link PException}, not a python exception. The exception is pushed back
# to the top.
#
# Pops: the exception
#
# Pushes: the saved exception state, the exception
#
def_op_graal(opc, "PUSH_EXC_INFO", 94, 0, 0, 1)

# Sets the current exception state to the saved state (by {@link #PUSH_EXC_INFO}) on the stack
# and pop it.
#
# Pops: save exception state
## def_op_graal(opc, "POP_EXCEPT", 95, 0, 1, 0)  # not observed

# Restore exception state and reraise exception.
#
# Pops: exception to reraise, then saved exception state
def_op_graal(opc, "END_EXC_HANDLER", 96, 0, 2, 0)

# Gets the python-level exception object from a {@link PException}.
#
# Pops: a {@link PException} Pushes: python exception
#
def_op_graal(opc, "UNWRAP_EXC", 97, 0, 1, 1)

# ----------
# generators
# ----------
#
# Yield value from the stack to the caller. Saves execution state. The generator will resume at
# the next instruction.
#
# Pops: yielded value
#
def_op_graal(opc, "YIELD_VALUE", 98, 0, 1, 0)
#
# Wrap value from the stack in a {@link PAsyncGenWrappedValue}. CPython 3.11 opcode, used here
# to avoid a runtime check
#
# Pops: an object Pushes: async_generator_wrapped_value
#
def_op_graal(opc, "ASYNCGEN_WRAP", 99, 0, 1, 1)
#
# Resume after yield. Will raise exception passed by {@code throw} if any.
#
# Pushes: value received from {@code send} or {@code None}.
#
def_op_graal(opc, "RESUME_YIELD", 100, 0, 0, 1)
#
# Send value into a generator. Jumps forward by the offset in the immediate argument if the
# generator is exhausted. Used to implement {@code yield from}.
#
# Pops: value to be sent, then generator
#
# Pushes (if not jumping): the generator, then the yielded value
#
# Pushes (if jumping): the generator return value
#
def_op_graal(
    opc, "SEND", 101, 1, 2
)  # , (oparg, followingArgs, withJump) -> withJump ? 1 : 2)

# Exception handler for forwarding {@code throw} calls into {@code yield from}.
#
# Pops: exception, then the generator
#
# Pushes (if not jumping): the generator, then the yielded value
#
# Pushes (if jumping): the generator return value
def_op_graal(
    opc, "THROW", 102, 1, 2
)  # , (oparg, followingArgs, withJump) -> withJump ? 1 : 2)

# Exception handler for async for loops. If the current exception is StopAsyncIteration, handle
# it, otherwise, reraise.
#
# Pops: exception, then the anext coroutine, then the async iterator
def_op_graal(opc, "END_ASYNC_FOR", 103, 0, 3, 0)

# with statements
#
# Enter a context manager and save data for its exit.
#
# Pops: the context manager
#
# Pushes: the context manager, then maybe-bound {@code __exit__}, then the result of
# {@code __enter__}
def_op_graal(opc, "SETUP_WITH", 104, 0, 1, 3)

# Run the exit handler of a context manager and reraise if necessary.
#
# Pops: exception or {@code None}, then maybe-bound {@code __exit__}, then the context manager

def_op_graal(opc, "EXIT_WITH", 105, 0, 3, 0)

# Enter a context manager and save data for its exit
#
# Pops: the context manager
#
# Pushes: the context manager, then the maybe-bound async function {@code __aexit__}, then the
# awaitable returned by {@code __aenter__}
#
def_op_graal(opc, "SETUP_AWITH", 106, 0, 1, 3)

# Run the exit handler of a context manager
#
# Pops: exception or {@code None}, then maybe-bound {@code __aexit__}, then the context manager
#
# Pushes: the exception or {@code None}, then the awaitable returned by {@code __aexit__}
def_op_graal(opc, "GET_AEXIT_CORO", 107, 0, 3, 2)

# Reraise the exception passed to {@code __aexit__} if appropriate
#
#!Pops: The result of awaiting {@code __aexit__}, then the exception
def_op_graal(opc, "EXIT_AWITH", 108, 0, 2, 0)


update_sets(loc)
