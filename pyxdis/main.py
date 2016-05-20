# Copyright (c) 2015-2016 by Rocky Bernstein
# Copyright (c) 2000-2002 by hartmut Goebel <h.goebel@crazy-compilers.com>

"""
CPython magic- and version- independent disassembly routines

There are two reasons we can't use Python's built-in routines
from dis. First, the bytecode we are extracting may be from a different
version of Python (different magic number) than the version of Python
that is doing the extraction.

Second, we need structured instruction information for the
(de)-parsing step. Python 3.4 and up provides this, but we still do
want to run on Python 2.7.
"""

from __future__ import print_function

import os, sys
from collections import deque

import pyxdis
from pyxdis import PYTHON_VERSION
from pyxdis.code import iscode
from pyxdis.load import check_object_path, load_module
from pyxdis.disassemble import get_disasm

## FIXME: this comes from Python's dis.py
## Isolate it?

# The inspect module interrogates this dictionary to build its
# list of CO_* constants. It is also used by pretty_flags to
# turn the co_flags field into a human readable list.
COMPILER_FLAG_NAMES = {
     1: "OPTIMIZED",
     2: "NEWLOCALS",
     4: "VARARGS",
     8: "VARKEYWORDS",
    16: "NESTED",
    32: "GENERATOR",
    64: "NOFREE",
   128: "COROUTINE",
   256: "ITERABLE_COROUTINE",
}

def pretty_flags(flags):
    """Return pretty representation of code flags."""
    names = []
    for i in range(32):
        flag = 1<<i
        if flags & flag:
            names.append(COMPILER_FLAG_NAMES.get(flag, hex(flag)))
            flags ^= flag
            if not flags:
                break
    else:
        names.append(hex(flags))
    return ", ".join(names)

def format_code_info(co, version):
    lines = []
    lines.append("# Method Name:       %s" % co.co_name)
    lines.append("# Filename:          %s" % co.co_filename)
    lines.append("# Argument count:    %s" % co.co_argcount)
    if version >= 3.0:
        lines.append("# Kw-only arguments: %s" % co.co_kwonlyargcount)
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
            lines.append("%4d: %s" % i_n)
    if co.co_varnames:
        lines.append("# Variable names:")
        for i_n in enumerate(co.co_varnames):
            lines.append("# %4d: %s" % i_n)
    if co.co_freevars:
        lines.append("# Free variables:")
        for i_n in enumerate(co.co_freevars):
            lines.append("%4d: %s" % i_n)
    if co.co_cellvars:
        lines.append("# Cell variables:")
        for i_n in enumerate(co.co_cellvars):
            lines.append("# %4d: %s" % i_n)
    return "\n".join(lines)

#################################

def disco(version, co, out=None, use_pyxdis_format=False):
    """
    diassembles and deparses a given code block 'co'
    """

    assert iscode(co)

    # store final output stream for case of error
    real_out = out or sys.stdout
    print('# Python bytecode %s (disassembled from Python %s)' %
              (version, PYTHON_VERSION), file=real_out)
    if co.co_filename:
        print(format_code_info(co, version))

    disasm = get_disasm(version)

    disasm = disasm.disassemble_native \
      if (not use_pyxdis_format) and hasattr(disasm, 'disassemble_native') \
      else disasm.disassemble

    queue = deque([co])
    disco_loop(disasm, version, queue, real_out, use_pyxdis_format)


def disco_loop(disasm, version, queue, real_out, use_pyxdis_format):
    while len(queue) > 0:
        co = queue.popleft()
        if co.co_name != '<module>':
            print("\n" + format_code_info(co, version), file=real_out)
        tokens = disasm(co, use_pyxdis_format)
        for t in tokens:
            if iscode(t.pattr):
                queue.append(t.pattr)
            elif iscode(t.attr):
                queue.append(t.attr)
            print(t.format(), file=real_out)
            pass
        pass

def disassemble_file(filename, outstream=None, native=False):
    """
    disassemble Python byte-code file (.pyc)

    If given a Python source file (".py") file, we'll
    try to find the corresponding compiled object.
    """
    filename = check_object_path(filename)
    version, timestamp, magic_int, co = load_module(filename)
    if type(co) == list:
        for con in co:
            disco(version, con, outstream, native)
    else:
        disco(version, co, outstream, native)
    co = None

def disassemble_files(in_base, out_base, files, outfile=None,
                      native=False):
    """
    in_base	base directory for input files
    out_base	base directory for output files (ignored when
    files	list of filenames to be uncompyled (relative to src_base)
    outfile	write output to this filename (overwrites out_base)

    For redirecting output to
    - <filename>		outfile=<filename> (out_base is ignored)
    - files below out_base	out_base=...
    - stdout			out_base=None, outfile=None
    """
    def _get_outstream(outfile):
        dir = os.path.dirname(outfile)
        failed_file = outfile + '_failed'
        if os.path.exists(failed_file):
            os.remove(failed_file)
        try:
            os.makedirs(dir)
        except OSError:
            pass
        return open(outfile, 'w')

    of = outfile
    if outfile == '-':
        outfile = None # use stdout
    elif outfile and os.path.isdir(outfile):
        out_base = outfile; outfile = None
    elif outfile:
        out_base = outfile; outfile = None

    for filename in files:
        infile = os.path.join(in_base, filename)
        # print (infile, file=sys.stderr)

        if of: # outfile was given as parameter
            outstream = _get_outstream(outfile)
        elif out_base is None:
            outstream = sys.stdout
        else:
            outfile = os.path.join(out_base, filename) + '_dis'
            outstream = _get_outstream(outfile)
            # print(outfile, file=sys.stderr)
            pass

        # try to disassemble the input file
        try:
            disassemble_file(infile, outstream, native)
        except KeyboardInterrupt:
            if outfile:
                outstream.close()
                os.remove(outfile)
            raise
        except:
            if outfile:
                outstream.close()
                os.rename(outfile, outfile + '_failed')
            else:
                sys.stderr.write("\n# Can't disassemble %s\n" % infile)
                import traceback
                traceback.print_exc()
        else: # uncompyle successfull
            if outfile:
                outstream.close()
            if not outfile: print('\n# okay disassembling', infile)
            sys.stdout.flush()

        if outfile:
            sys.stdout.write("\n")
            sys.stdout.flush()
        return

def _test():
    """Simple test program to disassemble a file."""
    argc = len(sys.argv)
    if argc != 2:
        if argc == 1 and pyxdis.PYTHON3:
            fn = __file__
        else:
            sys.stderr.write("usage: %s [-|CPython compiled file]\n" % __file__)
            sys.exit(2)
    else:
        fn = sys.argv[1]
    disassemble_file(fn, native=True)

if __name__ == "__main__":
    _test()
