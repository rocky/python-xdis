#  Copyright (c) 2018 by Rocky Bernstein
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

"""Python bytecode and instruction classes
Extracted from Python 3 dis module but generalized to
allow running on Python 2.
"""

import re, sys, types
from xdis import PYTHON3, PYTHON_VERSION

from xdis.namedtuple24 import namedtuple

from xdis.util import get_code_object, code2num, num2code, format_code_info

if PYTHON3:
    from io import StringIO
    from functools import reduce
else:
    from StringIO import StringIO


_have_code = (types.MethodType, types.FunctionType, types.CodeType, type)

def extended_arg_val(opc, val):
    return val << opc.EXTENDED_ARG_SHIFT

# This is modified from Python 3.6's dis
def unpack_opargs_bytecode(code, opc):
    extended_arg = 0
    try:
        n = len(code)
    except TypeError:
        code = code.co_code
        n = len(code)

    offset = 0
    while offset < n:
        prev_offset = offset
        op = code2num(code, offset)
        offset += 1
        if op_has_argument(op, opc):
            arg = code2num(code, offset) | extended_arg
            if op == opc.EXTENDED_ARG:
                extended_arg = (arg << opc.EXTENDED_ARG_SHIFT)
            else:
                extended_arg = 0
            offset += 2
        else:
            arg = None
        yield (prev_offset, op, arg)

def findlinestarts(code, dup_lines=False):
    """Find the offsets in a byte code which are start of lines in the source.

    Generate pairs (offset, lineno) as described in Python/compile.c.

    """
    if not isinstance(code.co_lnotab, str):
        byte_increments = list(code.co_lnotab[0::2])
        line_increments = list(code.co_lnotab[1::2])
    else:
        byte_increments = [ord(c) for c in code.co_lnotab[0::2]]
        line_increments = [ord(c) for c in code.co_lnotab[1::2]]

    lastlineno = None
    lineno = code.co_firstlineno
    addr = 0
    for byte_incr, line_incr in zip(byte_increments, line_increments):
        if byte_incr:
            if (lineno != lastlineno or
                (dup_lines and 0 < byte_incr < 255)):
                yield (addr, lineno)
                lastlineno = lineno
                pass
            addr += byte_incr
            pass
        lineno += line_incr
    if (lineno != lastlineno or
        (dup_lines and 0 < byte_incr < 255)):
        yield (addr, lineno)

def offset2line(offset, linestarts):
    """linestarts is expected to be a *list) of (offset, line number)
    where both offset and line number are in increasing order.
    Return the closes line number at or below the offset.
    If offset is less than the first line number given in linestarts,
    return line number 0.
    """
    if len(linestarts) == 0 or offset < linestarts[0][0]:
        return 0
    low = 0
    high = len(linestarts) - 1
    mid = (low + high + 1) // 2
    while low <= high:
        if linestarts[mid][0] > offset:
            high = mid - 1
        elif linestarts[mid][0] < offset:
            low = mid + 1
        else:
            return linestarts[mid][1]
        mid = (low + high + 1) // 2
        pass
    # Not found. Return closest position below
    if mid >= len(linestarts):
        return linestarts[len(linestarts)-1][1]
    return linestarts[high][1]

def get_jump_targets(code, opc):
    """Returns a list of instruction offsets in the supplied bytecode
    which are the targets of some sort of jump instruction.
    """
    offsets = []
    for offset, op, arg in unpack_opargs_bytecode(code, opc):
        if arg is not None:
            jump_offset = -1
            if op in opc.JREL_OPS:
                jump_offset = offset + 3 + arg
            elif op in opc.JABS_OPS:
                jump_offset = arg
            if jump_offset >= 0:
                if jump_offset not in offsets:
                    offsets.append(jump_offset)
    return offsets

