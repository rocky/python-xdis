# (C) Copyright 2020-2021, 2023-2025 by Rocky Bernstein
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

# Here, we are more closely modeling Python's ``dis`` module organization.
# However, it appears that Python's names and code have been copied a bit heavily from
# earlier versions of xdis (and without attribution).

from typing import List

from xdis.util import (
    COMPILER_FLAG_NAMES,
    PYPY_COMPILER_FLAG_NAMES,
    better_repr,
    code2num,
)
from xdis.version_info import IS_GRAAL


def _try_compile(source, name):
    """Attempts to compile the given source, first as an expression and
    then as a statement if the first approach fails.

    Utility function to accept strings in functions that otherwise
    expect code objects
    """
    try:
        c = compile(source, name, "eval")
    except SyntaxError:
        c = compile(source, name, "exec")
    return c


def code_info(x, version_tuple, is_pypy=False):
    """Formatted details of methods, functions, or code."""
    return format_code_info(get_code_object(x), version_tuple, is_pypy=is_pypy)


def get_code_object(x):
    """Helper to handle methods, functions, generators, strings and raw code objects"""
    if hasattr(x, "__func__"):  # Method
        x = x.__func__
    if hasattr(x, "__code__"):  # Function
        x = x.__code__
    elif hasattr(x, "func_code"):  # Function pre 2.7
        x = x.__code__
    elif hasattr(x, "gi_code"):  # Generator
        x = x.gi_code
    elif hasattr(x, "ag_code"):  # ...an asynchronous generator object, or
        x = x.ag_code
    elif hasattr(x, "cr_code"):  # ...a coroutine.
        x = x.cr_code
    # Handle source code.
    if isinstance(x, str):
        x = _try_compile(x, "<disassembly>")
    # By now, if we don't have a code object, we can't disassemble x.
    if hasattr(x, "co_code"):
        return x
    raise TypeError("don't know how to disassemble %s objects" % type(x).__name__)


def _get_cache_size_313(opname: str) -> int:
    _inline_cache_entries = {
        "LOAD_GLOBAL": 4,
        "BINARY_OP": 1,
        "UNPACK_SEQUENCE": 1,
        "COMPARE_OP": 1,
        "CONTAINS_OP": 1,
        "BINARY_SUBSCR": 1,
        "FOR_ITER": 1,
        "LOAD_SUPER_ATTR": 1,
        "LOAD_ATTR": 9,
        "STORE_ATTR": 4,
        "CALL": 3,
        "STORE_SUBSCR": 1,
        "SEND": 1,
        "JUMP_BACKWARD": 1,
        "TO_BOOL": 3,
        "POP_JUMP_IF_TRUE": 1,
        "POP_JUMP_IF_FALSE": 1,
        "POP_JUMP_IF_NONE": 1,
        "POP_JUMP_IF_NOT_NONE": 1,
    }
    return _inline_cache_entries.get(opname, 0)


def findlabels(code, opc):
    if opc.version_tuple < (3, 10) or IS_GRAAL:
        return findlabels_pre_310(code, opc)

    return findlabels_310(code, opc)


def findlabels_310(code: bytes, opc):
    """Returns a list of instruction offsets in the supplied bytecode
    which are the targets of some sort of jump instruction.
    """
    labels = []
    for offset, op, arg in unpack_opargs_bytecode_310(code, opc):
        if arg is not None:
            if op in opc.JREL_OPS:
                if opc.version_tuple >= (3, 11) and opc.opname[op] in ("JUMP_BACKWARD", "JUMP_BACKWARD_NO_INTERRUPT"):
                    arg = -arg
                label = offset + 2 + arg * 2
                # in 3.13 we have to add total cache offsets to label
                if opc.version_tuple >= (3, 13):
                    cachesize = _get_cache_size_313(opc.opname[op])
                    label += 2 * cachesize
            elif op in opc.JABS_OPS:
                label = arg * 2
            else:
                continue
            if label not in labels:
                labels.append(label)
    return labels


