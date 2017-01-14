"""CPython core set of bytecode opcodes based on version 2.3

This is used in bytecode disassembly among other things. This is
similar to the opcodes in Python's opcode.py library.

If this file changes the other opcode files may have to a adjusted accordingly.
"""

from xdis.opcodes.base import (
    def_op, name_op, varargs_op
    )

l = locals()

# FIXME: DRY this with opcode_3x.

cmp_op = ('<', '<=', '==', '!=', '>', '>=', 'in', 'not in', 'is',
        'is not', 'exception match', 'BAD')

hasconst = []
hasname = []
hasjrel = []
hasjabs = []
haslocal = []
hascompare = []
hasfree = []
hasnargs = []  # For function-like calls
hasvargs = []  # Similar but for operators BUILD_xxx

# opmap[opcode_name] => opcode_number
opmap = {}

# opcode[i] => opcode name
opname = [''] * 256

# oppush[op] => number of stack entries pushed
oppush = [0] * 256

# oppop[op] => number of stack entries popped
oppop  = [0] * 256

for op in range(256): opname[op] = '<%r>' % (op,)
del op

def compare_op(name, op, pop=2, push=1):
    def_op(l, name, op, pop, push)
    hascompare.append(op)

def const_op(name, op, pop=0, push=1):
    def_op(l, name, op, pop, push)
    hasconst.append(op)

def free_op(name, op, pop=0, push=1):
    def_op(l, name, op, pop, push)
    hasfree.append(op)

def jabs_op(name, op, pop=0, push=0):
    def_op(l, name, op, pop, push)
    hasjabs.append(op)

def jrel_op(name, op, pop=0, push=0):
    def_op(l, name, op, pop, push)
    hasjrel.append(op)

def local_op(name, op, pop=0, push=1):
    def_op(l, name, op, pop, push)
    haslocal.append(op)

def nargs_op(name, op, pop=-2, push=-2):
    def_op(l, name, op, pop, push)
    hasnargs.append(op)

# Instruction opcodes for compiled code
# Blank lines correspond to available opcodes

#        OP NAME           OPCODE POP PUSH
#-----------------------------------------
def_op(l, 'STOP_CODE',             0,  0,  0)
def_op(l, 'POP_TOP',               1,  1,  0)
def_op(l, 'ROT_TWO',               2,  2,  2)
def_op(l, 'ROT_THREE',             3,  3,  3)
def_op(l, 'DUP_TOP',               4,  0,  1)
def_op(l, 'ROT_FOUR',              5,  4,  4)

def_op(l, 'UNARY_POSITIVE',       10,  1,  1)
def_op(l, 'UNARY_NEGATIVE',       11,  1,  1)
def_op(l, 'UNARY_NOT',            12,  1,  1)
def_op(l, 'UNARY_CONVERT',        13,  1,  1)

def_op(l, 'UNARY_INVERT',         15,  1,  1)

def_op(l, 'BINARY_POWER',         19,  2,  1)

def_op(l, 'BINARY_MULTIPLY',      20,  2,  1)
def_op(l, 'BINARY_DIVIDE',        21,  2,  1)
def_op(l, 'BINARY_MODULO',        22,  2,  1)
def_op(l, 'BINARY_ADD',           23,  2,  1)
def_op(l, 'BINARY_SUBTRACT',      24,  2,  1)
def_op(l, 'BINARY_SUBSCR',        25,  2,  1)
def_op(l, 'BINARY_FLOOR_DIVIDE',  26,  2,  1)
def_op(l, 'BINARY_TRUE_DIVIDE',   27,  2,  1)
def_op(l, 'INPLACE_FLOOR_DIVIDE', 28,  2,  1)
def_op(l, 'INPLACE_TRUE_DIVIDE',  29,  2,  1)

def_op(l, 'SLICE+0',              30,  1,  1)
def_op(l, 'SLICE+1',              31,  2,  1)
def_op(l, 'SLICE+2',              32,  2,  1)
def_op(l, 'SLICE+3',              33,  3,  1)

def_op(l, 'STORE_SLICE+0',        40,  2,  0)
def_op(l, 'STORE_SLICE+1',        41,  3,  0)
def_op(l, 'STORE_SLICE+2',        42,  3,  0)
def_op(l, 'STORE_SLICE+3',        43,  4,  0)

def_op(l, 'DELETE_SLICE+0',       50,  1,  0)
def_op(l, 'DELETE_SLICE+1',       51,  2,  0)
def_op(l, 'DELETE_SLICE+2',       52,  2,  0)
def_op(l, 'DELETE_SLICE+3',       53,  3,  0)

def_op(l, 'INPLACE_ADD',          55,  2,  1)
def_op(l, 'INPLACE_SUBTRACT',     56,  2,  1)
def_op(l, 'INPLACE_MULTIPLY',     57,  2,  1)
def_op(l, 'INPLACE_DIVIDE',       58,  2,  1)
def_op(l, 'INPLACE_MODULO',       59,  2,  1)
def_op(l, 'STORE_SUBSCR',         60,  2,  1)
def_op(l, 'DELETE_SUBSCR',        61,  2,  0)

def_op(l, 'BINARY_LSHIFT',        62,  2,  1)
def_op(l, 'BINARY_RSHIFT',        63,  2,  1)
def_op(l, 'BINARY_AND',           64,  2,  1)
def_op(l, 'BINARY_XOR',           65,  2,  1)
def_op(l, 'BINARY_OR',            66,  2,  1)
def_op(l, 'INPLACE_POWER',        67,  2,  1)
def_op(l, 'GET_ITER',             68,  1,  1)

