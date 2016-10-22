"""
CPython core set of bytecode opcodes based on version 2.3

This is used in bytecode disassembly. This is similar to the
opcodes in Python's opcode.py library.
"""

# FIXME: DRY this along the lines of opcode_3x.
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

def _def_op(name, op, pop=-2, push=-2):
    opname[op] = name
    opmap[name] = op
    oppush[op] = push
    oppop[op] = pop

def compare_op(name, op, pop=2, push=1):
    _def_op(name, op, pop, push)
    hascompare.append(op)

def const_op(name, op, pop=0, push=1):
    _def_op(name, op, pop, push)
    hasconst.append(op)

def free_op(name, op, pop=0, push=1):
    _def_op(name, op, pop, push)
    hasfree.append(op)

def jabs_op(name, op, pop=0, push=0):
    _def_op(name, op, pop, push)
    hasjabs.append(op)

def jrel_op(name, op, pop=0, push=0):
    _def_op(name, op, pop, push)
    hasjrel.append(op)

def local_op(name, op, pop=0, push=1):
    _def_op(name, op, pop, push)
    haslocal.append(op)

def name_op(name, op, pop=-2, push=-2):
    _def_op(name, op, pop, push)
    hasname.append(op)

def nargs_op(name, op, pop=-2, push=-2):
    _def_op(name, op, pop, push)
    hasnargs.append(op)

def varargs_op(name, op, pop=-1, push=1):
    _def_op(name, op, pop, push)
    hasvargs.append(op)


# Instruction opcodes for compiled code
# Blank lines correspond to available opcodes

 #       OP NAME           OPCODE  POP PUSH
 #-----------------------------------------
_def_op('STOP_CODE',             0,  0,  0)
_def_op('POP_TOP',               1,  1,  0)
_def_op('ROT_TWO',               2,  2,  2)
_def_op('ROT_THREE',             3,  3,  3)
_def_op('DUP_TOP',               4,  1,  2)
_def_op('ROT_FOUR',              5,  4,  4)

_def_op('UNARY_POSITIVE',       10,  1,  1)
_def_op('UNARY_NEGATIVE',       11,  1,  1)
_def_op('UNARY_NOT',            12,  1,  1)
_def_op('UNARY_CONVERT',        13,  1,  1)

_def_op('UNARY_INVERT',         15,  1,  1)

_def_op('BINARY_POWER',         19,  2,  1)

_def_op('BINARY_MULTIPLY',      20,  2,  1)
_def_op('BINARY_DIVIDE',        21,  2,  1)
_def_op('BINARY_MODULO',        22,  2,  1)
_def_op('BINARY_ADD',           23,  2,  1)
_def_op('BINARY_SUBTRACT',      24,  2,  1)
_def_op('BINARY_SUBSCR',        25,  2,  1)
_def_op('BINARY_FLOOR_DIVIDE',  26,  2,  1)
_def_op('BINARY_TRUE_DIVIDE',   27,  2,  1)
_def_op('INPLACE_FLOOR_DIVIDE', 28,  2,  1)
_def_op('INPLACE_TRUE_DIVIDE',  29,  2,  1)

_def_op('SLICE+0',              30,  1,  1)
_def_op('SLICE+1',              31,  2,  1)
_def_op('SLICE+2',              32,  2,  1)
_def_op('SLICE+3',              33,  3,  1)

_def_op('STORE_SLICE+0',        40,  2,  0)
_def_op('STORE_SLICE+1',        41,  3,  0)
_def_op('STORE_SLICE+2',        42,  3,  0)
_def_op('STORE_SLICE+3',        43,  4,  0)

_def_op('DELETE_SLICE+0',       50,  1,  0)
_def_op('DELETE_SLICE+1',       51,  2,  0)
_def_op('DELETE_SLICE+2',       52,  2,  0)
_def_op('DELETE_SLICE+3',       53,  3,  0)

_def_op('INPLACE_ADD',          55,  2,  1)
_def_op('INPLACE_SUBTRACT',     56,  2,  1)
_def_op('INPLACE_MULTIPLY',     57,  2,  1)
_def_op('INPLACE_DIVIDE',       58,  2,  1)
_def_op('INPLACE_MODULO',       59,  2,  1)
_def_op('STORE_SUBSCR',         60,  2,  1)
_def_op('DELETE_SUBSCR',        61,  2,  0)

_def_op('BINARY_LSHIFT',        62,  2,  1)
_def_op('BINARY_RSHIFT',        63,  2,  1)
_def_op('BINARY_AND',           64,  2,  1)
_def_op('BINARY_XOR',           65,  2,  1)
_def_op('BINARY_OR',            66,  2,  1)
_def_op('INPLACE_POWER',        67,  2,  1)
_def_op('GET_ITER',             68,  1,  1)

_def_op('PRINT_EXPR',           70,  1,  0)
_def_op('PRINT_ITEM',           71,  1,  0)
_def_op('PRINT_NEWLINE',        72,  1,  0)
_def_op('PRINT_ITEM_TO',        73,  1,  0)
_def_op('PRINT_NEWLINE_TO',     74,  1,  0)
_def_op('INPLACE_LSHIFT',       75,  2,  1)
_def_op('INPLACE_RSHIFT',       76,  2,  1)
_def_op('INPLACE_AND',          77,  2,  1)
_def_op('INPLACE_XOR',          78,  2,  1)
_def_op('INPLACE_OR',           79,  2,  1)
_def_op('BREAK_LOOP',           80,  0,  0)

