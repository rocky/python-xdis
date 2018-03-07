# (C) Copyright 2017 by Rocky Bernstein
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

from copy import deepcopy
from xdis.bytecode import (
    findlinestarts, findlabels, get_jump_targets,
    get_jump_target_maps)
from xdis import wordcode
from xdis import IS_PYPY, PYTHON_VERSION

if PYTHON_VERSION < 2.4:
    from sets import Set as set
    frozenset = set

cmp_op = ('<', '<=', '==', '!=', '>', '>=', 'in', 'not-in', 'is',
        'is-not', 'exception-match', 'BAD')

# Opcodes greater than 90 take an instruction operand or "argument"
# as opcode.py likes to call it.
HAVE_ARGUMENT = 90

fields2copy = """
hascompare hascondition
hasconst hasfree hasjabs hasjrel haslocal
hasname hasnargs hasvargs oppop oppush
nofollow
""".split()

def init_opdata(l, from_mod, version=None, is_pypy=False):
    """Sets up a number of the structures found in Python's
    opcode.py. Python opcode.py routines assign attributes to modules.
    In order to do this in a modular way here, the local dictionary
    for the module is passed.
    """

    if version:
        l['python_version'] = version
    l['is_pypy'] = is_pypy
    l['cmp_op'] = cmp_op
    l['HAVE_ARGUMENT'] = HAVE_ARGUMENT
    if version <= 3.5:
        l['findlinestarts'] = findlinestarts
        l['findlabels']     = findlabels
        l['get_jump_targets'] = get_jump_targets
        l['get_jump_target_maps']  = get_jump_target_maps
    else:
        l['findlinestarts'] = wordcode.findlinestarts
        l['findlabels']     = wordcode.findlabels
        l['get_jump_targets'] = wordcode.get_jump_targets
        l['get_jump_target_maps']  = wordcode.get_jump_target_maps

    l['opmap'] = deepcopy(from_mod.opmap)
    l['opname'] = deepcopy(from_mod.opname)

    for field in fields2copy:
        l[field] = list(getattr(from_mod, field))


def compare_op(l, name, op, pop=2, push=1):
    def_op(l, name, op, pop, push)
    l['hascompare'].append(op)

def conditional_op(l, name, op):
    l['hascompare'].append(op)

def const_op(l, name, op, pop=0, push=1):
    def_op(l, name, op, pop, push)
    l['hasconst'].append(op)

def def_op(l, op_name, opcode, pop=-2, push=-2, fallthrough=True):
    l['opname'][opcode] = op_name
    l['opmap'][op_name] = opcode
    l['oppush'][opcode] = push
    l['oppop'][opcode] = pop
    if not fallthrough:
        l['nofollow'].append(opcode)

def free_op(l, name, op, pop=0, push=1):
    def_op(l, name, op, pop, push)
    l['hasfree'].append(op)

def jabs_op(l, name, op, pop=0, push=0, conditional=False, fallthrough=True):
    def_op(l, name, op, pop, push, fallthrough=fallthrough)
    l['hasjabs'].append(op)
    if conditional:
        l['hascondition'].append(op)

def jrel_op(l, name, op, pop=0, push=0, conditional=False, fallthrough=True):
    def_op(l, name, op, pop, push)
    l['hasjrel'].append(op)
    if conditional:
        l['hascondition'].append(op)

def local_op(l, name, op, pop=0, push=1):
    def_op(l, name, op, pop, push)
    l['haslocal'].append(op)

def name_op(l, op_name, op_code, pop=-2, push=-2):
    def_op(l, op_name, op_code, pop, push)
    l['hasname'].append(op_code)

def nargs_op(l, name, op, pop=-2, push=-2):
    def_op(l, name, op, pop, push)
    l['hasnargs'].append(op)

def rm_op(l, name, op):
    """Remove an opcode. This is used when basing a new Python release off
    of another one, and there is an opcode that is in the old release
    that was removed in the new release.
    We are pretty aggressive about removing traces of the op.
    """

    # opname is an array, so we need to keep the position in there.
    l['opname'][op] = '<%s>' % op

    if op in l['hasconst']:
       l['hasconst'].remove(op)
    if op in l['hascompare']:
       l['hascompare'].remove(op)
    if op in l['hascondition']:
       l['hascondition'].remove(op)
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
    if op in l['nofollow']:
       l['nofollow'].remove(op)

    assert l['opmap'][name] == op
    del l['opmap'][name]