def_op(l, 'PRINT_EXPR',           70,  1,  0)
def_op(l, 'PRINT_ITEM',           71,  1,  0)
def_op(l, 'PRINT_NEWLINE',        72,  1,  0)
def_op(l, 'PRINT_ITEM_TO',        73,  1,  0)
def_op(l, 'PRINT_NEWLINE_TO',     74,  1,  0)
def_op(l, 'INPLACE_LSHIFT',       75,  2,  1)
def_op(l, 'INPLACE_RSHIFT',       76,  2,  1)
def_op(l, 'INPLACE_AND',          77,  2,  1)
def_op(l, 'INPLACE_XOR',          78,  2,  1)
def_op(l, 'INPLACE_OR',           79,  2,  1)
def_op(l, 'BREAK_LOOP',           80,  0,  0)

def_op(l, 'LOAD_LOCALS',          82,  0,  1)
def_op(l, 'RETURN_VALUE',         83,  1,  0)
def_op(l, 'IMPORT_STAR',          84,  1,  0)
def_op(l, 'EXEC_STMT',            85,  3,  0)
def_op(l, 'YIELD_VALUE',          86,  1,  1)

def_op(l, 'POP_BLOCK',            87,  0,  0)
def_op(l, 'END_FINALLY',          88,  1,  0)
def_op(l, 'BUILD_CLASS',          89,  3,  0)

HAVE_ARGUMENT = 90              # Opcodes from here have an argument:

name_op(l, 'STORE_NAME',           90,  1,  0)  # Operand is in name list
name_op(l, 'DELETE_NAME',          91,  0,  0)      # ""
varargs_op(l, 'UNPACK_SEQUENCE',   92, -1,  1)  # Number of tuple items
jrel_op('FOR_ITER',             93, -1, -1)

name_op(l, 'STORE_ATTR',           95,  2,  0)  # Operand is in name list
name_op(l, 'DELETE_ATTR',          96,  1,  0)  # ""
name_op(l, 'STORE_GLOBAL',         97,  1,  0)  # ""
name_op(l, 'DELETE_GLOBAL',        98,  0,  0)  # ""
def_op(l, 'DUP_TOPX',             99,  1, -1)  # number of items to duplicate
const_op('LOAD_CONST',         100,  0,  1)  # Operand is in const list
name_op(l, 'LOAD_NAME',           101,  0,  1)  # Operand is in name list
varargs_op(l, 'BUILD_TUPLE',      102, -1,  1)  # Number of tuple items
varargs_op(l, 'BUILD_LIST',       103, -1,  1)  # Number of list items
varargs_op(l, 'BUILD_MAP',        104, -1,  1)  # Always zero for now
name_op(l, 'LOAD_ATTR',           105,  1,  1)  # Operand is in name list
compare_op('COMPARE_OP',       106,  2,  1)  # Comparison operator

name_op(l, 'IMPORT_NAME',       107,  2,  1) # Operand is in name list
name_op(l, 'IMPORT_FROM',       108,  0,  1) # Operand is in name list

jrel_op('JUMP_FORWARD',        110,  0,  0)  # Number of bytes to skip
jrel_op('JUMP_IF_FALSE',       111,  1,  1)  # ""
jrel_op('JUMP_IF_TRUE',        112,  1,  1)  # ""
jabs_op('JUMP_ABSOLUTE',       113,  0,  0)  # Target byte offset from beginning of code

name_op(l, 'LOAD_GLOBAL',      116,  0,  1)  # Operand is in name list

jabs_op('CONTINUE_LOOP',       119,  0,  0)  # Target address
jrel_op('SETUP_LOOP',          120,  0,  0)  # Distance to target address
jrel_op('SETUP_EXCEPT',        121,  0,  0)  # ""
jrel_op('SETUP_FINALLY',       122,  0,  0)  # ""

local_op('LOAD_FAST',          124,  0,  1)  # Local variable number
local_op('STORE_FAST',         125,  1,  0)  # Local variable number
local_op('DELETE_FAST',        126)    # Local variable number

def_op(l, 'RAISE_VARARGS',     130, -1,  0)   # Number of raise arguments (1, 2, or 3)
nargs_op('CALL_FUNCTION',      131, -1,  1)   # #args + (#kwargs << 8)

def_op(l, 'MAKE_FUNCTION',     132, -1,  1)   # Number of args with default values
varargs_op(l, 'BUILD_SLICE',   133, -1,  1)   # Number of items

def_op(l, 'MAKE_CLOSURE',      134, -1,  1)
free_op('LOAD_CLOSURE',        135,  0,  1)
free_op('LOAD_DEREF',          136,  0,  1)
free_op('STORE_DEREF',         137,  1,  0)

nargs_op('CALL_FUNCTION_VAR',  140, -1,  1)   # #args + (#kwargs << 8)
nargs_op('CALL_FUNCTION_KW',   141, -1,  1)   # #args + (#kwargs << 8)
nargs_op('CALL_FUNCTION_VAR_KW', 142, -1, 1)  # #args + (#kwargs << 8)

def_op(l, 'EXTENDED_ARG', 143)
EXTENDED_ARG = 143

fields2copy = """cmp_op hasjabs""".split()

def dump_opcodes(opmap):
    """Utility for dumping opcodes"""
    op2name = {}
    for k in opmap.keys():
        op2name[opmap[k]] = k
    for i in sorted(op2name.keys()):
        print("%-3s %s" % (str(i), op2name[i]))