def findlabels_pre_310(code, opc):
    """Returns a list of instruction offsets in the supplied bytecode
    which are the targets of some sort of jump instruction.
    """
    offsets = []
    for offset, op, arg in unpack_opargs_bytecode(code, opc):
        if arg is not None:
            jump_offset = -1
            if op in opc.JREL_OPS:
                op_len = op_size(op, opc)
                jump_offset = offset + op_len + arg
            elif op in opc.JABS_OPS:
                jump_offset = arg
            if jump_offset >= 0:
                if jump_offset not in offsets:
                    offsets.append(jump_offset)
    return offsets


# For the `co_lines` attribute, we want to emit the full form, omitting
# the (350, 360, No line number) and empty entries.

NO_LINE_NUMBER = -128


def findlinestarts(code, dup_lines=False):
    """Find the offsets in a byte code which are start of lines in the source.

    Generate pairs (offset, lineno) as described in Python/compile.c.
    """

    if hasattr(code, "co_lines"):
        # Taken from 3.10 findlinestarts
        lastline = None
        for start, _, line in code.co_lines():
            if line is not None and line != lastline:
                lastline = line
                yield start, line

    else:
        lineno_table = code.co_lnotab

        if isinstance(lineno_table, dict):
            # We have an uncompressed line-number table
            # The below could be done with a Python generator, but
            # we want to be Python 2.x compatible.
            for addr, lineno in lineno_table.items():
                yield addr, lineno
            # For 3.8 we have to fall through to the return rather
            # than add raise StopIteration
        elif len(lineno_table) == 0:
            yield 0, code.co_firstlineno
        else:
            if isinstance(lineno_table[0], int):
                byte_increments = list(code.co_lnotab[0::2])
                line_deltas = list(code.co_lnotab[1::2])
            else:
                byte_increments = [ord(c) for c in code.co_lnotab[0::2]]
                line_deltas = [ord(c) for c in code.co_lnotab[1::2]]
            bytecode_len = len(code.co_code)

            lastlineno = None
            lineno = code.co_firstlineno
            offset = 0
            byte_incr = 0
            for byte_incr, line_delta in zip(byte_increments, line_deltas):
                if byte_incr:
                    if lineno != lastlineno or dup_lines and 0 < byte_incr < 255:
                        yield offset, lineno
                        lastlineno = lineno
                        pass
                    if offset >= bytecode_len:
                        # The rest of the ``lnotab byte offsets are past the end of
                        # the bytecode; any line numbers for these have been removed.
                        return
                    offset += byte_incr
                    pass
                if line_delta >= 0x80:
                    # line_deltas is an array of 8-bit *signed* integers
                    line_delta -= 0x100
                lineno += line_delta
            if lineno != lastlineno or (dup_lines and 0 < byte_incr < 255):
                yield offset, lineno

    return


def instruction_size(op, opc):
    """For a given opcode, `op`, in opcode module `opc`,
    return the size, in bytes, of an `op` instruction.

    This is the size of the opcode (one byte) and any operand it has.
    In Python before version 3.6, this will be either 1 or 3 bytes.
    In Python 3.6 or later, it is 2 bytes: a "word"."""
    if op < opc.HAVE_ARGUMENT:
        return 2 if opc.version_tuple >= (3, 6) else 1
    else:
        return 2 if opc.version_tuple >= (3, 6) else 3


# Compatibility
op_size = instruction_size


def show_code(co, version_tuple, file=None, is_pypy=False):
    """Print details of methods, functions, or code to *file*.

    If *file* is not provided, the output is printed on stdout.
    """
    if file is None:
        print(code_info(co, version_tuple, is_pypy=is_pypy))
    else:
        file.write(code_info(co, version_tuple) + "\n")


def op_has_argument(opcode: int, opc) -> bool:
    """
    Return True if `opcode` instruction has an operand.
    """
    return opcode >= opc.HAVE_ARGUMENT


def pretty_flags(flags, is_pypy=False):
    """Return pretty representation of code flags."""
    names = []
    result = "0x%08x" % flags
    for i in range(32):
        flag = 1 << i
        if flags & flag:
            names.append(COMPILER_FLAG_NAMES.get(flag, hex(flag)))
            if is_pypy:
                names.append(PYPY_COMPILER_FLAG_NAMES.get(flag, hex(flag)))
            flags ^= flag
            if not flags:
                break
    else:
        names.append(hex(flags))
    names.reverse()
    return "%s (%s)" % (result, " | ".join(names))


