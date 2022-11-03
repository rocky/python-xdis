#  Copyright (c) 2018-2022 by Rocky Bernstein
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

import sys, types
from xdis.namedtuple24 import namedtuple

from xdis.cross_dis import (
    get_code_object,
    format_code_info,
    instruction_size,
    op_has_argument,
)
from xdis.instruction import Instruction
from xdis.util import code2num, num2code

from StringIO import StringIO

_have_code = (types.MethodType, types.FunctionType, types.CodeType, type)


def extended_arg_val(opc, val):
    """Return the adjusted value of an extended argument operand.
    """
    return val << opc.EXTENDED_ARG_SHIFT

def get_jump_val(jump_arg, version):
    if version[:2] >= (3, 10):
        return jump_arg * 2
    else:
        return jump_arg

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
        return linestarts[len(linestarts) - 1][1]
    return linestarts[high][1]


def _get_const_info(const_index, const_list):
    """Helper to get optional details about const references

    Returns the dereferenced constant and its repr if the constant
    list is defined.
    Otherwise, returns the constant index and its repr().
    """
    argval = const_index
    if const_list is not None:
        argval = const_list[const_index]

    # float values nan and inf are not directly representable in Python at least
    # before 3.5 and even there it is via a library constant.
    # So we will canonicalize their representation as float('nan') and float('inf')
    if isinstance(argval, float) and str(argval) in frozenset(
        ["nan", "-nan", "inf", "-inf"]
    ):
        return argval, "float('%s')" % argval
    return argval, repr(argval)


def _get_name_info(name_index, name_list):
    """Helper to get optional details about named references

    Returns the dereferenced name as both value and repr if the name
    list is defined.
    Otherwise, returns the name index and its repr().
    """
    argval = name_index
    if (
        name_list is not None
        # PyPY seems to "optimize" out constant names,
        # so we need for that:
        and name_index < len(name_list)
    ):
        argval = name_list[name_index]
        argrepr = argval
    else:
        argrepr = repr(argval)
    return argval, argrepr