def varargs_op(l, op_name, op_code, pop=-1, push=1):
    def_op(l, op_name, op_code, pop, push)
    l['hasvargs'].append(op_code)

# Some of the convoluted code below reflects some of the
# many Python idiocies over the years.

def finalize_opcodes(l):

    # Not sure why, but opcode.py address has opcode.EXTENDED_ARG
    # as well as opmap['EXTENDED_ARG']
    l['EXTENDED_ARG'] = l['opmap']['EXTENDED_ARG']

    # In Python 3.6+ this is 8, but we expect
    # those opcodes to set that
    if 'EXTENDED_ARG_SHIFT' not in l:
        l['EXTENDED_ARG_SHIFT'] = 16

    l['ARG_MAX_VALUE'] = (1 << l['EXTENDED_ARG_SHIFT']) - 1
    l['EXTENDED_ARG']  = l['opmap']['EXTENDED_ARG']

    l['opmap'] = fix_opcode_names(l['opmap'])

    # Now add in the attributes into the module
    for op in l['opmap']:
        l[op] = l['opmap'][op]
    l['JUMP_OPs'] = frozenset(l['hasjrel'] + l['hasjabs'])
    l['NOFOLLOW'] = frozenset(l['nofollow'])
    opcode_check(l)
    return

def fix_opcode_names(opmap):
    """
    Python stupidly named some OPCODES with a + which prevents using opcode name
    directly as an attribute, e.g. SLICE+3. So we turn that into SLICE_3 so we
    can then use opcode_23.SLICE_3.  Later Python's fix this.
    """
    return dict([(k.replace('+', '_'), v)
                  for (k, v) in opmap.items()])


def update_pj3(g, l):
    g.update({'PJIF': l['opmap']['POP_JUMP_IF_FALSE']})
    g.update({'PJIT': l['opmap']['POP_JUMP_IF_TRUE']})
    update_sets(l)

def update_pj2(g, l):
    g.update({'PJIF': l['opmap']['JUMP_IF_FALSE']})
    g.update({'PJIT': l['opmap']['JUMP_IF_TRUE']})
    update_sets(l)

def update_sets(l):
    l['COMPARE_OPS']     = frozenset(l['hascompare'])
    l['CONDITION_OPS']   = frozenset(l['hascondition'])
    l['CONST_OPS']       = frozenset(l['hasconst'])
    l['FREE_OPS']        = frozenset(l['hasfree'])
    l['JREL_OPS']        = frozenset(l['hasjrel'])
    l['JABS_OPS']        = frozenset(l['hasjabs'])
    l['JUMP_UNCONDITONAL']    = frozenset([l['opmap']['JUMP_ABSOLUTE'],
                                           l['opmap']['JUMP_FORWARD']])
    l['LOOP_OPS']        = frozenset([l['opmap']['SETUP_LOOP']])
    l['LOCAL_OPS']       = frozenset(l['haslocal'])
    l['JUMP_OPS']        = (l['JABS_OPS']
                              | l['JREL_OPS']
                              | l['LOOP_OPS']
                              | l['JUMP_UNCONDITONAL'])
    l['NAME_OPS']        = frozenset(l['hasname'])
    l['NARGS_OPS']       = frozenset(l['hasnargs'])
    l['VARGS_OPS']       = frozenset(l['hasvargs'])

def format_extended_arg(arg):
    return str(arg * (1 << 16))

def format_extended_arg36(arg):
    return str(arg * (1 << 8))

def opcode_check(l):
    """When the version of Python we are running happens
    to have the same opcode set as the opcode we are
    importing, we perform checks to make sure our opcode
    set matches exactly.
    """
    # Python 2.6 reports 2.6000000000000001
    if (abs(PYTHON_VERSION - l['python_version']) <= 0.01
        and IS_PYPY == l['is_pypy']):
        try:
            import dis
            opmap = fix_opcode_names(dis.opmap)
            # print(set(opmap.items()) - set(l['opmap'].items()))
            # print(set(l['opmap'].items()) - set(opmap.items()))

            assert all(item in opmap.items() for item in l['opmap'].items())
            assert all(item in l['opmap'].items() for item in opmap.items())
        except:
            import sys

def dump_opcodes(opmap):
    """Utility for dumping opcodes"""
    op2name = {}
    for k in opmap.keys():
        op2name[opmap[k]] = k
    for i in sorted(op2name.keys()):
        print("%-3s %s" % (str(i), op2name[i]))
