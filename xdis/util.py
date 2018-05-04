# (C) Copyright 2018 by Rocky Bernstein
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

import types

def code2num(code, i):
    if isinstance(code, str):
        return ord(code[i])
    else:
        return code[i]

def num2code(num):
    return (num & 0xff, num >> 8)

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

    # These are in Python 3.x
    0x00000080: "COROUTINE",
    0x00000100: "ITERABLE_COROUTINE",

    # These are used only in Python 2.x */
    0x00001000: "GENERATOR_ALLOWED",
    0x00002000: "FUTURE_DIVISION",
    0x00004000: "ABSOLUTE_IMPORT",
    0x00008000: "FUTURE_WITH_STATEMENT",
    0x00010000: "FUTURE_PRINT_FUNCTION",
    0x00020000: "FUTURE_UNICODE_LITERALS",
    0x00040000: "FUTURE_BARRY_AS_DBFL",

    # These are PYPY specific
    0x00100000: "KILL_DOCSTRING",
    0x00200000: "YIELD_INSIDE_TRY",

    0x00000100: "PYPY_SOURCE_IS_UTF8",
    0x00000200: "PYPY_DONT_IMPLY_DEDENT",
    0x00000400: "PYPY_ONLY_AST",
    0x10000000: "PYPY_ACCEPT_NULL_BYTES"
}

# Invert above dictionary so we can look up a bit value
# from the compile flag name
COMPILER_FLAG_BIT = {}
for (v, k) in COMPILER_FLAG_NAMES.items():
    COMPILER_FLAG_BIT[k] = v

# Allow us to access by just name, prefixed with CO. e.g
# CO_OPTIMIZED, CO_NOFREE

for v, k in COMPILER_FLAG_BIT.items():
    globals().update(dict({'CO_'+v: k}))

def pretty_flags(flags):
    """Return pretty representation of code flags."""
    names = []
    result = "0x%08x" % flags
    for i in range(32):
        flag = 1 << i
        if flags & flag:
            names.append(COMPILER_FLAG_NAMES.get(flag, hex(flag)))
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


def format_code_info(co, version, name=None):
    if not name:
        name = co.co_name
    lines = []
    lines.append("# Method Name:       %s" % name)
    lines.append("# Filename:          %s" % co.co_filename)
    lines.append("# Argument count:    %s" % co.co_argcount)
    if version >= 3.0:
        lines.append("# Kw-only arguments: %s" % co.co_kwonlyargcount)

    pos_argc = co.co_argcount
    lines.append("# Number of locals:  %s" % co.co_nlocals)
    if version >= 1.5:
        lines.append("# Stack size:        %s" % co.co_stacksize)
    lines.append("# Flags:             %s" % pretty_flags(co.co_flags))
    if version >= 1.5:
        lines.append("# First Line:        %s" % co.co_firstlineno)
    # if co.co_freevars:
    #     lines.append("# Freevars:      %s" % str(co.co_freevars))
    if co.co_consts:
        lines.append("# Constants:")
        for i_c in enumerate(co.co_consts):
            lines.append("# %4d: %r" % i_c)
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
    if hasattr(x, 'im_func'):
        x = x.im_func
    if hasattr(x, 'func_code'): # Method
        x = x.func_code
    if hasattr(x, 'gi_code'):  # Generator
        x = x.gi_code
    if hasattr(x, '__dict__'):
        items = x.__dict__.items()
        items.sort()
        for name, x1 in items:
            if type(x1) in (types.MethodType,
                            types.FunctionType,
                            types.CodeType,
                            types.ClassType):
                x = x1
    if hasattr(x, 'co_code'):
        return x
    if isinstance(x, str):     # Source code
        x = _try_compile(x, "<disassembly>")
    raise TypeError("don't know how to disassemble %s objects" %
                    type(x).__name__)


def code_info(x, version):
    """Formatted details of methods, functions, or code."""
    return format_code_info(get_code_object(x), version)


def show_code(co, version, file=None):
    """Print details of methods, functions, or code to *file*.

    If *file* is not provided, the output is printed on stdout.
    """
    if file is None:
        print(code_info(co, version))
    else:
        file.write(code_info(co, version) + '\n')