def get_jump_target_maps(code, opc):
    """Returns a dictionary where the key is an offset and the values are
    a list of instruction offsets which can get run before that
    instruction. This includes jump instructions as well as non-jump
    instructions. Therefore, the keys of the dictionary are reachible
    instructions. The values of the dictionary may be useful in control-flow
    analysis.
    """
    offset2prev = {}
    prev_offset = -1
    for offset, op, arg in unpack_opargs_bytecode(code, opc):
        if prev_offset >= 0:
            prev_list = offset2prev.get(offset, [])
            prev_list.append(prev_offset)
            offset2prev[offset] = prev_list
        if op in opc.NOFOLLOW:
            prev_offset = -1
        else:
            prev_offset = offset
        if arg is not None:
            jump_offset = -1
            if op in opc.JREL_OPS:
                jump_offset = offset + 3 + arg
            elif op in opc.JABS_OPS:
                jump_offset = arg
            if jump_offset >= 0:
                prev_list = offset2prev.get(jump_offset, [])
                prev_list.append(offset)
                offset2prev[jump_offset] = prev_list
    return offset2prev


findlabels = get_jump_targets

def _get_const_info(const_index, const_list):
    """Helper to get optional details about const references

       Returns the dereferenced constant and its repr if the constant
       list is defined.
       Otherwise returns the constant index and its repr().
    """
    argval = const_index
    if const_list is not None:
        argval = const_list[const_index]

    # float values nan and inf are not directly representable in Python at least
    # before 3.5 and even there it is via a library constant.
    # So we will canonicalize their representation as float('nan') and float('inf')
    if isinstance(argval, float) and str(argval) in frozenset(['nan', '-nan', 'inf', '-inf']):
        return argval, "float('%s')" % argval
    return argval, repr(argval)

def _get_name_info(name_index, name_list):
    """Helper to get optional details about named references

       Returns the dereferenced name as both value and repr if the name
       list is defined.
       Otherwise returns the name index and its repr().
    """
    argval = name_index
    if (name_list is not None
        # PyPY seems to "optimize" out constant names,
        # so we need for that:
        and name_index < len(name_list)):
        argval = name_list[name_index]
        argrepr = argval
    else:
        argrepr = repr(argval)
    return argval, argrepr

def get_instructions_bytes(bytecode, opc, varnames=None, names=None, constants=None,
                           cells=None, linestarts=None, line_offset=0):
    """Iterate over the instructions in a bytecode string.

    Generates a sequence of Instruction namedtuples giving the details of each
    opcode.  Additional information about the code's runtime environment
    (e.g. variable names, constants) can be specified using optional
    arguments.

    """
    labels = opc.findlabels(bytecode, opc)
    extended_arg = 0

    # FIXME: We really need to distinguish 3.6.0a1 from 3.6.a3.
    # See below FIXME
    if opc.python_version >= 3.6:
        python_36 = True
    else:
        python_36 = False

    starts_line = None
    # enumerate() is not an option, since we sometimes process
    # multiple elements on a single pass through the loop
    n = len(bytecode)
    i = 0
    extended_arg = 0
    while i < n:
        op = code2num(bytecode, i)

        offset = i
        if linestarts is not None:
            starts_line = linestarts.get(i, None)
            if starts_line is not None:
                starts_line += line_offset
        is_jump_target = i in labels
        i = i+1
        arg = None
        argval = None
        argrepr = ''
        has_arg = op_has_argument(op, opc)
        optype = None
        if has_arg:
            if python_36:
                arg = code2num(bytecode, i) | extended_arg
                if op == opc.EXTENDED_ARG:
                    extended_arg = (arg << 8)
                else:
                    extended_arg = 0
                # FIXME: Python 3.6.0a1 is 2, for 3.6.a3 we have 1
                i += 1
            else:
                arg = code2num(bytecode, i) + code2num(bytecode, i+1)*256 + extended_arg
                i += 2
                if op == opc.EXTENDED_ARG:
                    extended_arg = arg*65536
                else:
                    extended_arg = 0

            #  Set argval to the dereferenced value of the argument when
            #  availabe, and argrepr to the string representation of argval.
            #    disassemble_bytes needs the string repr of the
            #    raw name index for LOAD_GLOBAL, LOAD_CONST, etc.
            argval = arg
            if op in opc.CONST_OPS:
                argval, argrepr = _get_const_info(arg, constants)
                optype = 'const'
            elif op in opc.NAME_OPS:
                argval, argrepr = _get_name_info(arg, names)
                optype = 'name'
            elif op in opc.JREL_OPS:
                argval = i + arg
                argrepr = "to " + repr(argval)
                optype = 'jrel'
            elif op in opc.JABS_OPS:
                argval = arg
                argrepr = "to " + repr(argval)
                optype = 'jabs'
            elif op in opc.LOCAL_OPS:
                argval, argrepr = _get_name_info(arg, varnames)
                optype = 'local'
            elif op in opc.COMPARE_OPS:
                argval = opc.cmp_op[arg]
                argrepr = argval
                optype = 'compare'
            elif op in opc.FREE_OPS:
                argval, argrepr = _get_name_info(arg, cells)
                optype = 'free'
            elif op in opc.NARGS_OPS:
                optype = 'nargs'
                if not python_36:
                    argrepr = ("%d positional, %d keyword pair" %
                               (code2num(bytecode, i-2), code2num(bytecode, i-1)))
            # This has to come after hasnargs. Some are in both?
            elif op in opc.VARGS_OPS:
                optype = 'vargs'
            if hasattr(opc, 'opcode_arg_fmt') and opc.opname[op] in opc.opcode_arg_fmt:
                argrepr = opc.opcode_arg_fmt[opc.opname[op]](arg)
        elif python_36:
            i += 1

        opname = opc.opname[op]
        inst_size = op_size(op, opc)
        yield Instruction(opname, op, optype, inst_size, arg, argval, argrepr,
                          has_arg, offset, starts_line, is_jump_target)

