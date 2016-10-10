"""Python disassembly functions specific to wordcode from python 3.6
Extracted from
"""
from xdis import PYTHON3
from xdis.bytecode import op_has_argument

def _unpack_opargs(code, opc):
    # enumerate() is not an option, since we sometimes process
    # multiple elements on a single pass through the loop
    extended_arg = 0
    n = len(code)
    i = 0
    while i < n:
        op = code[i] if PYTHON3 else ord(code[i])
        offset = i
        i += 1
        arg = None
        if op_has_argument(op, opc):
            if PYTHON3:
                arg = code[i] + code[i+1]*256 + extended_arg
            else:
                arg = ord(code[i]) + ord(code[i+1])*256 + extended_arg
            extended_arg = 0
            i += 2
            if op == opc.EXTENDED_ARG:
                extended_arg = arg*65536
        yield (offset, op, arg)


def findlinestarts(code):
    """Find the offsets in a byte code which are start of lines in the source.

    Generate pairs (offset, lineno) as described in Python/compile.c.

    """
    if PYTHON3:
        byte_increments = code.co_lnotab[0::2]
        line_increments = code.co_lnotab[1::2]
    else:
        byte_increments = [ord(c) for c in code.co_lnotab[0::2]]
        line_increments = [ord(c) for c in code.co_lnotab[1::2]]

    lastlineno = None
    lineno = code.co_firstlineno
    addr = 0
    for byte_incr, line_incr in zip(byte_increments, line_increments):
        if byte_incr:
            if lineno != lastlineno:
                yield (addr, lineno)
                lastlineno = lineno
            addr += byte_incr
        if line_incr >= 0x80:
            # line_increments is an array of 8-bit signed integers
            line_incr -= 0x100
        lineno += line_incr
    if lineno != lastlineno:
        yield (addr, lineno)


def findlabels(code, opc):
    """Detect all offsets in a byte code which are jump targets.

    Return the list of offsets.

    """
    labels = []
    for offset, op, arg in _unpack_opargs(code, opc):
        if arg is not None:
            label = -1
            if op in opc.hasjrel:
                label = offset + 3 + arg
            elif op in opc.hasjabs:
                label = arg
            if label >= 0:
                if label not in labels:
                    labels.append(label)
    return labels
