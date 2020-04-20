# (C) Copyright 2020 by Rocky Bernstein
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

# Here we are more closely modeling Python's Lib/dis.py organization.
# However it appears that Python names and code has copied a bit heavily from
# earlier versions of xdis (and without attribution).

from xdis.util import COMPILER_FLAG_NAMES, PYPY_COMPILER_FLAG_NAMES, better_repr

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


def format_code_info(co, version, name=None, is_pypy=False):
    if not name:
        name = co.co_name
    lines = []
    lines.append("# Method Name:       %s" % name)
    lines.append("# Filename:          %s" % co.co_filename)

    if version >= 1.3:
        lines.append("# Argument count:    %s" % co.co_argcount)

    if version >= 3.8 and hasattr(co, "co_posonlyargcount"):
        lines.append("# Position-only argument count: %s" % co.co_posonlyargcount)

    if version >= 3.0 and hasattr(co, "co_kwonlyargcount"):
        lines.append("# Keyword-only arguments: %s" % co.co_kwonlyargcount)

    pos_argc = co.co_argcount
    if version >= 1.3:
        lines.append("# Number of locals:  %s" % co.co_nlocals)
    if version >= 1.5:
        lines.append("# Stack size:        %s" % co.co_stacksize)

    if version >= 1.3:
        lines.append(
            "# Flags:             %s" % pretty_flags(co.co_flags, is_pypy=is_pypy)
        )

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
    if version > 2.0:
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
