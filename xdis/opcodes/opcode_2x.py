"""
CPython core set of bytecode opcodes based on version 2.3

This is used in scanner (bytecode disassembly) and parser (Python grammar).

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
hasnargs = []

opmap = {}
opname = [''] * 256
for op in range(256): opname[op] = '<%r>' % (op,)
del op

def _def_op(name, op):
    opname[op] = name
    opmap[name] = op

def name_op(name, op):
    _def_op(name, op)
    hasname.append(op)

def jrel_op(name, op):
    _def_op(name, op)
    hasjrel.append(op)

def jabs_op(name, op):
    _def_op(name, op)
    hasjabs.append(op)


# Instruction opcodes for compiled code
# Blank lines correspond to available opcodes

_def_op('STOP_CODE', 0)
_def_op('POP_TOP', 1)
_def_op('ROT_TWO', 2)
_def_op('ROT_THREE', 3)
_def_op('DUP_TOP', 4)
_def_op('ROT_FOUR', 5)

_def_op('UNARY_POSITIVE', 10)
_def_op('UNARY_NEGATIVE', 11)
_def_op('UNARY_NOT', 12)
_def_op('UNARY_CONVERT', 13)

_def_op('UNARY_INVERT', 15)

_def_op('BINARY_POWER', 19)

_def_op('BINARY_MULTIPLY', 20)
_def_op('BINARY_DIVIDE', 21)
_def_op('BINARY_MODULO', 22)
_def_op('BINARY_ADD', 23)
_def_op('BINARY_SUBTRACT', 24)
_def_op('BINARY_SUBSCR', 25)
_def_op('BINARY_FLOOR_DIVIDE', 26)
_def_op('BINARY_TRUE_DIVIDE', 27)
_def_op('INPLACE_FLOOR_DIVIDE', 28)
_def_op('INPLACE_TRUE_DIVIDE', 29)

_def_op('SLICE+0', 30)
_def_op('SLICE+1', 31)
_def_op('SLICE+2', 32)
_def_op('SLICE+3', 33)

_def_op('STORE_SLICE+0', 40)
_def_op('STORE_SLICE+1', 41)
_def_op('STORE_SLICE+2', 42)
_def_op('STORE_SLICE+3', 43)

_def_op('DELETE_SLICE+0', 50)
_def_op('DELETE_SLICE+1', 51)
_def_op('DELETE_SLICE+2', 52)
_def_op('DELETE_SLICE+3', 53)

_def_op('INPLACE_ADD', 55)
_def_op('INPLACE_SUBTRACT', 56)
_def_op('INPLACE_MULTIPLY', 57)
_def_op('INPLACE_DIVIDE', 58)
_def_op('INPLACE_MODULO', 59)
_def_op('STORE_SUBSCR', 60)
_def_op('DELETE_SUBSCR', 61)

_def_op('BINARY_LSHIFT', 62)
_def_op('BINARY_RSHIFT', 63)
_def_op('BINARY_AND', 64)
_def_op('BINARY_XOR', 65)
_def_op('BINARY_OR', 66)
_def_op('INPLACE_POWER', 67)
_def_op('GET_ITER', 68)

_def_op('PRINT_EXPR', 70)
_def_op('PRINT_ITEM', 71)
_def_op('PRINT_NEWLINE', 72)
_def_op('PRINT_ITEM_TO', 73)
_def_op('PRINT_NEWLINE_TO', 74)
_def_op('INPLACE_LSHIFT', 75)
_def_op('INPLACE_RSHIFT', 76)
_def_op('INPLACE_AND', 77)
_def_op('INPLACE_XOR', 78)
_def_op('INPLACE_OR', 79)
_def_op('BREAK_LOOP', 80)

_def_op('LOAD_LOCALS', 82)
_def_op('RETURN_VALUE', 83)
_def_op('IMPORT_STAR', 84)
_def_op('EXEC_STMT', 85)
_def_op('YIELD_VALUE', 86)

_def_op('POP_BLOCK', 87)
_def_op('END_FINALLY', 88)
_def_op('BUILD_CLASS', 89)

HAVE_ARGUMENT = 90              # Opcodes from here have an argument:

name_op('STORE_NAME', 90)       # Index in name list
name_op('DELETE_NAME', 91)      # ""
_def_op('UNPACK_SEQUENCE', 92)   # Number of tuple items
jrel_op('FOR_ITER', 93)

name_op('STORE_ATTR', 95)       # Index in name list
name_op('DELETE_ATTR', 96)      # ""
name_op('STORE_GLOBAL', 97)     # ""
name_op('DELETE_GLOBAL', 98)    # ""
_def_op('DUP_TOPX', 99)          # number of items to duplicate
_def_op('LOAD_CONST', 100)       # Index in const list
hasconst.append(100)
name_op('LOAD_NAME', 101)       # Index in name list
_def_op('BUILD_TUPLE', 102)      # Number of tuple items
_def_op('BUILD_LIST', 103)       # Number of list items
_def_op('BUILD_MAP', 104)        # Always zero for now
name_op('LOAD_ATTR', 105)       # Index in name list
_def_op('COMPARE_OP', 106)       # Comparison operator
hascompare.append(106)

name_op('IMPORT_NAME', 107)     # Index in name list
name_op('IMPORT_FROM', 108)     # Index in name list

jrel_op('JUMP_FORWARD', 110)    # Number of bytes to skip
jrel_op('JUMP_IF_FALSE', 111)   # ""
jrel_op('JUMP_IF_TRUE', 112)    # ""
jabs_op('JUMP_ABSOLUTE', 113)   # Target byte offset from beginning of code

name_op('LOAD_GLOBAL', 116)     # Index in name list

jabs_op('CONTINUE_LOOP', 119)   # Target address
jrel_op('SETUP_LOOP', 120)      # Distance to target address
jrel_op('SETUP_EXCEPT', 121)    # ""
jrel_op('SETUP_FINALLY', 122)   # ""

_def_op('LOAD_FAST', 124)        # Local variable number
haslocal.append(124)
_def_op('STORE_FAST', 125)       # Local variable number
haslocal.append(125)
_def_op('DELETE_FAST', 126)      # Local variable number
haslocal.append(126)

_def_op('RAISE_VARARGS', 130)    # Number of raise arguments (1, 2, or 3)
_def_op('CALL_FUNCTION', 131)    # #args + (#kwargs << 8)
hasnargs.append(131)

_def_op('MAKE_FUNCTION', 132)    # Number of args with default values
_def_op('BUILD_SLICE', 133)      # Number of items

_def_op('MAKE_CLOSURE', 134)
_def_op('LOAD_CLOSURE', 135)
hasfree.append(135)

_def_op('LOAD_DEREF', 136)
hasfree.append(136)
_def_op('STORE_DEREF', 137)
hasfree.append(137)

_def_op('CALL_FUNCTION_VAR', 140)     # #args + (#kwargs << 8)
hasnargs.append(140)

_def_op('CALL_FUNCTION_KW', 141)      # #args + (#kwargs << 8)
hasnargs.append(141)

_def_op('CALL_FUNCTION_VAR_KW', 142)  # #args + (#kwargs << 8)
hasnargs.append(142)

_def_op('EXTENDED_ARG', 143)
EXTENDED_ARG = 143

fields2copy = """cmp_op hasjabs""".split()

def def_op(opname, opmap, name, op):
    opname[op] = name
    opmap[name] = op

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

    assert l['opmap'][name] == op
    del l['opmap'][name]

def dump_opcodes(opmap):
    """Utility for dumping opcodes"""
    op2name = {}
    for k in opmap.keys():
        op2name[opmap[k]] = k
    for i in sorted(op2name.keys()):
        print("%-3s %s" % (str(i), op2name[i]))

# Remove some methods so no importers are tempted to use it.
del _def_op, name_op, jrel_op, jabs_op
