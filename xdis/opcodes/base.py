# (C) Copyright 2017 by Rocky Bernstein
"""
Common routines for entering and classifiying
opcodes
"""

cmp_op = ('<', '<=', '==', '!=', '>', '>=', 'in', 'not in', 'is',
        'is not', 'exception match', 'BAD')

def compare_op(l, name, op, pop=2, push=1):
    def_op(l, name, op, pop, push)
    l['hascompare'].append(op)

def const_op(l, name, op, pop=0, push=1):
    def_op(l, name, op, pop, push)
    l['hasconst'].append(op)

def def_op(l, op_name, opcode, pop=-2, push=-2):
    l['opname'][opcode] = op_name
    l['opmap'][op_name] = opcode
    l['oppush'][opcode] = push
    l['oppop'][opcode] = pop

def free_op(l, name, op, pop=0, push=1):
    def_op(l, name, op, pop, push)
    l['hasfree'].append(op)

def jabs_op(l, name, op, pop=0, push=0):
    def_op(l, name, op, pop, push)
    l['hasjabs'].append(op)

def jrel_op(l, name, op, pop=0, push=0):
    def_op(l, name, op, pop, push)
    l['hasjrel'].append(op)

def local_op(l, name, op, pop=0, push=1):
    def_op(l, name, op, pop, push)
    l['haslocal'].append(op)

def name_op(l, op_name, op_code, pop=-2, push=-2):
    def_op(l, op_name, op_code, push, pop)
    l['hasname'].append(op_code)

def nargs_op(l, name, op, pop=-2, push=-2):
    def_op(l, name, op, pop, push)
    l['hasnargs'].append(op)

def rm_op(l, name, op):
    # opname is an array, so we need to keep the position in there.
    l['opname'][op] = '<%s>' % op

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

def varargs_op(l, op_name, op_code, pop=-1, push=1):
    def_op(l, op_name, op_code, pop, push)
    l['hasvargs'].append(op_code)
