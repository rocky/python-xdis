# Copyright (c) 2016-2018, 2020-2022 by Rocky Bernstein
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
"""
CPython version-independent disassembly routines
"""

# Note: we tend to eschew new Python 3 things, and even future
# imports so this can run on older Pythons. This is
# intended to be a more cross-version Python program

import datetime, re, sys

try:
    from collections import deque
except ImportError:
    class deque:
        def __init__(self, initial_todo=[]):
            self.todo = initial_todo

        def popleft(self):
            return self.todo.pop()

        def append(self, item):
            return self.todo.append(item)

        def __len__(self):
            return len(self.todo)

import xdis
from xdis.bytecode import Bytecode
from xdis.codetype import iscode, codeType2Portable
from xdis.cross_dis import format_code_info
from xdis.load import check_object_path, load_module
from xdis.magics import PYTHON_MAGIC_INT
from xdis.op_imports import op_imports, remap_opcodes
from xdis.version import __version__
from xdis.version_info import IS_PYPY, PYTHON_VERSION_TRIPLE


def get_opcode(version_tuple, is_pypy, alternate_opmap=None):
    # Set up disassembler with the right opcodes
    lookup = ".".join((str(i) for i in version_tuple))
    if is_pypy:
        lookup += "pypy"
    if lookup in op_imports.keys():
        if alternate_opmap is not None:
            # TODO: change bytecode version number comment line to indicate altered
            return remap_opcodes(op_imports[lookup], alternate_opmap)
        return op_imports[lookup]
    if is_pypy:
        pypy_str = " for pypy"
    else:
        pypy_str = ""
    raise TypeError("%s is not a Python version%s I know about" % (lookup, pypy_str))


def show_module_header(
    version_tuple,
    co,
    timestamp,
    out=sys.stdout,
    is_pypy=False,
    magic_int=None,
    source_size=None,
    sip_hash=None,
    header=True,
    show_filename=True,
):

    bytecode_version = ".".join((str(i) for i in version_tuple))
    real_out = out or sys.stdout
    if is_pypy:
        co_pypy_str = "PyPy "
    else:
        co_pypy_str = ""

    if IS_PYPY:
        run_pypy_str = "PyPy "
    else:
        run_pypy_str = ""

    if header:
        magic_str = ""
        if magic_int:
            magic_str = str(magic_int)
        real_out.write(
            (
                "# pydisasm version %s\n# %sPython bytecode %s%s"
                "\n# Disassembled from %sPython %s\n"
            )
            % (
                __version__,
                co_pypy_str,
                bytecode_version,
                " (%s)" % magic_str,
                run_pypy_str,
                "\n# ".join(sys.version.split("\n")),
            )
        )
    if PYTHON_VERSION_TRIPLE < (3, 0) and bytecode_version >= "3.0":
        real_out.write(
            "\n## **Warning** bytecode strings may be converted to strings.\n"
        )
        real_out.write("## To avoid loss, run this from Python 3.0 or greater\n\n")

    if timestamp is not None:
        value = datetime.datetime.fromtimestamp(timestamp)
        real_out.write("# Timestamp in code: %d" % timestamp)
        real_out.write(value.strftime(" (%Y-%m-%d %H:%M:%S)\n"))
    if source_size is not None:
        real_out.write("# Source code size mod 2**32: %d bytes\n" % source_size)
    if sip_hash is not None:
        real_out.write("# SipHash:           0x%x\n" % sip_hash)
    if show_filename:
        real_out.write("# Embedded file name: %s\n" % co.co_filename)


def disco(
    version_tuple,
    co,
    timestamp,
    out=sys.stdout,
    is_pypy=False,
    magic_int=None,
    source_size=None,
    sip_hash=None,
    asm_format="classic",
    alternate_opmap=None,
):
    """
    diassembles and deparses a given code block 'co'
    """

    assert iscode(co)

    show_module_header(
        version_tuple,
        co,
        timestamp,
        out,
        is_pypy,
        magic_int,
        source_size,
        sip_hash,
        header=True,
        show_filename=False,
    )

    # store final output stream for case of error
    real_out = out or sys.stdout

    if co.co_filename and asm_format != "xasm":
        real_out.write(format_code_info(co, version_tuple) + "\n")
        pass

    opc = get_opcode(version_tuple, is_pypy, alternate_opmap)

    if asm_format == "xasm":
        disco_loop_asm_format(opc, version_tuple, co, real_out, {}, set([]))
    else:
        queue = deque([co])
        disco_loop(
            opc, version_tuple, queue, real_out, asm_format=asm_format, dup_lines=True
        )


def disco_loop(
    opc, version_tuple, queue, real_out, dup_lines=False, asm_format="classic"
):
    """Disassembles a queue of code objects. If we discover
    another code object which will be found in co_consts, we add
    the new code to the list. Note that the order of code discovery
    is in the order of first encountered which is not amenable for
    the format used by a disassembler where code objects should
    be defined before using them in other functions.
    However, this is not recursive and will overall lead to less
    memory consumption at run time.
    """

    while len(queue) > 0:
        co = queue.popleft()
        if co.co_name not in ("<module>", "?"):
            real_out.write("\n" + format_code_info(co, version_tuple) + "\n")

        bytecode = Bytecode(co, opc, dup_lines=dup_lines)
        real_out.write(bytecode.dis(asm_format=asm_format) + "\n")

        for c in co.co_consts:
            if iscode(c):
                queue.append(c)
            pass
        pass


