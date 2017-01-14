"""
CPython 1.5 bytecode opcodes

This is used in bytecode disassembly. This is similar to the
opcodes in Python's dis.py library.
"""

# These are used from outside this module
from xdis.bytecode import findlabels, findlinestarts
from xdis.opcodes.base import (
    cmp_op, compare_op, const_op,
    def_op,
    free_op, jabs_op, jrel_op,
    local_op, name_op, nargs_op,
    varargs_op,
    HAVE_ARGUMENT
    )

l = locals()

# FIXME: can we DRY this even more?

hasconst = []
hasname = []
hasjrel = []
hasjabs = []
haslocal = []
hascompare = []
hasfree = []
hasnargs = []  # For function-like calls
hasvargs = []  # Similar but for operators BUILD_xxx

# oppush[op] => number of stack entries pushed
oppush = [0] * 256

# oppop[op] => number of stack entries popped
oppop  = [0] * 256

opmap = {}
opname = [''] * 256
for op in range(256): opname[op] = '<%r>' % (op,)
del op

# Instruction opcodes for compiled code
# Blank lines correspond to available opcodes

def_op(l, 'STOP_CODE', 0)
def_op(l, 'POP_TOP', 1)
def_op(l, 'ROT_TWO', 2)
def_op(l, 'ROT_THREE', 3)
def_op(l, 'DUP_TOP', 4)

def_op(l, 'UNARY_POSITIVE', 10)
def_op(l, 'UNARY_NEGATIVE', 11)
def_op(l, 'UNARY_NOT', 12)
def_op(l, 'UNARY_CONVERT', 13)

def_op(l, 'UNARY_INVERT', 15)

def_op(l, 'BINARY_POWER', 19)

def_op(l, 'BINARY_MULTIPLY', 20)
def_op(l, 'BINARY_DIVIDE', 21)
def_op(l, 'BINARY_MODULO', 22)
def_op(l, 'BINARY_ADD', 23)
def_op(l, 'BINARY_SUBTRACT', 24)
def_op(l, 'BINARY_SUBSCR', 25)

def_op(l, 'SLICE+0', 30)
def_op(l, 'SLICE+1', 31)
def_op(l, 'SLICE+2', 32)
def_op(l, 'SLICE+3', 33)

def_op(l, 'STORE_SLICE+0', 40)
def_op(l, 'STORE_SLICE+1', 41)
def_op(l, 'STORE_SLICE+2', 42)
def_op(l, 'STORE_SLICE+3', 43)

def_op(l, 'DELETE_SLICE+0', 50)
def_op(l, 'DELETE_SLICE+1', 51)
def_op(l, 'DELETE_SLICE+2', 52)
def_op(l, 'DELETE_SLICE+3', 53)

def_op(l, 'STORE_SUBSCR', 60)
def_op(l, 'DELETE_SUBSCR', 61)

def_op(l, 'BINARY_LSHIFT', 62)
def_op(l, 'BINARY_RSHIFT', 63)
def_op(l, 'BINARY_AND', 64)
def_op(l, 'BINARY_XOR', 65)
def_op(l, 'BINARY_OR', 66)

def_op(l, 'PRINT_EXPR', 70)
def_op(l, 'PRINT_ITEM', 71)
def_op(l, 'PRINT_NEWLINE', 72)

def_op(l, 'BREAK_LOOP', 80)

def_op(l, 'LOAD_LOCALS', 82)
def_op(l, 'RETURN_VALUE', 83)

def_op(l, 'EXEC_STMT', 85)

def_op(l, 'POP_BLOCK', 87)
def_op(l, 'END_FINALLY', 88)
def_op(l, 'BUILD_CLASS', 89)

name_op(l, 'STORE_NAME', 90)       # Index in name list
name_op(l, 'DELETE_NAME', 91)      # ""
varargs_op(l, 'UNPACK_TUPLE', 92)  # Number of tuple items
def_op(l, 'UNPACK_LIST', 93)	   # Number of list items
name_op(l, 'STORE_ATTR', 95)       # Index in name list
name_op(l, 'DELETE_ATTR', 96)      # ""
name_op(l, 'STORE_GLOBAL', 97)     # ""
name_op(l, 'DELETE_GLOBAL', 98)    # ""

const_op(l, 'LOAD_CONST', 100)     # Index in const list
name_op(l, 'LOAD_NAME', 101)       # Index in name list
varargs_op(l, 'BUILD_TUPLE', 102)  # Number of tuple items
varargs_op(l, 'BUILD_LIST', 103)   # Number of list items
varargs_op(l, 'BUILD_MAP', 104)    # Always zero for now
name_op(l, 'LOAD_ATTR', 105)       # Index in name list
compare_op(l, 'COMPARE_OP', 106)   # Comparison operator

name_op(l, 'IMPORT_NAME', 107)     # Index in name list
name_op(l, 'IMPORT_FROM', 108)     # Index in name list

jrel_op(l, 'JUMP_FORWARD', 110)    # Number of bytes to skip
jrel_op(l, 'JUMP_IF_FALSE', 111)   # ""
jrel_op(l, 'JUMP_IF_TRUE', 112)    # ""
jabs_op(l, 'JUMP_ABSOLUTE', 113)   # Target byte offset from beginning of code
def_op(l, 'FOR_LOOP', 114)	   # Number of bytes to skip

name_op(l, 'LOAD_GLOBAL', 116)     # Index in name list

jrel_op(l, 'SETUP_LOOP', 120)      # Distance to target address
jrel_op(l, 'SETUP_EXCEPT', 121)    # ""
jrel_op(l, 'SETUP_FINALLY', 122)   # ""

local_op(l, 'LOAD_FAST', 124)      # Local variable number
local_op(l, 'STORE_FAST', 125)     # Local variable number
local_op(l, 'DELETE_FAST', 126)    # Local variable number
def_op(l, 'SET_LINENO', 127)	   # Current line number

def_op(l, 'RAISE_VARARGS',  130)   # Number of raise arguments (1, 2, or 3)
nargs_op(l, 'CALL_FUNCTION', 131)  # #args + (#kwargs << 8)

def_op(l, 'MAKE_FUNCTION', 132)    # Number of args with default values
varargs_op(l, 'BUILD_SLICE', 133)  # Number of items

EXTENDED_ARG = 143

fields2copy = """cmp_op hasjabs""".split()

def updateGlobal():
    globals().update({'python_version': 1.5})
    # Canonicalize to PJIx: JUMP_IF_y and POP_JUMP_IF_y
    globals().update({'PJIF': opmap['JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['JUMP_IF_TRUE']})

    globals().update({'JUMP_OPs': map(lambda op: opname[op],
                                      hasjrel + hasjabs)})
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))
    return

updateGlobal()

def dump_opcodes(opmap):
    """Utility for dumping opcodes"""
    op2name = {}
    for k in opmap.keys():
        op2name[opmap[k]] = k
    for i in sorted(op2name.keys()):
        print("%-3s %s" % (str(i), op2name[i]))