def format_code_info(
    co, version_tuple: tuple, name=None, is_pypy=False, is_graal=False
):
    if not name:
        name = co.co_name
    lines = []

    if not (name == "?" and version_tuple <= (2, 4)):
        lines.append("# Method Name:       %s" % name)

    # Python before version 2.4 and earlier didn't store a name for the main routine.
    # Later versions use "<module>"
    lines.append("# Filename:          %s" % co.co_filename)

    if not is_graal:
        if version_tuple >= (1, 3):
            lines.append("# Argument count:    %s" % co.co_argcount)

        if version_tuple >= (3, 8) and hasattr(co, "co_posonlyargcount"):
            lines.append("# Position-only argument count: %s" % co.co_posonlyargcount)

        if version_tuple >= (3, 0) and hasattr(co, "co_kwonlyargcount"):
            lines.append("# Keyword-only arguments: %s" % co.co_kwonlyargcount)

        pos_argc = co.co_argcount
        if version_tuple >= (1, 3):
            lines.append("# Number of locals:  %s" % co.co_nlocals)
        if version_tuple >= (1, 5):
            lines.append("# Stack size:        %s" % co.co_stacksize)
            pass
        pass
    else:
        pos_argc = 0

    if version_tuple >= (1, 3):
        lines.append(
            "# Flags:             %s" % pretty_flags(co.co_flags, is_pypy=is_pypy)
        )

    if version_tuple >= (1, 5):
        lines.append("# First Line:        %s" % co.co_firstlineno)
    # if co.co_freevars:
    #     lines.append("# Freevars:      %s" % str(co.co_freevars))
    if co.co_consts:
        lines.append("# Constants:")
        for i, c in enumerate(co.co_consts):
            lines.append("# %4d: %s" % (i, better_repr(c)))
    if co.co_names:
        lines.append("# Names:")
        for i_n in enumerate(co.co_names):
            lines.append("# %4d: %s" % i_n)
    if co.co_varnames:
        lines.append("# Varnames:")
        lines.append("#\t%s" % ", ".join(co.co_varnames))
        pass
    if pos_argc > 0:
        lines.append("# Positional arguments:")
        lines.append("#\t%s" % ", ".join(co.co_varnames[:pos_argc]))
        pass
    if len(co.co_varnames) > pos_argc:
        lines.append("# Local variables:")
        for i, n in enumerate(co.co_varnames[pos_argc:]):
            lines.append("# %4d: %s" % (pos_argc + i, n))
    if version_tuple > (2, 0):
        if co.co_freevars:
            lines.append("# Free variables:")
            for i_n in enumerate(co.co_freevars):
                lines.append("# %4d: %s" % i_n)
                pass
            pass
        if co.co_cellvars:
            lines.append("# Cell variables:")
            for i_n in enumerate(co.co_cellvars):
                lines.append("# %4d: %s" % i_n)
                pass
            pass
    return "\n".join(lines)


def format_exception_table(bytecode, version_tuple) -> str:
    if version_tuple < (3, 11) or not hasattr(bytecode, "exception_entries"):
        return ""
    lines: List[str] = ["ExceptionTable:"]
    for entry in bytecode.exception_entries:
        lasti = " lasti" if entry.lasti else ""
        end = entry.end - 2
        lines.append(
            f"  {entry.start} to {end} -> {entry.target} [{entry.depth}]{lasti}"
        )
    return "\n".join(lines)


def extended_arg_val(opc, val):
    return val << opc.EXTENDED_ARG_SHIFT


def unpack_opargs_bytecode_310(code, opc):
    extended_arg = 0
    try:
        n = len(code)
    except TypeError:
        code = code.co_code
        n = len(code)
    for offset in range(0, n, 2):
        op = code2num(code, offset)
        if op_has_argument(op, opc):
            arg = code2num(code, offset + 1) | extended_arg
            extended_arg = extended_arg_val(opc, arg) if op == opc.EXTENDED_ARG else 0
        else:
            arg = None
        yield offset, op, arg


# This is modified from Python 3.6's ``dis`` module
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
            extended_arg = (
                extended_arg_val(opc, arg)
                if hasattr(opc, "EXTENDED_ARG") and op == opc.EXTENDED_ARG
                else 0
            )
            offset += 2
        else:
            arg = None
        yield prev_offset, op, arg