def code_uniquify(basename, co_code):
    # FIXME: better would be a hash of the co_code
    return "%s_0x%x" % (basename, id(co_code))


def disco_loop_asm_format(opc, version_tuple, co, real_out, fn_name_map, all_fns):
    """Produces disassembly in a format more conducive to
    automatic assembly by producing inner modules before they are
    used by outer ones. Since this is recursive, we'll
    use more stack space at runtime.
    """

    co = codeType2Portable(co)
    co_name = co.co_name
    mapped_name = fn_name_map.get(co_name, co_name)

    new_consts = []
    for c in co.co_consts:
        if iscode(c):
            if isinstance(c, types.CodeType):
                c_compat = codeType2Portable(c)
            else:
                c_compat = c

            disco_loop_asm_format(
                opc, version_tuple, c_compat, real_out, fn_name_map, all_fns
            )

            m = re.match(".* object <(.+)> at", str(c))
            if m:
                basename = m.group(1)
                if basename != "module":
                    mapped_name = code_uniquify(basename, c.co_code)
                    c_compat.co_name = mapped_name
            c_compat.freeze()
            new_consts.append(c_compat)
        else:
            new_consts.append(c)
        pass
    co.co_consts = new_consts

    m = re.match("^<(.+)>$", co.co_name)
    if m or co_name in all_fns:
        if co_name in all_fns:
            basename = co_name
        else:
            basename = m.group(1)
        if basename != "module":
            mapped_name = code_uniquify(basename, co.co_code)
            co_name = mapped_name
            assert mapped_name not in fn_name_map
        fn_name_map[mapped_name] = basename
        co.co_name = mapped_name
        pass
    elif co_name in fn_name_map:
        # FIXME: better would be a hash of the co_code
        mapped_name = code_uniquify(co_name, co.co_code)
        fn_name_map[mapped_name] = co_name
        co.co_name = mapped_name
        pass

    co = co.freeze()
    all_fns.add(co_name)
    if co.co_name != "<module>" or co.co_filename:
        real_out.write("\n" + format_code_info(co, version_tuple, mapped_name) + "\n")

    bytecode = Bytecode(co, opc, dup_lines=True)
    real_out.write(bytecode.dis(asm_format="asm") + "\n")


def disassemble_file(
    filename,
    outstream=sys.stdout,
    asm_format="classic",
    header=False,
    alternate_opmap=None,
):
    """
    disassemble Python byte-code file (.pyc)

    If given a Python source file (".py") file, we'll
    try to find the corresponding compiled object.

    If that fails we'll compile internally for the Python version currently running
    """
    pyc_filename = None
    try:
        # FIXME: add whether we want PyPy
        pyc_filename = check_object_path(filename)
        (
            version_tuple,
            timestamp,
            magic_int,
            co,
            is_pypy,
            source_size,
            sip_hash,
        ) = load_module(pyc_filename)
    except Exception:

        # Hack alert: we're using pyc_filename set as a proxy for whether the filename exists.
        # check_object_path() will succeed if the file exists.
        if pyc_filename is None:
            raise
        import os
        stat = os.stat(filename)
        source = open(filename, "r").read()
        co = compile(source, filename, "exec")
        is_pypy = IS_PYPY
        magic_int = PYTHON_MAGIC_INT
        sip_hash = 0
        source_size = stat.st_size
        timestamp = stat.st_mtime
        version_tuple = PYTHON_VERSION_TRIPLE
    else:
        filename = pyc_filename

    if asm_format == "header":
        show_module_header(
            version_tuple,
            co,
            timestamp,
            outstream,
            is_pypy,
            magic_int,
            source_size,
            sip_hash,
            header=header,
            show_filename=True,
        )
    else:
        disco(
            version_tuple=version_tuple,
            co=co,
            timestamp=timestamp,
            out=outstream,
            is_pypy=is_pypy,
            magic_int=magic_int,
            source_size=source_size,
            sip_hash=sip_hash,
            asm_format=asm_format,
            alternate_opmap=alternate_opmap,
        )
    # print co.co_filename
    return (
        filename,
        co,
        version_tuple,
        timestamp,
        magic_int,
        is_pypy,
        source_size,
        sip_hash,
    )


def _test():
    """Simple test program to disassemble a file."""
    argc = len(sys.argv)
    if argc != 2:
        if argc == 1 and xdis.PYTHON3:
            fn = __file__
        else:
            sys.stderr.write("usage: %s [-|CPython compiled file]\n" % __file__)
            sys.exit(2)
    else:
        fn = sys.argv[1]
    disassemble_file(fn)


if __name__ == "__main__":
    _test()
