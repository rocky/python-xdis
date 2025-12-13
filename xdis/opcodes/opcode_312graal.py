# (C) 2025 by Rocky Bernstein
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
Python Graal 3.12 (graal-24) bytecode opcodes

See com.oracle.graal.python/src/com/oracle/graal/python/compiler/OpCodes.java
"""

from typing import Dict, Set

from xdis.opcodes.base import VARYING_STACK_INT, init_opdata

# from xdis.opcodes.base_graal import findlabels  # noqa
from xdis.opcodes.base_graal import (  # find_linestarts,  # noqa
    binary_op_graal,
    call_op_graal,
    collection_op_graal,
    const_op_graal,
    def_op_graal,
    free_op_graal,
    jrel_op_graal,
    name_op_graal,
    nargs_op_graal,
    store_op_graal,
    unary_op_graal,
    update_sets,
)
from xdis.version_info import PythonImplementation

python_implementation = PythonImplementation("Graal")
version_tuple = (3, 12, 7)

arg_counts: Dict[int, int] = {}

# opcodes that perform a binary operation on the top two stack entries
binaryop: Set[int] = set([])

# opcodes that perform some sort of call
callop: Set[int] = set([])

# opcodes that perform some sort of call
collectionop: Set[int] = set([])

# opcodes that perform a unary operation on the toip stack entry
unaryop: Set[int] = set([])

opc = loc = locals()

init_opdata(loc, None, None)


# Instruction opcodes for compiled code
# Blank lines correspond to available opcodes

# If the POP field is -1 and the opcode is a var args operation
# then the operand holds the size.
#
# If the POP field is negative and the opcode is a nargs operation
# then pop the operand amount plus the negative of the POP amount.

# Pop a single item from the stack.
def_op_graal(loc, "POP_TOP", 0x0, 0, 1, 0)

# Exchange two top stack items.
def_op_graal(loc, "ROT_TWO", 0x1, 0, 2, 0)

# Exchange three top stack items. [a, b, c] (a is top) becomes [b, c, a]
def_op_graal(loc, "ROT_THREE", 0x2, 0, 3, 0)

# Exchange N top stack items. [a, b, c, ..., N] (a is top) becomes [b, c, ..., N, a].
def_op_graal(
    loc, "ROT_N", 0x3, -1, -1
)  #  (oparg, followingArgs, withJump) -> oparg, (oparg, followingArgs, withJump) -> oparg)

# Duplicates the top stack item.
def_op_graal(loc, "DUP_TOP", 0x4, 0, 1, 0)

# Does nothing. Might still be useful to maintain a line number.
def_op_graal(loc, "NOP", 0x5, 0, 0, 0)

# Performs a unary operation specified by the immediate operand. It
# has to be the ordinal of one of {@link UnaryOps} constants.
#  Pops: operand
#  Pushes: result
unary_op_graal(loc, "UNARY_OP", 0x6, 1, 1, 1)

# Performs a binary operation specified by the immediate operand. It has to be the ordinal of
# one of {@link BinaryOps} constants.
#   Pops: right operand, then left operand
#   Pushes: result
binary_op_graal(loc, "BINARY_OP", 0x7, 1, 2, 1)

# Performs subscript get operation - {@code a[b]}.
#   Pops: {@code b}, then {@code a}
#   Pushes: result
def_op_graal(loc, "BINARY_SUBSCR", 0x8, 1, 2, 0)

# Performs subscript set operation - {@code a[b] = c}.
#   Pops: {@code b}, then {@code a}, then {@code c}
def_op_graal(loc, "STORE_SUBSCR", 0x9, 0, 3, 0)

# Performs subscript delete operation - {@code del a[b]}.
#   Pops: {@code b}, then {@code a}
#
def_op_graal(loc, "DELETE_SUBSCR", 0xA, 0, 2, 0)

# Gets an iterator of an object.
#   Pops: object
#   Pushes: iterator
def_op_graal(loc, "GET_ITER", 0xB, 1, 1, 0)

# Gets an iterator of an object, does nothing for a generator iterator or a coroutine.
#   Pops: object
#   Pushes: iterator
def_op_graal(loc, "GET_YIELD_FROM_ITER", 0xC, 0, 1, 1)

# Gets an awaitable of an object.
#   Pops: object
#   Pushes: awaitable
def_op_graal(loc, "GET_AWAITABLE", 0xD, 0, 1, 1)

# Gets the async iterator of an object - error if a coroutine is returned.
#   Pops: object
#   Pushes: async iterator
#  Not in 3.8
def_op_graal(loc, "GET_AITER", 0xe, 0, 1, 1)

# Get the awaitable that will return the next element of an async iterator.
#   Pops: object
#   Pushes: awaitable
#  Not in 3.8
def_op_graal(loc, "GET_ANEXT", 0xf, 0, 1, 1)

# Pushes: {@code __build_class__} builtin
def_op_graal(loc, "LOAD_BUILD_CLASS", 0x10, 0, 1, 0)

# Pushes: {@code AssertionError} builtin exception type
def_op_graal(loc, "LOAD_ASSERTION_ERROR", 0x11, 0, 0, 1)

# Returns the value to the caller. In generators, performs generator return.
#   Pops: return value
def_op_graal(loc, "RETURN_VALUE", 0x12, 0, 1, 0)
#
# Reads a name from locals dict, globals or builtins determined by the
# immediate operand which indexes the names array ({@code co_names}).
#  Pushes: read object
name_op_graal(loc, "LOAD_NAME", 0x13, 1, 0, 1)
loc["nullaryloadop"].add(0x13)

# Writes the stack top into a name in locals dict or globals
# determined by the immediate operand which indexes the names array
# ({@code co_names}).
#  Pops: object to be written
store_op_graal(loc, "STORE_NAME", 0x14, 1, 1, "name", 1)
# observed

# Deletes the name in locals dict or globals determined by the
# immediate operand which indexes the names array ({@code co_names}).
name_op_graal(loc, "DELETE_NAME", 0x15, 1, 0, 1)

# Reads an attribute - {@code a.b}. {@code b} is determined by the immediate operand which
# indexes the names array ({@code co_names}).
#  Pops: {@code a}
#  Pushes: read attribute
name_op_graal(loc, "LOAD_ATTR", 0x16, 1, 1, 1)
#
# Reads method on an object. The method name is determined by the
# first immediate operand which indexes the names array ({@code
# co_names}).
#   Pushes: read method
name_op_graal(loc, "LOAD_METHOD", 0x17, 1, 1, 1)

# Writes an attribute - {@code a.b = c}. {@code b} is determined by
# the immediate operand which indexes the names array ({@code
# co_names}).
#  Pops: {@code c}, then {@code a}
name_op_graal(loc, "STORE_ATTR", 0x18, 1, 2, 1)

# Deletes an attribute - {@code del a.b}. {@code b} is determined by
# the immediate operand which indexes the names array ({@code
# co_names}).
#  Pops: {@code a}
name_op_graal(loc, "DELETE_ATTR", 0x19, 1, 1, 1)

# Reads a global variable. The name is determined by the immediate
# operand which indexes the names array ({@code co_names}).
#   Pushes: read object
name_op_graal(loc, "LOAD_GLOBAL", 0x1A, 1, 0, 1)
loc["nullaryloadop"].add(0x1A)


# Writes a global variable. The name is determined by the immediate
# operand which indexes the names array ({@code co_names}).
#  Pops: value to be written
name_op_graal(loc, "STORE_GLOBAL", 0x1B, 1, 1, 0)

# Deletes a global variable. The name is determined by the immediate operand which indexes the
# names array ({@code co_names}).
name_op_graal(loc, "DELETE_GLOBAL", 0x1C, 1, 0, 0)

# Reads a constant object from constants array ({@code co_consts}). Performs no conversion.
#   Pushes: read constant
const_op_graal(loc, "LOAD_CONST", 0x1D, 1, 0, 1)
loc["nullaryloadop"].add(0x1D)

# Reads a local variable determined by the immediate operand which indexes a stack slot and a
# variable name in varnames array ({@code co_varnames}).
#   Pushes: read value
def_op_graal(loc, "LOAD_FAST", 0x1E, 1, 0, 1)
loc["nullaryloadop"].add(0x1EC)


# Writes a local variable determined by the immediate operand which indexes a stack slot and a
# variable name in varnames array ({@code co_varnames}).
#  Pops: value to be written
def_op_graal(loc, "STORE_FAST", 0x1F, 1, 1, 1)

# Deletes a local variable determined by the immediate operand which indexes a stack slot and a
# variable name in varnames array ({@code co_varnames}).
def_op_graal(loc, "DELETE_FAST", 0x20, 1, 0, 1)

# Reads a local cell variable determined by the immediate operand
# which indexes a stack slot after celloffset and a variable name in
# cellvars or freevars array ({@code co_cellvars}, {@code
# co_freevars}).
#  Pushes: cell contents
free_op_graal(loc, "LOAD_DEREF", 0x21, 1, 0, 1)

# Deletes a local cell variable determined by the immediate operand
# which indexes a stack slot after celloffset and a variable name in
# cellvars or freevars array ({@code co_cellvars}, {@code
# co_freevars}). Note that it doesn't delete the cell, just its
# contents.
free_op_graal(loc, "DELETE_DEREF", 0x22, 1, 0, 0)

# Writes a local cell variable determined by the immediate operand
# which indexes a stack slot after celloffset and a variable name in
# cellvars or freevars array ({@code co_cellvars}, {@code
# co_freevars}).
#  Pops: value to be written into the cell contents
# FIXME: this should be tagged as both a "free" and as "store" op.
free_op_graal(loc, "STORE_DEREF", 0x23, 1, 1, 0)

# TODO not implemented
def_op_graal(loc, "LOAD_CLASSDEREF", 0x24, 1, 0, 1)

# Raises an exception. If the immediate operand is 0, it pops nothing
# and is equivalent to {@code raise} without arguments. If the
# immediate operand is 1, it is equivalent to {@code raise e} and it
# pops {@code e}. If the immediate operand is 2, it is equivalent to
# {@code raise e from c} and it pops {@code c}, then {@code e}. Other
# immediate operand values are illegal.
def_op_graal(
    loc, "RAISE_VARARGS", 0x27, 1, 0, 1
)  # , (oparg, followingArgs, withJump) -> oparg, 0)

# Creates a slice object. If the immediate argument is 2, it is equivalent to a slice
# {@code a:b}. It pops {@code b}, then {@code a}. If the immediate argument is 3, it is
# equivalent to a slice {@code a:b:c}. It pops {@code c}, then {@code b}, then {@code a}. Other
# immediate operand values are illegal.
#   Pushes: the created slice object
def_op_graal(
    loc, "BUILD_SLICE", 0x28, 1, 0, 1
)  # (oparg, followingArgs, withJump) -> oparg, 1)

# Formats a value. If the immediate argument contains flag {@link FormatOptions#FVS_HAVE_SPEC},
# it is equivalent to {@code format(conv(v), spec)}. It pops {@code spec}, then {@code v}.
# Otherwise, it is equivalent to {@code format(conv(v), None)}. It pops {@code v}. {@code conv}
# is determined by the immediate operand which contains one of the {@code FVC} options in
# {@link FormatOptions}.
#  Pushes: the formatted value
def_op_graal(
    loc, "FORMAT_VALUE", 0x29, 2, 1, 1
)  # , (oparg, followingArgs, withJump) -> (oparg & FormatOptions.FVS_MASK) == FormatOptions.FVS_HAVE_SPEC ? 2 : 1, 1)

# Extends the immediate operand of the following instruction by its own operand shifted left by
# a byte.
def_op_graal(loc, "EXTENDED_ARG", 0x2A, 1, 0, 0)


# Imports a module by name determined by the immediate operand which
# indexes the names array ({@code co_names}).
#  Pops: fromlist (must be a constant {@code TruffleString[]}), then level (must be {@code int})
#  Pushes: imported module
name_op_graal(loc, "IMPORT_NAME", 0x2B, 1, 2, 1)
loc["nullaryloadop"].add(0x2B)


# Imports a name from a module. The name determined by the immediate operand which indexes the
# names array ({@code co_names}).
#  Pops: module object
#   Pushes: module object, imported object
name_op_graal(loc, "IMPORT_FROM", 0x2C, 1, 1, 1)

# Imports all names from a module of name determined by the immediate operand which indexes the
# names array ({@code co_names}). The imported names are written to locals dict (can only be
# invoked on module level).
#   Pops: level (must be {@code int})
def_op_graal(loc, "IMPORT_STAR", 0x2D, 1, 1, 0)

# Prints the top of the stack. Used by "single" parsing mode to echo
# expressions.
#   Pops: the value to print
def_op_graal(loc, "PRINT_EXPR", 0x2E, 0, 1, 0)

# Creates annotations dict in locals
def_op_graal(loc, "SETUP_ANNOTATIONS", 0x2F, 0, 0, 0)

# Determines if a python object is a sequence.
def_op_graal(loc, "MATCH_SEQUENCE", 0x30, 0, 0, 1)

# Determines if a Python object is a mapping.
def_op_graal(loc, "MATCH_MAPPING", 0x31, 0, 0, 1)

# Determines if a Python object is of a particular type.
def_op_graal(loc, "MATCH_CLASS", 0x32, 1, 3, 2)

# Matches the keys (stack top) in a dict (stack second). On successful
# match pushes the values and True, otherwise None and False.
def_op_graal(loc, "MATCH_KEYS", 0x33, 0, 2, 4)

# Creates a copy of a dict (stack second) without elements matching a
# tuple of keys (stack top).
def_op_graal(loc, "COPY_DICT_WITHOUT_KEYS", 0x34, 0, 1, 1)

# Retrieves the length of a Python object and stores it on top.
def_op_graal(loc, "GET_LEN", 0x35, 0, 0, 1)

# -------------------------------------
# load bytecodes for special constants
# -------------------------------------

def_op_graal(loc, "LOAD_NONE", 0x36, 0, 1, 0)
loc["nullaryloadop"].add(0x36)

def_op_graal(loc, "LOAD_ELLIPSIS", 0x37, 0, 1, 0)
def_op_graal(loc, "LOAD_TRUE", 0x38, 0, 1, 0)
loc["nullaryloadop"].add(0x38)

def_op_graal(loc, "LOAD_FALSE", 0x39, 0, 1, 0)
loc["nullaryloadop"].add(0x39)

def_op_graal(loc, "LOAD_BYTE", 0x3A, 1, 0, 1)
#
#### Continue adding opcode numbers here...


# Loads {@code int} from primitiveConstants array indexed by the immediate operand.
#
def_op_graal(loc, "LOAD_INT", 0x3B, 1, 0, 1)
#
# Loads {@code long} from primitiveConstants array indexed by the immediate operand.
#
def_op_graal(loc, "LOAD_LONG", 0x3C, 1, 0, 1)
#
# Loads {@code double} from primitiveConstants array indexed by the immediate operand
# (converted from long).
#
def_op_graal(loc, "LOAD_DOUBLE", 0x3D, 1, 0, 1)
#

# Creates a {@link PInt} from a {@link BigInteger} in constants array indexed by the immediate
# operand.
#
def_op_graal(loc, "LOAD_BIGINT", 0x3E, 1, 0, 1)
#
# Currently the same as {@link #LOAD_CONST}.
#
const_op_graal(loc, "LOAD_STRING", 0x3F, 0, 1)

#
# Creates python {@code bytes} from a {@code byte[]} array in constants array indexed by the
# immediate operand.
#
def_op_graal(loc, "LOAD_BYTES", 0x40, 0, 1)
#
# Creates python {@code complex} from a {@code double[]} array of size 2 in constants array
# indexed by the immediate operand.
#
def_op_graal(loc, "LOAD_COMPLEX", 0x41, 1, 0, 1)

# Creates a collection out of a Java array in constants array indexed by the immediate operand.
# The second immediate operand determines the array type and kind, using values from {@link
# CollectionBits}. The only allowed kinds are list and tuple.
#
const_op_graal(loc, "LOAD_CONST_COLLECTION", 0x42, 2, 0, 2)

# -------
# calling
# -------

# calls method on an object using an array as args. the receiver is taken from the first
# element of the array. the method name is determined by the immediate operand which indexes
# the names array ({@code co_names}).
#
# pops: args ({@code object[]} of size >= 1)
#
# pushes: call result
#
call_op_graal(loc, "call_method_varargs", 0x43, 1, 1, 1)
#
# calls method on an object using a number of stack args determined by the first immediate
# operand.
#
# pops: multiple arguments depending on the first immediate operand, then the method and the
# receiver
#
# pushes: call result
#
call_op_graal(
    loc, "CALL_METHOD", 0x44, 1, 1, 1
)  # , (oparg, followingArgs, withJump) -> oparg + 2, 1)
#
# Calls a callable using a number of stack args determined by the immediate operand.
#
# Pops: multiple arguments depending on the immediate operand (0 - 4), then the callable
#
# Pushes: call result
#
call_op_graal(
    loc, "CALL_FUNCTION", 0x45, 2, 1, 1
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
call_op_graal(loc, "CALL_COMPREHENSION", 0x46, 0, 2)
#
# Calls a callable using an arguments array and keywords array.
#
# Pops: keyword args ({@code PKeyword[]}), then args ({@code Object[]}), then callable
#
# Pushes: call result
#
call_op_graal(loc, "CALL_FUNCTION_KW", 0x47, 0, 3)
arg_counts[0x47] = 0

#
# Calls a callable using an arguments array. No keywords are passed.
#
# Pops: args ({@code Object[]}), then callable
#
# Pushes: call result
#
def_op_graal(loc, "CALL_FUNCTION_VARARGS", 0x48, 0, 2, 0)

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
    loc, "UNPACK_SEQUENCE", 0x49, 1, VARYING_STACK_INT, 1
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
    loc, "UNPACK_EX", 0x4a, VARYING_STACK_INT, VARYING_STACK_INT, 1
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
jrel_op_graal(
    loc, "FOR_ITER", 0x4b, 1, 1, True, True, 1
)  # (, (oparg, followingArgs, withJump) -> withJump ? 0 : 2)
#
# Jump forward by the offset in the immediate operand.
#
jrel_op_graal(loc, "JUMP_FORWARD", 0x4c, 1, 0, False, False, 1)

# Jump backward by the offset in the immediate operand. May trigger OSR compilation.
#
jrel_op_graal(loc, "JUMP_BACKWARD", 0x4d, 1, 0, False, False, 1)

# Jump forward by the offset in the immediate operand if the top of the stack is false (in
# Python sense).
#
# Pops (if not jumping): top of the stack
jrel_op_graal(
    loc, "JUMP_IF_FALSE_OR_POP", 0x4e, 1, 1, True, True, 3,
)  # , (oparg, followingArgs, withJump) -> withJump ? 0 : 1, 0)

# Jump forward by the offset in the immediate operand if the top of the stack is true (in
# Python sense).
#
# Pops (if not jumping): top of the stack
#
jrel_op_graal(
    loc, "JUMP_IF_TRUE_OR_POP", 0x4f, 1, 1, True, True, 3,
)  # , (oparg, followingArgs, withJump) -> withJump ? 0 : 1, 0)
#
# Jump forward by the offset in the immediate operand if the top of the stack is false (in
# Python sense).
#
# Pops: top of the stack
#
jrel_op_graal(loc, "POP_AND_JUMP_IF_FALSE", 0x50, 1, 1, True, True, 3)
#
# Jump forward by the offset in the immediate operand if the top of the stack is true (in
# Python sense).
#
# Pops: top of the stack
#
jrel_op_graal(loc, "POP_AND_JUMP_IF_TRUE", 0x51, 1, 1, True, True, 3)


# ----------------
# making callables
# ----------------

#
# Like {@link #LOAD_DEREF}, but loads the cell itself, not the contents.
#
# Pushes: the cell object
#
free_op_graal(loc, "LOAD_CLOSURE", 0x52, 1, 0, 1)
#
# Reduces multiple stack items into an array of cell objects.
#
# Pops: multiple cells (count = immediate argument)
#
# Pushes: cell object array ({@code PCell[]})
#
def_op_graal(
    loc, "CLOSURE_FROM_STACK", 0x53, 1
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
    loc, "MAKE_FUNCTION", 0x54, 1, 2, 2
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
collection_op_graal(
    loc, "COLLECTION_FROM_STACK", 0x58, 1
)  # , (oparg, followingArgs, withJump) -> CollectionBits.elementCount(oparg), 1)
#
# Add multiple elements from the stack to the collection below them. Collection type is
# determined by {@link CollectionBits} in immediate operand. Tuple is not supported.
#
# Pops: items to be added (count = immediate argument)
#
collection_op_graal(
    loc, "COLLECTION_ADD_STACK", 0x59, 1
)  # , (oparg, followingArgs, withJump) -> CollectionBits.elementCount(oparg) + 1, 1)
#
# Concatenates two collection of the same type. Collection type is determined by
# {@link CollectionBits} in immediate operand. Tuple is not supported.
#
# Pops: second collection, first collection
#
# Pushes: concatenated collection
#
collection_op_graal(loc, "COLLECTION_ADD_COLLECTION", 0x5a, 1, 2, 1)
#
# Converts collection to another type determined by {@link CollectionBits} in immediate
# operand. The converted collection is expected to be an independent copy (they don't share
# storage).
#
# Pops: original collection
#
# Pushes: converted collection
#
collection_op_graal(loc, "COLLECTION_FROM_COLLECTION", 0x5b, 1, 1, 1)
#
# Converts list to tuple by reusing the underlying storage.
#
# Pops: list
#
# Pushes: tuple
#
def_op_graal(loc, "TUPLE_FROM_LIST", 0x5c, 0, 1, 1)
#
# Converts list to frozenset.
#
# Pops: list
#
# Pushes: frozenset
#
def_op_graal(loc, "FROZENSET_FROM_LIST", 0x5d, 0, 1, 1)
#
# Adds an item to a collection that is multiple items deep under the top of the stack,
# determined by the immediate argument.
#
# Pops: item to be added
#
collection_op_graal(
    loc, "ADD_TO_COLLECTION", 0x5e, 1
)  #  (oparg, followingArgs, withJump) -> CollectionBits.collectionKind(oparg) == CollectionBits.KIND_DICT ? 2 : 1, 0)
#
# Like {@link #COLLECTION_ADD_COLLECTION} for dicts, but with checks for duplicate keys
# necessary for keyword arguments merge. Note it works with dicts. Keyword arrays need to be
# converted to dicts first.
#
def_op_graal(loc, "KWARGS_DICT_MERGE", 0x5F, 0, 2, 0)
#
# Create a single {@link PKeyword} object. The name is determined by the immediate operand
# which indexes the names array ({@code co_names})
#
# Pops: keyword value
#
# Pushes: keyword object
#
def_op_graal(loc, "MAKE_KEYWORD", 0x60, 1, 1, 1)

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
jrel_op_graal(loc, "MATCH_EXC_OR_JUMP", 0x61, 1, 0, 1)
#
# Save the current exception state on the stack and set it to the exception on the stack. The
# exception object is {@link PException}, not a python exception. The exception is pushed back
# to the top.
#
# Pops: the exception
#
# Pushes: the saved exception state, the exception
#
def_op_graal(loc, "PUSH_EXC_INFO", 0x62, 0, 0, 1)

# Sets the current exception state to the saved state (by {@link #PUSH_EXC_INFO}) on the stack
# and pop it.
#
# Pops: save exception state
def_op_graal(loc, "POP_EXCEPT", 0x63, 0, 1, 0)

# Restore exception state and reraise exception.
#
# Pops: exception to reraise, then saved exception state
def_op_graal(loc, "END_EXC_HANDLER", 0x64, 0, 2, 0)

# Gets the python-level exception object from a {@link PException}.
#
# Pops: a {@link PException} Pushes: python exception
#
def_op_graal(loc, "UNWRAP_EXC", 0x65, 0, 1, 1)

# ----------
# generators
# ----------
#
# Yield value from the stack to the caller. Saves execution state. The generator will resume at
# the next instruction.
#
# Pops: yielded value
#
def_op_graal(loc, "YIELD_VALUE", 0x66, 0, 1, 0)
#
# Wrap value from the stack in a {@link PAsyncGenWrappedValue}. CPython 3.11 opcode, used here
# to avoid a runtime check
#
# Pops: an object Pushes: async_generator_wrapped_value
#
def_op_graal(loc, "ASYNCGEN_WRAP", 0x67, 0, 1, 1)
#
# Resume after yield. Will raise exception passed by {@code throw} if any.
#
# Pushes: value received from {@code send} or {@code None}.
#
def_op_graal(loc, "RESUME_YIELD", 0x68, 0, 0, 1)
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
jrel_op_graal(
    loc, "SEND", 0x69, 1, 2, 1
)  # , (oparg, followingArgs, withJump) -> withJump ? 1 : 2)

# Exception handler for forwarding {@code throw} calls into {@code yield from}.
#
# Pops: exception, then the generator
#
# Pushes (if not jumping): the generator, then the yielded value
#
# Pushes (if jumping): the generator return value
def_op_graal(
    loc, "THROW", 0x6A, 1, 2, 1
)  # , (oparg, followingArgs, withJump) -> withJump ? 1 : 2)

# Exception handler for async for loops. If the current exception is StopAsyncIteration, handle
# it, otherwise, reraise.
#
# Pops: exception, then the anext coroutine, then the async iterator
def_op_graal(loc, "END_ASYNC_FOR", 0x6B, 0, 3, 0)

# with statements
#
# Enter a context manager and save data for its exit.
#
# Pops: the context manager
#
# Pushes: the context manager, then maybe-bound {@code __exit__}, then the result of
# {@code __enter__}
def_op_graal(loc, "SETUP_WITH", 0x6c, 1, 0, 0)

# Run the exit handler of a context manager and reraise if necessary.
#
# Pops: exception or {@code None}, then maybe-bound {@code __exit__}, then the context manager

def_op_graal(loc, "EXIT_WITH", 0x6d, 0, 3, 0)

# Enter a context manager and save data for its exit
#
# Pops: the context manager
#
# Pushes: the context manager, then the maybe-bound async function {@code __aexit__}, then the
# awaitable returned by {@code __aenter__}
#
def_op_graal(loc, "SETUP_AWITH", 0x6e, 0, 1, 3)

# Run the exit handler of a context manager
#
# Pops: exception or {@code None}, then maybe-bound {@code __aexit__}, then the context manager
#
# Pushes: the exception or {@code None}, then the awaitable returned by {@code __aexit__}
def_op_graal(loc, "GET_AEXIT_CORO", 0x6f, 0, 3, 2)

# Reraise the exception passed to {@code __aexit__} if appropriate
#
#!Pops: The result of awaiting {@code __aexit__}, then the exception
def_op_graal(loc, "EXIT_AWITH", 0x70, 0, 2, 0)

# Quickened bytecodes
#
def_op_graal(loc, "LOAD_TRUE_O", 0x71, 1, 0, 0)
def_op_graal(loc, "LOAD_TRUE_B", 0x72, 1, 0, 0)
def_op_graal(loc, "LOAD_FALSE_O", 0x73, 1, 0, 0)
def_op_graal(loc, "LOAD_FALSE_B", 0x74, 1, 0, 0)
def_op_graal(loc, "LOAD_BYTE_O", 0x75, 1, 0, 1)
def_op_graal(loc, "LOAD_BYTE_I", 0x76, 1, 0, 1)
def_op_graal(loc, "LOAD_INT_O", 0x77, 1, 0, 1)
def_op_graal(loc, "LOAD_INT_I", 0x78, 1, 0, 1)
def_op_graal(loc, "LOAD_LONG_O", 0x7A, 1, 0, 1)
def_op_graal(loc, "LOAD_LONG_L", 0x7A, 1, 0, 1)
def_op_graal(loc, "LOAD_DOUBLE_O", 0x7B, 1, 0, 1)
def_op_graal(loc, "LOAD_DOUBLE_D", 0x7C, 1, 0, 1)
# There are more...
# LOAD_FAST*
# STORE_FAST*
# UNARY_OP*
# BINARY_OP*
# FOR_ITER*
# BINARY_SUBSCR*
# and MORE!

# Something is wrong here...
collection_op_graal(loc, "COLLECTION_FROM_COLLECTION", 0xa0, 1, 1, 0)
#

update_sets(loc)