def get_instructions_bytes(
    bytecode,
    opc,
    varnames=None,
    names=None,
    constants=None,
    cells=None,
    linestarts=None,
    line_offset=0,
):
    """Iterate over the instructions in a bytecode string.

    Generates a sequence of Instruction namedtuples giving the details of each
    opcode.  Additional information about the code's runtime environment
    (e.g. variable names, constants) can be specified using optional
    arguments.

    """
    labels = opc.findlabels(bytecode, opc)
    # label_maps = get_jump_target_maps(bytecode, opc)
    extended_arg = 0

    # FIXME: We really need to distinguish 3.6.0a1 from 3.6.a3.
    # See below FIXME
    if opc.python_version >= (3, 6):
        python_36 = True
    else:
        python_36 = False

    starts_line = None
    # enumerate() is not an option, since we sometimes process
    # multiple elements on a single pass through the loop
    n = len(bytecode)
    i = 0
    extended_arg_count = 0
    extended_arg = 0
    extended_arg_size = instruction_size(opc.EXTENDED_ARG, opc)
    while i < n:
        op = code2num(bytecode, i)

        offset = i
        if linestarts is not None:
            starts_line = linestarts.get(i, None)
            if starts_line is not None:
                starts_line += line_offset
        if i in labels:
            is_jump_target = True
        else:
            is_jump_target = False

        i += 1
        arg = None
        argval = None
        argrepr = ""
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
                arg = (
                    code2num(bytecode, i)
                    + code2num(bytecode, i + 1) * 256
                    + extended_arg
                )
                i += 2
                if op == opc.EXTENDED_ARG:
                    extended_arg = arg*65536
                else:
                    extended_arg = 0

            #  Set argval to the dereferenced value of the argument when
            #  available, and argrepr to the string representation of argval.
            #    disassemble_bytes needs the string repr of the
            #    raw name index for LOAD_GLOBAL, LOAD_CONST, etc.
            argval = arg
            if op in opc.CONST_OPS:
                argval, argrepr = _get_const_info(arg, constants)
                optype = "const"
            elif op in opc.NAME_OPS:
                argval, argrepr = _get_name_info(arg, names)
                optype = "name"
            elif op in opc.JREL_OPS:
                argval = i + get_jump_val(arg, opc.python_version)
                argrepr = "to " + repr(argval)
                optype = "jrel"
            elif op in opc.JABS_OPS:
                argval = get_jump_val(arg, opc.python_version)
                argrepr = "to " + repr(argval)
                optype = "jabs"
            elif op in opc.LOCAL_OPS:
                argval, argrepr = _get_name_info(arg, varnames)
                optype = "local"
            elif op in opc.COMPARE_OPS:
                argval = opc.cmp_op[arg]
                argrepr = argval
                optype = "compare"
            elif op in opc.FREE_OPS:
                argval, argrepr = _get_name_info(arg, cells)
                optype = "free"
            elif op in opc.NARGS_OPS:
                optype = "nargs"
                if not (
                    python_36
                    or opc.opname[op] in ("RAISE_VARARGS", "DUP_TOPX", "MAKE_FUNCTION")
                ):
                    argrepr = "%d positional, %d named" % (
                        code2num(bytecode, i - 2),
                        code2num(bytecode, i - 1),
                    )
            # This has to come after hasnargs. Some are in both?
            elif op in opc.VARGS_OPS:
                optype = "vargs"
            if hasattr(opc, "opcode_arg_fmt") and opc.opname[op] in opc.opcode_arg_fmt:
                argrepr = opc.opcode_arg_fmt[opc.opname[op]](arg)
        elif python_36:
            i += 1

        opname = opc.opname[op]
        inst_size = instruction_size(op, opc) + (extended_arg_count * extended_arg_size)
        # fallthrough = op not in opc.nofollow
        yield Instruction(
            opname,
            op,
            optype,
            inst_size,
            arg,
            argval,
            argrepr,
            has_arg,
            offset,
            starts_line,
            is_jump_target,
            extended_arg_count != 0,
        )
        # fallthrough)
        if op == opc.EXTENDED_ARG:
            extended_arg_count = extended_arg_count + 1
        else:
            extended_arg_count = 0


def next_offset(op, opc, offset):
    """Returns the bytecode offset for the instruction that is assumed to
    start at `offset` and has opcode `op`. opc contains information for the
    bytecode version of that we should be using.
    """
    return offset + instruction_size(op, opc)