def op_has_argument(op, opc):
    return op >= opc.HAVE_ARGUMENT

def next_offset(op, opc, offset):
    return offset + instruction_size(op, opc)

# FIXME: this would better be called an instr_size
# since it is about instructions, not opcodes
def instruction_size(op, opc):
    """For a given opcode, `op`, in opcode module `opc`,
    return the size, in bytes, of an `op` instruction.

    This is the size of the opcode (1 byte) and any operand it has. In
    Python before version 3.6 this will be either 1 or 3 bytes.  In
    Python 3.6 or later, it is 2 bytes or a "word"."""
    if op < opc.HAVE_ARGUMENT:
        if opc.version >= 3.6:
            return 2
        else:
            return 1
    else:
        if opc.version >= 3.6:
            return 2
        else:
            return 3

# Compatiblity
op_size = instruction_size

_Instruction = namedtuple("_Instruction",
     "opname opcode optype inst_size arg argval argrepr has_arg offset starts_line is_jump_target")

def from_traceback(cls, tb):
    """ Construct a Bytecode from the given traceback """
    while tb.tb_next:
        tb = tb.tb_next
    return cls(tb.tb_frame.f_code, current_offset=tb.tb_lasti)

class Instruction(_Instruction):
    """Details for a bytecode operation

       Defined fields:
         opname - human readable name for operation
         opcode - numeric code for operation
         optype - opcode classification. One of
            compare, const, free, jabs, jrel, local, name, nargs
         inst_size - number of bytes the instruction occupies
         arg - numeric argument to operation (if any), otherwise None
         argval - resolved arg value (if known), otherwise same as arg
         argrepr - human readable description of operation argument
         has_arg - True opcode takes an argument. In that case,
                   argval and argepr will have that value. False
                   if this opcode doesn't take an argument. In that case,
                   don't look at argval or argrepr.
         offset - start index of operation within bytecode sequence
         starts_line - line started by this opcode (if any), otherwise None
         is_jump_target - True if other code jumps to here, otherwise False
    """
    # FIXME: remove has_arg from initialization but keep it as a field.

    def disassemble(self, lineno_width=3, mark_as_current=False, asm_format=False):
        """Format instruction details for inclusion in disassembly output

        *lineno_width* sets the width of the line number field (0 omits it)
        *mark_as_current* inserts a '-->' marker arrow as part of the line
        """
        fields = []
        if asm_format:
            indexed_operand = set(['name', 'local', 'compare', 'free'])
        # Column: Source code line number
        if lineno_width:
            if self.starts_line is not None:
                if asm_format:
                    lineno_fmt = "%%%dd:\n" % lineno_width
                    fields.append(lineno_fmt % self.starts_line)
                    fields.append(' ' * (lineno_width))
                    if self.is_jump_target:
                        fields.append(' ' * (lineno_width-1))
                else:
                    lineno_fmt = "%%%dd:" % lineno_width
                    fields.append(lineno_fmt % self.starts_line)
            else:
                fields.append(' ' * (lineno_width+1))
        # Column: Current instruction indicator
        if mark_as_current and not asm_format:
            fields.append('-->')
        else:
            fields.append('   ')
        # Column: Jump target marker
        if self.is_jump_target:
            if not asm_format:
                fields.append('>>')
            else:
                fields = ["L%d:\n" % self.offset] + fields
                if not self.starts_line:
                    fields.append(' ')
        else:
            fields.append('  ')
        # Column: Instruction offset from start of code sequence
        if not asm_format:
            fields.append(repr(self.offset).rjust(4))

        # Column: Opcode name
        fields.append(self.opname.ljust(20))
        # Column: Opcode argument
        if self.arg is not None:
            argrepr = self.argrepr
            if asm_format:
                if self.optype == 'jabs':
                    fields.append('L' + str(self.arg))
                elif self.optype == 'jrel':
                    argval = self.offset + self.arg + self.inst_size
                    fields.append('L' + str(argval))
                elif self.optype in indexed_operand:
                    fields.append('(%s)' % argrepr)
                    argrepr = None
                elif (self.optype == 'const'
                      and not re.search('\s', argrepr)):
                    fields.append('(%s)' % argrepr)
                    argrepr = None
                else:
                    fields.append(repr(self.arg))
            else:
                fields.append(repr(self.arg).rjust(6))
            # Column: Opcode argument details
            if argrepr:
                fields.append('(%s)' % argrepr)
                pass
            pass
        return ' '.join(fields).rstrip()

    # FIXME: figure out how to do disassemble passing in opnames

