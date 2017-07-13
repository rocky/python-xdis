"""Python disassembly functions specific to wordcode from Python 3.6+
"""
from xdis import PYTHON3
from xdis.bytecode import op_has_argument

def unpack_opargs_wordcode(code, opc):
    extended_arg = 0
    for i in range(0, len(code), 2):
        op = code[i]
        if op_has_argument(op, opc):
            if isinstance(code[i+1], str):
                arg = ord(code[i+1]) | extended_arg
            else:
                arg = code[i+1] | extended_arg
            if op == opc.EXTENDED_ARG:
                extended_arg = (arg << 8)
            else:
                extended_arg = 0
        else:
            arg = None
        yield (i, op, arg)

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
    for offset, op, arg in unpack_opargs_wordcode(code, opc):
        if arg is not None:
            label = -1
            if op in opc.JREL_OPS:
                label = offset + 2 + arg
            elif op in opc.JABS_OPS:
                label = arg
            if label >= 0:
                if label not in labels:
                    labels.append(label)
    return labels