class Bytecode(object):
    """Bytecode operations involving a Python code object.

    Instantiate this with a function, method, string of code, or a code object
    (as returned by compile()).

    Iterating over these yields the bytecode operations as Instruction instances.
    """

    def __init__(self, x, opc, first_line=None, current_offset=None, dup_lines=True):
        self.codeobj = co = get_code_object(x)
        self._line_offset = 0
        self._cell_names = ()
        if opc.version > 1.5:
            if first_line is None:
                self.first_line = co.co_firstlineno
            else:
                self.first_line = first_line
                self._line_offset = first_line - co.co_firstlineno
            if opc.version > 2.0:
                self._cell_names = co.co_cellvars + co.co_freevars
                pass
            pass

        self._linestarts = dict(opc.findlinestarts(co, dup_lines=dup_lines))
        self._original_object = x
        self.opc = opc
        self.opnames = opc.opname
        self.current_offset = current_offset

    def __iter__(self):
        co = self.codeobj
        return get_instructions_bytes(
            co.co_code,
            self.opc,
            co.co_varnames,
            co.co_names,
            co.co_consts,
            self._cell_names,
            self._linestarts,
            line_offset=self._line_offset,
        )

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self._original_object)

    @classmethod
    def from_traceback(cls, tb):
        """Construct a Bytecode from the given traceback"""
        while tb.tb_next:
            tb = tb.tb_next
        return cls(tb.tb_frame.f_code, current_offset=tb.tb_lasti)

    def info(self):
        """Return formatted information about the code object."""
        return format_code_info(self.codeobj, self.opc.version_tuple)

    def dis(self, asm_format="classic"):
        """Return a formatted view of the bytecode operations."""
        co = self.codeobj
        if self.current_offset is not None:
            offset = self.current_offset
        else:
            offset = -1
        output = StringIO()
        if self.opc.version > 2.0:
            cells = self._cell_names
            linestarts = self._linestarts
        else:
            cells = None
            linestarts = None

        self.disassemble_bytes(
            co.co_code,
            varnames=co.co_varnames,
            names=co.co_names,
            constants=co.co_consts,
            cells=cells,
            linestarts=linestarts,
            line_offset=self._line_offset,
            file=output,
            lasti=offset,
            asm_format=asm_format,
        )
        return output.getvalue()

    def distb(self, tb=None):
        """Disassemble a traceback (default: last traceback)."""
        if tb is None:
            try:
                tb = sys.last_traceback
            except AttributeError:
                raise RuntimeError("no last traceback to disassemble")
            while tb.tb_next:
                tb = tb.tb_next
        self.disassemble(tb.tb_frame.f_code, tb.tb_lasti)

    def disassemble_bytes(
        self,
        code,
        lasti=-1,
        varnames=None,
        names=None,
        constants=None,
        cells=None,
        linestarts=None,
        file=sys.stdout,
        line_offset=0,
        asm_format="classic",
    ):
        # Omit the line number column entirely if we have no line number info
        show_lineno = linestarts is not None or self.opc.version_tuple < (2, 3)

        # Old Python's use "SET_LINENO" to set a line number
        set_lineno_number = 0
        last_was_set_lineno = False

        # TODO?: Adjust width upwards if max(linestarts.values()) >= 1000?
        if show_lineno:
            lineno_width = 3
        else:
            lineno_width = 0
        instructions = []
        for instr in get_instructions_bytes(
            code,
            self.opc,
            varnames,
            names,
            constants,
            cells,
            linestarts,
            line_offset=line_offset,
        ):

            # Python 1.x into early 2.0 uses SET_LINENO
            if last_was_set_lineno:
                instr = Instruction(
                    instr.opname,
                    instr.opcode,
                    instr.optype,
                    instr.inst_size,
                    instr.arg,
                    instr.argval,
                    instr.argrepr,
                    instr.has_arg,
                    instr.offset,
                    set_lineno_number,  # this is the only field that changes
                    instr.is_jump_target,
                    instr.has_extended_arg,
                )
            last_was_set_lineno = False
            if instr.opname == "SET_LINENO":
                set_lineno_number = instr.argval
                last_was_set_lineno = True

            instructions.append(instr)
            new_source_line = (
                show_lineno and instr.starts_line is not None and instr.offset > 0
            )
            if new_source_line:
                file.write("\n")
            is_current_instr = instr.offset == lasti
            file.write(
                instr.disassemble(
                    self.opc, lineno_width, is_current_instr, asm_format, instructions
                )
                + "\n"
            )

            # Python bytecode before 1.4 has a RESERVE_FAST instruction that
            # store STORE_FAST and LOAD_FAST instructions in a different area
            # currently we can't track names in this area, but instead use
            # locals and hope the two are the same.
            if instr.opname == "RESERVE_FAST":
                file.write(
                    "# Warning: subsequent LOAD_FAST and STORE_FAST after RESERVE_FAST are "
                    "inaccurate here in Python before 1.5\n"
                )
            pass
        return

    def get_instructions(self, x, first_line=None):
        """Iterator for the opcodes in methods, functions or code

        Generates a series of Instruction named tuples giving the details of
        each operation in the supplied code.

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
        return get_instructions_bytes(
            co.co_code,
            self.opc,
            co.co_varnames,
            co.co_names,
            co.co_consts,
            cell_names,
            linestarts,
            line_offset,
        )


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
                "error at item %d [%s, %s], opcode not valid" % (i, opname, operands)
            )
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
                    "operand %s [%s, %s], not found in names" % (i, opname, operands)
                )
            else:
                bc += num2code(k)
                pass
            pass
        pass

    return reduce(lambda a, b: a + chr(b), bc, "")


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
