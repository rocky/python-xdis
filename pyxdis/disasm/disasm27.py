# Copyright (c) 2015, 2016 by Rocky Bernstein
# Copyright (c) 2000-2002 by hartmut Goebel <h.goebel@crazy-compilers.com>
"""
Python 2.7 bytecode disassembler

This sets up opcodes Python's 3.5 and calls a generalized
disassemble routine for Python 3.
"""


from __future__ import print_function

import dis, inspect
from collections import namedtuple
from array import array

from pyxdis.code import iscode
import pyxdis.disassemble as disasm

class Disassembler27(disasm.Disassembler):
    def __init__(self):
        disasm.Disassembler.__init__(self, 2.7)

    def disassemble(self, co, classname=None, code_objects={}):
        """
        Like disassemble but doesn't try to adjust any opcodes.
        """

        # Container for insns
        insns = []

        customize = {}
        Instruction = self.Instruction # shortcut

        n = self.setup_code(co)
        self.build_lines_data(co, n)

        # self.lines contains (block,addrLastInstr)
        if classname:
            classname = '_' + classname.lstrip('_') + '__'

            def unmangle(name):
                if name.startswith(classname) and name[-2:] != '__':
                    return name[len(classname) - 2:]
                return name

            free = [ unmangle(name) for name in (co.co_cellvars + co.co_freevars) ]
            names = [ unmangle(name) for name in co.co_names ]
            varnames = [ unmangle(name) for name in co.co_varnames ]
        else:
            free = co.co_cellvars + co.co_freevars
            names = co.co_names
            varnames = co.co_varnames

        extended_arg = 0
        for offset in self.op_range(0, n):
            op = self.code[offset]
            op_name = self.opname[op]

            oparg = None; pattr = None
            if op >= HAVE_ARGUMENT:
                oparg = self.get_argument(offset) + extended_arg
                extended_arg = 0
                if op == EXTENDED_ARG:
                    extended_arg = oparg * scan.L65536
                    continue
                if op in hasconst:
                    pattr = co.co_consts[oparg]
                elif op in hasname:
                    pattr = names[oparg]
                elif op in hasjrel:
                    pattr = repr(offset + 3 + oparg)
                elif op in hasjabs:
                    pattr = repr(oparg)
                elif op in haslocal:
                    pattr = varnames[oparg]
                elif op in hascompare:
                    pattr = cmp_op[oparg]
                elif op in hasfree:
                    pattr = free[oparg]

            if offset in self.linestartoffsets:
                linestart = self.linestartoffsets[offset]
            else:
                linestart = None

            insns.append(Token(op_name, oparg, pattr, offset, linestart))
            pass
        return insns, customize

    def setup_code(self, co):
        """
        Creates Python-independent bytecode structure (byte array) in
        self.code and records previous instruction in self.prev
        The size of self.code is returned
        """
        self.code = array('B', co.co_code)

        n = -1
        for i in self.op_range(0, len(self.code)):
            if self.opname[self.code[i]] in ('RETURN_VALUE', 'END_FINALLY'):
                n = i + 1
                pass
            pass
        assert n > -1, "Didn't find RETURN_VALUE or END_FINALLY FINALLY"
        self.code = array('B', co.co_code[:n])

        return n

    def build_prev_op(self, n):
        self.prev = [0]
        # mapping addresses of instruction & argument
        for i in self.op_range(0, n):
            op = self.code[i]
            self.prev.append(i)
            if op >= HAVE_ARGUMENT:
                self.prev.append(i)
                self.prev.append(i)
                pass
            pass

    def build_lines_data(self, co, n):
        """
        Initializes self.lines and self.linesstartoffsets
        """
        self.lines = []
        linetuple = namedtuple('linetuple', ['l_no', 'next'])

        # linestarts is a tuple of (offset, line number).
        # Turn that in a has that we can index
        linestarts = list(dis.findlinestarts(co))
        self.linestartoffsets = {}
        for offset, lineno in linestarts:
            self.linestartoffsets[offset] = lineno

        j = 0
        (prev_start_byte, prev_line_no) = linestarts[0]
        for (start_byte, line_no) in linestarts[1:]:
            while j < start_byte:
                self.lines.append(linetuple(prev_line_no, start_byte))
                j += 1
            prev_line_no = start_byte
        while j < n:
            self.lines.append(linetuple(prev_line_no, n))
            j+=1
        return

    def build_stmt_indices(self):
        code = self.code
        start = 0
        end = len(code)

        stmt_opcodes = set([
            SETUP_LOOP, BREAK_LOOP, CONTINUE_LOOP,
            SETUP_FINALLY, END_FINALLY, SETUP_EXCEPT, SETUP_WITH,
            POP_BLOCK, STORE_FAST, DELETE_FAST, STORE_DEREF,
            STORE_GLOBAL, DELETE_GLOBAL, STORE_NAME, DELETE_NAME,
            STORE_ATTR, DELETE_ATTR, STORE_SUBSCR, DELETE_SUBSCR,
            RETURN_VALUE, RAISE_VARARGS, POP_TOP,
            PRINT_EXPR, PRINT_ITEM, PRINT_NEWLINE, PRINT_ITEM_TO, PRINT_NEWLINE_TO,
            STORE_SLICE_0, STORE_SLICE_1, STORE_SLICE_2, STORE_SLICE_3,
            DELETE_SLICE_0, DELETE_SLICE_1, DELETE_SLICE_2, DELETE_SLICE_3,
            JUMP_ABSOLUTE, EXEC_STMT,
        ])

        stmt_opcode_seqs = [(PJIF, JF), (PJIF, JA), (PJIT, JF), (PJIT, JA)]

        designator_ops = set([
            STORE_FAST, STORE_NAME, STORE_GLOBAL, STORE_DEREF, STORE_ATTR,
            STORE_SLICE_0, STORE_SLICE_1, STORE_SLICE_2, STORE_SLICE_3,
            STORE_SUBSCR, UNPACK_SEQUENCE, JA
        ])

        prelim = self.all_instr(start, end, stmt_opcodes)

        stmts = self.stmts = set(prelim)
        pass_stmts = set()
        for seq in stmt_opcode_seqs:
            for i in self.op_range(start, end-(len(seq)+1)):
                match = True
                for elem in seq:
                    if elem != code[i]:
                        match = False
                        break
                    i += self.op_size(code[i])

                if match:
                    i = self.prev[i]
                    stmts.add(i)
                    pass_stmts.add(i)

        if pass_stmts:
            stmt_list = list(stmts)
            stmt_list.sort()
        else:
            stmt_list = prelim
        last_stmt = -1
        self.next_stmt = []
        slist = self.next_stmt = []
        i = 0
        for s in stmt_list:
            if code[s] == JA and s not in pass_stmts:
                target = self.get_target(s)
                if target > s or self.lines[last_stmt].l_no == self.lines[s].l_no:
                    stmts.remove(s)
                    continue
                j = self.prev[s]
                while code[j] == JA:
                    j = self.prev[j]
                if code[j] == LIST_APPEND: # list comprehension
                    stmts.remove(s)
                    continue
            elif code[s] == POP_TOP and code[self.prev[s]] == ROT_TWO:
                stmts.remove(s)
                continue
            elif code[s] in designator_ops:
                j = self.prev[s]
                while code[j] in designator_ops:
                    j = self.prev[j]
                if code[j] == FOR_ITER:
                    stmts.remove(s)
                    continue
            last_stmt = s
            slist += [s] * (s-i)
            i = s
        slist += [end] * (end-len(slist))

    def next_except_jump(self, start):
        '''
        Return the next jump that was generated by an except SomeException:
        construct in a try...except...else clause or None if not found.
        '''

        if self.code[start] == DUP_TOP:
            except_match = self.first_instr(start, len(self.code), POP_JUMP_IF_FALSE)
            if except_match:
                jmp = self.prev[self.get_target(except_match)]
                self.ignore_if.add(except_match)
                self.not_continue.add(jmp)
                return jmp

        count_END_FINALLY = 0
        count_SETUP_ = 0
        for i in self.op_range(start, len(self.code)):
            op = self.code[i]
            if op == END_FINALLY:
                if count_END_FINALLY == count_SETUP_:
                    assert self.code[self.prev[i]] in (JA, JF, RETURN_VALUE)
                    self.not_continue.add(self.prev[i])
                    return self.prev[i]
                count_END_FINALLY += 1
            elif op in (SETUP_EXCEPT, SETUP_WITH, SETUP_FINALLY):
                count_SETUP_ += 1

    def find_jump_targets(self):
        '''
        Detect all offsets in a byte code which are jump targets.

        Return the list of offsets.

        This procedure is modelled after dis.findlabels(), but here
        for each target the number of jumps are counted.
        '''

        n = len(self.code)
        self.structs = [{'type':  'root',
                           'start': 0,
                           'end':   n-1}]
        self.loops = []  # All loop entry points
        self.fixed_jumps = {} # Map fixed jumps to their real destination
        self.ignore_if = set()
        self.build_stmt_indices()

        # Containers filled by detect_structure()
        self.not_continue = set()
        self.return_end_ifs = set()

        targets = {}
        for i in self.op_range(0, n):
            op = self.code[i]

            # Determine structures and fix jumps in Python versions
            # since 2.3
            self.detect_structure(i, op)

            if op >= HAVE_ARGUMENT:
                label = self.fixed_jumps.get(i)
                oparg = self.code[i+1] + self.code[i+2] * 256
                if label is None:
                    if op in hasjrel and op != FOR_ITER:
                        label = i + 3 + oparg
                    elif op in hasjabs:
                        if op in (JUMP_IF_FALSE_OR_POP, JUMP_IF_TRUE_OR_POP):
                            if (oparg > i):
                                label = oparg

                if label is not None and label != -1:
                    targets[label] = targets.get(label, []) + [i]
            elif op == END_FINALLY and i in self.fixed_jumps:
                label = self.fixed_jumps[i]
                targets[label] = targets.get(label, []) + [i]
        return targets

if __name__ == "__main__":
    co = inspect.currentframe().f_code
    insns, customize = Disassembler27().disassemble(co)
    for t in insns:
        print(t)
    pass
