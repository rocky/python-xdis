# This comes from Python's dis.py

from xdis import PYTHON3
if PYTHON3:
    def code2num(code, i):
        return code[i]
else:
    def code2num(code, i):
        return ord(code[i])

# The inspect module interrogates this dictionary to build its
# list of CO_* constants. It is also used by pretty_flags to
# turn the co_flags field into a human readable list.
COMPILER_FLAG_NAMES = {
    0x0001: "OPTIMIZED",
    0x0002: "NEWLOCALS",
    0x0004: "VARARGS",
    0x0008: "VARKEYWORDS",
    0x0010: "NESTED",
    0x0020: "GENERATOR",
    0x0040: "NOFREE",

    # These are in Python 3.x
    0x0080: "COROUTINE",
    0x0100: "ITERABLE_COROUTINE",

    # These are used only in Python 2.x */
    0x01000: "GENERATOR_ALLOWED",
    0x02000: "FUTURE_DIVISION",
    0x04000: "ABSOLUTE_IMPORT",
    0x08000: "FUTURE_WITH_STATEMENT",
    0x10000: "FUTURE_PRINT_FUNCTION",
    0x20000: "FUTURE_UNICODE_LITERALS",
    0x40000: "FUTURE_BARRY_AS_DBFL",

    # These are PYPY specific
    0x100000: "KILL_DOCSTRING",
    0x200000: "YIELD_INSIDE_TRY",

    0x0100: "PYPY_SOURCE_IS_UTF8",
    0x0200: "PYPY_DONT_IMPLY_DEDENT",
    0x0400: "PYPY_ONLY_AST",
    0x10000000 :"PYPY_ACCEPT_NULL_BYTES"
}

def pretty_flags(flags):
    """Return pretty representation of code flags."""
    names = []
    result = "0x%08x" % flags
    for i in range(32):
        flag = 1<<i
        if flags & flag:
            names.append(COMPILER_FLAG_NAMES.get(flag, hex(flag)))
            flags ^= flag
            if not flags:
                break
    else:
        names.append(hex(flags))
    names.reverse()
    return "%s (%s)" % (result, " | ".join(names))

def format_code_info(co, version):
    lines = []
    lines.append("# Method Name:       %s" % co.co_name)
    lines.append("# Filename:          %s" % co.co_filename)
    lines.append("# Argument count:    %s" % co.co_argcount)
    if version >= 3.0:
        lines.append("# Kw-only arguments: %s" % co.co_kwonlyargcount)

    pos_argc = co.co_argcount
    lines.append("# Number of locals:  %s" % co.co_nlocals)
    lines.append("# Stack size:        %s" % co.co_stacksize)
    lines.append("# Flags:             %s" % pretty_flags(co.co_flags))
    if co.co_consts:
        lines.append("# Constants:")
        for i_c in enumerate(co.co_consts):
            lines.append("# %4d: %r" % i_c)
    if co.co_names:
        lines.append("# Names:")
        for i_n in enumerate(co.co_names):
            lines.append("# %4d: %s" % i_n)
    if pos_argc > 0:
        lines.append("# Positional arguments:")
        lines.append("#\t%s" % ", ".join(co.co_varnames[:pos_argc]))
        pass
    if len(co.co_varnames) > pos_argc:
        lines.append("# Local variables:")
        for i, n in enumerate(co.co_varnames[pos_argc:]):
            lines.append("# %4d: %s" % (pos_argc+i, n))
    if co.co_freevars:
        lines.append("# Free variables:")
        for i_n in enumerate(co.co_freevars):
            lines.append("# %4d: %s" % i_n)
    if co.co_cellvars:
        lines.append("# Cell variables:")
        for i_n in enumerate(co.co_cellvars):
            lines.append("# %4d: %s" % i_n)
    return "\n".join(lines)

def _try_compile(source, name):
    """Attempts to compile the given source, first as an expression and
       then as a statement if the first approach fails.

       Utility function to accept strings in functions that otherwise
       expect code objects
    """
    try:
        c = compile(source, name, 'eval')
    except SyntaxError:
        c = compile(source, name, 'exec')
    return c

def get_code_object(x):
    """Helper to handle methods, functions, generators, strings and raw code objects"""
    if hasattr(x, '__func__'): # Method
        x = x.__func__
    if hasattr(x, '__code__'): # Function
        x = x.__code__
    if hasattr(x, 'gi_code'):  # Generator
        x = x.gi_code
    if isinstance(x, str):     # Source code
        x = _try_compile(x, "<disassembly>")
    if hasattr(x, 'co_code'):  # Code object
        return x
    raise TypeError("don't know how to disassemble %s objects" %
                    type(x).__name__)

def code_info(x):
    """Formatted details of methods, functions, or code."""
    return format_code_info(get_code_object(x))

def show_code(co):
    """Print details of methods, functions, or code to *file*.

    If *file* is not provided, the output is printed on stdout.
    """
    print(code_info(co))
