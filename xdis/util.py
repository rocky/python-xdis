# (C) Copyright 2018-2019 by Rocky Bernstein
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

from math import copysign

def code2num(code, i):
    if isinstance(code, str):
        return ord(code[i])
    else:
        return code[i]


def num2code(num):
    return (num & 0xFF, num >> 8)


# The inspect module interrogates this dictionary to build its
# list of CO_* constants. It is also used by pretty_flags to
# turn the co_flags field into a human readable list.
COMPILER_FLAG_NAMES = {
    0x00000001: "OPTIMIZED",
    0x00000002: "NEWLOCALS",
    0x00000004: "VARARGS",
    0x00000008: "VARKEYWORDS",
    0x00000010: "NESTED",
    0x00000020: "GENERATOR",
    0x00000040: "NOFREE",
    # These are in Python 3.5 +
    0x00000080: "COROUTINE",
    0x00000100: "ITERABLE_COROUTINE",
    # These are in Python 3.6+
    0x00000200: "ASYNC_GENERATOR",

    # These are used only in Python 2.x */
    0x00001000: "GENERATOR_ALLOWED",
    0x00002000: "FUTURE_DIVISION",
    0x00004000: "ABSOLUTE_IMPORT",
    0x00008000: "FUTURE_WITH_STATEMENT",
    0x00010000: "FUTURE_PRINT_FUNCTION",
    0x00020000: "FUTURE_UNICODE_LITERALS",
    0x00040000: "FUTURE_BARRY_AS_DBFL",
}

# These are PYPY specific
PYPY_COMPILER_FLAG_NAMES = {
    0x00100000: "PYPY_KILL_DOCSTRING",
    0x00200000: "PYPY_YIELD_INSIDE_TRY",
    0x00000400: "PYPY_ONLY_AST",
    0x10000000: "PYPY_ACCEPT_NULL_BYTES",
}

# Invert above dictionary so we can look up a bit value
# from the compile flag name
COMPILER_FLAG_BIT = dict([v, k] for (k, v) in COMPILER_FLAG_NAMES.items())

# Allow us to access by just name, prefixed with CO. e.g
# CO_OPTIMIZED, CO_NOFREE
globals().update(dict(["CO_" + k, v] for (k, v) in COMPILER_FLAG_BIT.items()))


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


def code_has_star_arg(code):
    """Return True iff
    the code object has a variable positional parameter (*args-like)"""
    return (code.co_flags & 4) != 0


def code_has_star_star_arg(code):
    """Return True iff
    The code object has a variable keyword parameter (**kwargs-like)."""
    return (code.co_flags & 8) != 0

def is_negative_zero(n):
    """Returns true if n is -0.0"""
    return n == 0.0 and copysign(1, n) == -1

def better_repr(v):
    """Work around Python's unorthogonal and unhelpful repr() for primitive float
    and complex."""
    if isinstance(v, float):
        # float values 'nan' and 'inf' are not directly
        # representable in Python before Python 3.5. In Python 3.5
        # it is accessible via a library constant math.inf.  We
        # will canonicalize representation of these value as
        # float('nan') and float('inf')
        if str(v) in frozenset(["nan", "-nan", "inf", "-inf"]):
            return "float('%s')" % v
        elif is_negative_zero(v):
            return "-0.0"
        return repr(v)
    elif isinstance(v, complex):
        real = better_repr(v.real)
        imag = better_repr(v.imag)
        # FIXME: we could probably use repr() in most cases
        # sort out when that's possible.
        # The below is however round-tripable, and Python's repr() isn't.
        return "complex(%s, %s)" % (real, imag)
    elif isinstance(v, tuple):
        if len(v) == 1:
            return "(%s,)" % better_repr(v[0])
        return "(%s)" % ", ".join(better_repr(i) for i in v)
    elif isinstance(v, list):
        l = better_repr(v)
        if len(v) == 1:
            return "[%s,]" % better_repr(v[0])
        return "[%s]" % ", ".join(better_repr(i) for i in v)
    # TODO: elif deal with sets and dicts
    else:
        return repr(v)

def format_code_info(co, version, name=None, is_pypy=False):
    if not name:
        name = co.co_name
    lines = []
    lines.append("# Method Name:       %s" % name)
    lines.append("# Filename:          %s" % co.co_filename)

    if version >= 1.3:
        lines.append("# Argument count:    %s" % co.co_argcount)

    if version >= 3.0 and hasattr(co, "co_kwonlyargcount"):
        lines.append("# Kw-only arguments: %s" % co.co_kwonlyargcount)

    pos_argc = co.co_argcount
    if version >= 1.3:
        lines.append("# Number of locals:  %s" % co.co_nlocals)
    if version >= 1.5:
        lines.append("# Stack size:        %s" % co.co_stacksize)

    if version >= 1.3:
        lines.append("# Flags:             %s" % pretty_flags(co.co_flags, is_pypy=is_pypy))

    if version >= 1.5:
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
        c = compile(source, name, "eval")
    except SyntaxError:
        c = compile(source, name, "exec")
    return c


def get_code_object(x):
    """Helper to handle methods, functions, generators, strings and raw code objects"""
    if hasattr(x, "__func__"):  # Method
        x = x.__func__
    if hasattr(x, "__code__"):  # Function
        x = x.__code__
    if hasattr(x, "gi_code"):  # Generator
        x = x.gi_code
    if isinstance(x, str):  # Source code
        x = _try_compile(x, "<disassembly>")
    if hasattr(x, "co_code"):  # Code object
        return x
    raise TypeError("don't know how to disassemble %s objects" % type(x).__name__)


def code_info(x, version, is_pypy=False):
    """Formatted details of methods, functions, or code."""
    return format_code_info(get_code_object(x), version, is_pypy=is_pypy)


def show_code(co, version, file=None, is_pypy=False):
    """Print details of methods, functions, or code to *file*.

    If *file* is not provided, the output is printed on stdout.
    """
    if file is None:
        print(code_info(co, version, is_pypy=is_pypy))
    else:
        file.write(code_info(co, version) + "\n")