class Bytecode(object):
    """The bytecode operations of a piece of code

    Instantiate this with a function, method, string of code, or a code object
    (as returned by compile()).

    Iterating over this yields the bytecode operations as Instruction instances.
    """
    def __init__(self, x, opc, first_line=None, current_offset=None,
                 dup_lines=False):
        self.codeobj = co = get_code_object(x)
        if first_line is None:
            self.first_line = co.co_firstlineno
            self._line_offset = 0
        else:
            self.first_line = first_line
            self._line_offset = first_line - co.co_firstlineno
        self._cell_names = co.co_cellvars + co.co_freevars
        self._linestarts = dict(opc.findlinestarts(co, dup_lines=dup_lines))
        self._original_object = x
        self.opc = opc
        self.opnames = opc.opname
        self.current_offset = current_offset

    def __iter__(self):
        co = self.codeobj
        return get_instructions_bytes(co.co_code, self.opc, co.co_varnames, co.co_names,
                                      co.co_consts, self._cell_names,
                                      self._linestarts,
                                      line_offset=self._line_offset)

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__,
                                 self._original_object)

    def info(self):
        """Return formatted information about the code object."""
        return format_code_info(self.codeobj, self.opc.version)

    def dis(self, asm_format=False):
        """Return a formatted view of the bytecode operations."""
        co = self.codeobj
        if self.current_offset is not None:
            offset = self.current_offset
        else:
            offset = -1
        output = StringIO()
        self.disassemble_bytes(co.co_code, varnames=co.co_varnames,
                               names=co.co_names, constants=co.co_consts,
                               cells=self._cell_names,
                               linestarts=self._linestarts,
                               line_offset=self._line_offset,
                               file=output,
                               lasti=offset,
                               asm_format=asm_format)
        return output.getvalue()

    def disassemble_bytes(self, code, lasti=-1, varnames=None, names=None,
                          constants=None, cells=None, linestarts=None,
                          file=sys.stdout, line_offset=0,
                          asm_format=False):
        # Omit the line number column entirely if we have no line number info
        show_lineno = linestarts is not None
        # TODO?: Adjust width upwards if max(linestarts.values()) >= 1000?
        if show_lineno:
            lineno_width = 3
        else:
            lineno_width = 0
        for instr in get_instructions_bytes(code, self.opc, varnames, names,
                                             constants, cells, linestarts,
                                             line_offset=line_offset):
            new_source_line = (show_lineno and
                               instr.starts_line is not None and
                               instr.offset > 0)
            if new_source_line:
                file.write("\n")
            is_current_instr = instr.offset == lasti
            file.write(instr.disassemble(lineno_width, is_current_instr, asm_format)
                       + "\n")
            pass
        return

    def get_instructions(self, x, first_line=None):
        """Iterator for the opcodes in methods, functions or code

        Generates a series of Instruction named tuples giving the details of
        each operations in the supplied code.

        If *first_line* is not None, it indicates the line number that should
        be reported for the first source line in the disassembled code.
        Otherwise, the source line information (if any) is taken directly from
        the disassembled code object.
        """
        co = get_code_object(x)
        cell_names = co.co_cellvars + co.co_freevars
        linestarts = dict(self.opc.findlinestarts(co))
        if first_line is not None:
            line_offset = first_line - co.co_firstlineno
        else:
            line_offset = 0
        return get_instructions_bytes(co.co_code, self.opc, co.co_varnames,
                                      co.co_names, co.co_consts, cell_names, linestarts,
                                      line_offset)