_def_op('LOAD_LOCALS',          82,  0,  1)
_def_op('RETURN_VALUE',         83,  1,  0)
_def_op('IMPORT_STAR',          84,  1,  0)
_def_op('EXEC_STMT',            85,  3,  0)
_def_op('YIELD_VALUE',          86,  1,  1)

_def_op('POP_BLOCK',            87,  0,  0)
_def_op('END_FINALLY',          88,  1,  0)
_def_op('BUILD_CLASS',          89,  3,  0)

HAVE_ARGUMENT = 90              # Opcodes from here have an argument:

name_op('STORE_NAME',           90,  1,  0)  # Index in name list
name_op('DELETE_NAME',          91,  0,  0)      # ""
varargs_op('UNPACK_SEQUENCE',   92, -1,  1)  # Number of tuple items
jrel_op('FOR_ITER',             93, -1, -1)

name_op('STORE_ATTR',           95,  2,  0)  # Index in name list
name_op('DELETE_ATTR',          96,  1,  0)  # ""
name_op('STORE_GLOBAL',         97,  1,  0)  # ""
name_op('DELETE_GLOBAL',        98,  0,  0)  # ""
_def_op('DUP_TOPX',             99,  1, -1)  # number of items to duplicate
const_op('LOAD_CONST',         100,  0,  1)  # Index in const list
name_op('LOAD_NAME',           101,  0,  1)  # Index in name list
varargs_op('BUILD_TUPLE',      102, -1,  1)  # Number of tuple items
varargs_op('BUILD_LIST',       103, -1,  1)  # Number of list items
varargs_op('BUILD_MAP',        104, -1,  1)  # Always zero for now
name_op('LOAD_ATTR',           105,  1,  1)  # Index in name list
compare_op('COMPARE_OP',       106,  2,  1)  # Comparison operator

name_op('IMPORT_NAME',         107,  0,  1)  # Index in name list
name_op('IMPORT_FROM',         108,  1,  1)  # Index in name list

jrel_op('JUMP_FORWARD',        110,  0,  0)  # Number of bytes to skip
jrel_op('JUMP_IF_FALSE',       111,  1,  1)  # ""
jrel_op('JUMP_IF_TRUE',        112,  1,  1)  # ""
jabs_op('JUMP_ABSOLUTE',       113,  0,  0)  # Target byte offset from beginning of code

name_op('LOAD_GLOBAL',         116,  0,  1)  # Index in name list

jabs_op('CONTINUE_LOOP',       119,  0,  0)  # Target address
jrel_op('SETUP_LOOP',          120,  0,  0)  # Distance to target address
jrel_op('SETUP_EXCEPT',        121,  0,  0)  # ""
jrel_op('SETUP_FINALLY',       122,  0,  0)  # ""

local_op('LOAD_FAST',          124,  0,  1)  # Local variable number
local_op('STORE_FAST',         125,  1,  0)  # Local variable number
local_op('DELETE_FAST',        126)    # Local variable number

_def_op('RAISE_VARARGS',       130, -1,  0)   # Number of raise arguments (1, 2, or 3)
nargs_op('CALL_FUNCTION',      131, -1,  1)   # #args + (#kwargs << 8)

_def_op('MAKE_FUNCTION',       132, -1,  1)   # Number of args with default values
varargs_op('BUILD_SLICE',      133, -1,  1)   # Number of items

_def_op('MAKE_CLOSURE',        134, -1,  1)
free_op('LOAD_CLOSURE',        135,  0,  1)
free_op('LOAD_DEREF',          136,  0,  1)
free_op('STORE_DEREF',         137,  1,  0)

nargs_op('CALL_FUNCTION_VAR',  140, -1,  1)   # #args + (#kwargs << 8)
nargs_op('CALL_FUNCTION_KW',   141, -1,  1)   # #args + (#kwargs << 8)
nargs_op('CALL_FUNCTION_VAR_KW', 142, -1, 1)  # #args + (#kwargs << 8)

_def_op('EXTENDED_ARG', 143)
EXTENDED_ARG = 143

fields2copy = """cmp_op hasjabs""".split()

def def_op(opname, opmap, name, op, pop=-2, push=-2):
    opname[op] = name
    opmap[name] = op
    oppush[op] = push
    oppop[op] = pop

def rm_op(name, op, l):
    # opname is an array, so we need to keep the position in there.
    l['opname'][op] = ''

    if op in l['hasconst']:
       l['hasconst'].remove(op)
    if op in l['hascompare']:
       l['hascompare'].remove(op)
    if op in l['hasfree']:
       l['hasfree'].remove(op)
    if op in l['hasjabs']:
       l['hasjabs'].remove(op)
    if op in l['hasname']:
       l['hasname'].remove(op)
    if op in l['hasjrel']:
       l['hasjrel'].remove(op)
    if op in l['haslocal']:
       l['haslocal'].remove(op)
    if op in l['hasname']:
       l['hasname'].remove(op)
    if op in l['hasnargs']:
       l['hasnargs'].remove(op)
    if op in l['hasvargs']:
       l['hasvargs'].remove(op)

    assert l['opmap'][name] == op
    del l['opmap'][name]

def dump_opcodes(opmap):
    """Utility for dumping opcodes"""
    op2name = {}
    for k in opmap.keys():
        op2name[opmap[k]] = k
    for i in sorted(op2name.keys()):
        print("%-3s %s" % (str(i), op2name[i]))