def get_jump_target_maps(code, opc):
    """Returns a dictionary where the key is an offset and the values are
    a list of instruction offsets which can get run before that
    instruction. This includes jump instructions as well as non-jump
    instructions. Therefore, the keys of the dictionary are reachable
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
                op_len = op_size(op, opc)
                jump_offset = offset + op_len + arg
            elif op in opc.JABS_OPS:
                jump_offset = arg
            if jump_offset >= 0:
                prev_list = offset2prev.get(jump_offset, [])
                prev_list.append(offset)
                offset2prev[jump_offset] = prev_list
    return offset2prev


# In CPython, this is C code. We redo this in Python using the
# information in opc.
def xstack_effect(opcode, opc, oparg: int = 0, jump=None):
    """Compute the stack effect of opcode with argument oparg, using
    oppush and oppop tables in opc.

    If the code has a jump target and jump is True, stack_effect()
    will return the stack effect of jumping. If jump is False, it will
    return the stack effect of not jumping. And if jump is None
    (default), it will return the maximal stack effect of both cases.
    """
    version_tuple = opc.version_tuple
    pop, push = opc.oppop[opcode], opc.oppush[opcode]
    opname = opc.opname[opcode]
    if opname in "BUILD_CONST_KEY_MAP" and version_tuple >= (3, 12):
        return -oparg
    if opname == "BUILD_MAP" and version_tuple >= (3, 5):
        return 1 - (2 * oparg)
    elif opname in ("UNPACK_SEQUENCE", "UNPACK_EX") and version_tuple >= (3, 0):
        return push + oparg
    elif opname in (
        "BUILD_LIST",
        "BUILD_SET",
        "BUILD_STRING",
        "BUILD_TUPLE",
    ) and version_tuple >= (3, 12):
        return 1 - oparg
    elif opname in ("BUILD_SLICE") and version_tuple <= (2, 7):
        return -2 if oparg == 3 else -1
    elif opname == "LOAD_ATTR" and version_tuple >= (3, 12):
        return 1 if oparg & 1 else 0
    elif opname == "MAKE_FUNCTION":
        if version_tuple >= (3, 5):
            if 0 <= oparg <= 10:
                if version_tuple == (3, 5):
                    return [-1, -2, -3, -3, -2, -3, -3, -4, -2, -3, -3, -4][oparg]
                elif (3, 6) <= version_tuple < (3, 11):
                    return [-1, -2, -2, -3, -2, -3, -3, -4, -2, -3, -3, -4][oparg]
                elif 0 <= oparg <= 2:
                    return [0, -1, -1][oparg]
                else:
                    return None
            else:
                return None
    elif opname == "CALL" and version_tuple >= (3, 12):
        return -oparg - 1
    elif opname == "CALL_KW":
        return -2 - oparg
    elif opname == "CALL_FUNCTION_EX":
        if (3, 5) <= version_tuple < (3, 11):
            return -2 if oparg & 1 else -1
        elif 0 <= oparg <= 3:
            return -3 if oparg & 1 else -2
        else:
            return None
    elif opname in (
        "INSTRUMENTED_LOAD_SUPER_ATTR",
        "LOAD_SUPER_ATTR",
    ) and version_tuple >= (3, 12):
        return -1 if oparg & 1 else -2
    elif opname == "LOAD_GLOBAL" and version_tuple >= (3, 11):
        return 2 if oparg & 1 else 1
    elif opname == "PRECALL" and version_tuple >= (3, 11):
        return -oparg
    elif opname == "RAISE_VARARGS" and version_tuple >= (3, 12):
        return -oparg
    if push >= 0 and pop >= 0:
        return push - pop
    elif pop < 0:
        # The amount popped depends on oparg, and opcode class
        if opcode in opc.VARGS_OPS:
            return push - oparg + (pop + 1)
        elif opcode in opc.NARGS_OPS:
            return -oparg + pop + push
    return -100


if __name__ == "__main__":
    from dis import findlabels as findlabels_std

    my_code = findlabels.__code__.co_code
    from xdis.op_imports import get_opcode_module

    my_opc = get_opcode_module()
    assert findlabels(my_code, my_opc) == findlabels_std(my_code)