def list2bytecode(l, opc, varnames, consts):
    """Convert list/tuple of list/tuples to bytecode
    _names_ contains a list of name objects
    """
    bc = []
    for i, opcodes in enumerate(l):
        opname = opcodes[0]
        operands = opcodes[1:]
        if opname not in opc.opname:
            raise TypeError(
                "error at item %d [%s, %s], opcode not valid" %
                (i, opname, operands))
        opcode = opc.opmap[opname]
        bc.append(opcode)
        print(opname, operands)
        gen = [j for j in operands if operands]
        for j in gen:
            if opcode in opc.hasconst:
                thing = consts
            else:
                thing = varnames
            k = list(thing).index(j)
            if k == -1:
                raise TypeError(
                    "operand %s [%s, %s], not found in names" %
                    (i, opname, operands))
            else:
                bc += num2code(k)
                pass
            pass
        pass
    if opc.python_version < 3.0:
        return reduce(lambda a, b: a + chr(b), bc, '')
    else:
        if PYTHON3:
            return bytes(bc)
        elif PYTHON_VERSION < 2.5:
            return reduce(lambda a, b: a + chr(b), bc, '')
        else:
            return bytes(bytearray(bc))


# if __name__ == '__main__':
#     import xdis.opcodes.opcode_27  as opcode_27
#     import xdis.opcodes.opcode_34  as opcode_34
#     import xdis.opcodes.opcode_36  as opcode_36
#     consts = (None, 2)
#     varnames = ('a')
#     instructions = [
#         ('LOAD_CONST', 2),
#         ('STORE_FAST', 'a'),
#         ('LOAD_FAST', 'a'),
#         ('RETURN_VALUE',)
#     ]
#     def f():
#         a = 2
#         return a
#     if PYTHON3:
#         print(f.__code__.co_code)
#     else:
#         print(f.func_code.co_code)

#     bc = list2bytecode(instructions, opcode_27, varnames, consts)
#     print(bc)
#     bc = list2bytecode(instructions, opcode_34, varnames, consts)
#     print(bc)
#     bc = list2bytecode(instructions, opcode_36, varnames, consts)
#     print(bc)
