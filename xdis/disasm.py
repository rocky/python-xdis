# Copyright (c) 2016-2018, 2020-2021, 2023-2025
# by Rocky Bernstein
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

import datetime
import dis
import re
import sys
import types
from collections import deque

import xdis
from xdis.bytecode import Bytecode
from xdis.bytecode_graal import Bytecode_Graal
from xdis.codetype import codeType2Portable
from xdis.codetype.base import iscode
from xdis.cross_dis import format_code_info, format_exception_table
from xdis.load import check_object_path, load_module
from xdis.magics import GRAAL3_MAGICS, PYTHON_MAGIC_INT
from xdis.op_imports import op_imports, remap_opcodes
from xdis.version import __version__
from xdis.version_info import (
    PYTHON_IMPLEMENTATION,
    PYTHON_VERSION_TRIPLE,
    PythonImplementation,
)


# FIXME we may also need to distinguish by magic_int2magic
# (for 3.8.5 Graal for example.)
def get_opcode(
    version_tuple: tuple,
    python_implementation,
    alternate_opmap=None,
    magic_int: int = -1,
):
    # Set up disassembler with the right opcodes
    lookup = ".".join((str(i) for i in version_tuple))
    if python_implementation == PythonImplementation.PyPy:
        lookup += "PyPy"
    elif python_implementation == PythonImplementation.Graal:
        if magic_int == 21290:
            if version_tuple == (3, 11, 7):
                lookup = "3.11.7Graal"
            else:
                lookup = "3.12.7Graal"
        else:
            lookup += "Graal"
    elif python_implementation == PythonImplementation.RustPython:
        lookup += "Rust"
    if lookup in op_imports.keys():
        if alternate_opmap is not None:
            # TODO: change bytecode version number comment line to indicate altered
            return remap_opcodes(op_imports[lookup], alternate_opmap)
        return op_imports[lookup]
    if str(python_implementation) != "CPython":
        pypy_str = " for %s" % python_implementation
    else:
        pypy_str = ""
    raise TypeError("%s is not a Python version%s I know about" % (lookup, pypy_str))


def show_module_header(
    version_tuple,
    co,
    timestamp,
    out=sys.stdout,
    magic_int=None,
    source_size=None,
    sip_hash=None,
    header=True,
    show_filename=True,
    python_implementation=PYTHON_IMPLEMENTATION,
    file_offset=None,
):
    bytecode_version = ".".join((str(i) for i in version_tuple))
    real_out = out or sys.stdout
    implementation_str = python_implementation

    if header:
        magic_str = ""
        if magic_int:
            magic_str = str(magic_int)
        real_out.write(
            (
                "# pydisasm version %s\n# %s Python bytecode %s%s"
                "\n#   Disassembled from %s Python %s\n"
            )
            % (
                __version__,
                implementation_str,
                bytecode_version,
                " (%s)" % magic_str,
                str(PYTHON_IMPLEMENTATION),
                "\n# ".join(sys.version.split("\n")),
            )
        )
    if PYTHON_VERSION_TRIPLE < (3, 0) and bytecode_version >= "3.0":
        real_out.write(
            "\n## **Warning** bytecode strings will be converted to strings.\n"
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
    if file_offset:
        real_out.write("# Position in bytecode file: 0x%x\n" % file_offset)


def disco(
    version_tuple,
    co,
    timestamp,
    out=sys.stdout,
    magic_int: int=-1,
    source_size=None,
    sip_hash=None,
    asm_format: str = "classic",
    alternate_opmap=None,
    show_source: bool = False,
    methods=tuple(),
    python_implementation=PYTHON_IMPLEMENTATION,
    file_offsets: dict = {},
) -> None:
    """
    disassembles and deparses a given code block 'co'
    """

    assert iscode(co)

    show_module_header(
        version_tuple,
        co,
        timestamp,
        out,
        magic_int,
        source_size,
        sip_hash,
        header=True,
        show_filename=False,
        python_implementation=python_implementation,
    )

    # Store final output stream when there is an error.
    real_out = out or sys.stdout

    if co.co_filename and asm_format != "xasm":
        if not_filtered(co, methods):
            real_out.write(
                format_code_info(
                    co,
                    version_tuple,
                    python_implementation=python_implementation,
                    file_offset=file_offsets.get(co),
                )
                + "\n"
            )
        pass

    opc = get_opcode(version_tuple, python_implementation, alternate_opmap, magic_int)

    if asm_format == "xasm":
        disco_loop_asm_format(opc, version_tuple, co, real_out, {}, set([]))
    else:
        queue = deque([co])
        disco_loop(
            opc,
            version_tuple,
            queue,
            real_out,
            asm_format=asm_format,
            dup_lines=True,
            show_source=show_source,
            methods=methods,
            file_offsets=file_offsets,
            is_unusual_bytecode=magic_int in GRAAL3_MAGICS,
        )


def disco_loop(
    opc,
    version_tuple,
    queue,
    real_out,
    dup_lines=False,
    asm_format="classic",
    show_source=False,
    methods=tuple(),
    file_offsets: dict = {},
    is_unusual_bytecode: bool = False,
) -> None:
    """Disassembles a queue of code objects. If we discover
    another code object which will be found in co_consts, we add
    the new code to the list. Note that the order of code discovery
    is in the order of first encountered that is not amenable for
    the format used by a disassembler where code objects should
    be defined before using them in other functions.
    However, this is not recursive and will overall lead to less
    memory consumption at run time.
    """

    while len(queue) > 0:
        co = queue.popleft()
        if not_filtered(co, methods):
            if co.co_name not in ("<module>", "?"):
                real_out.write(
                    "\n"
                    + format_code_info(
                        co, version_tuple, file_offset=file_offsets.get(co)
                    )
                    + "\n"
                )

            if asm_format == "dis":
                assert version_tuple[:2] == PYTHON_VERSION_TRIPLE[:2], (
                    "dis requires disassembly from the same Python version: "
                    "Bytecode is for %s; Running: %s"
                    % (version_tuple[:2], PYTHON_VERSION_TRIPLE[:2])
                )
                dis.disassemble(co, lasti=-1)
                assert version_tuple[:2] == PYTHON_VERSION_TRIPLE[:2], (
                    "dis requires disassembly from the same Python version: "
                    "Bytecode is for %s; Running: %s"
                    % (version_tuple[:2], PYTHON_VERSION_TRIPLE[:2])
                )
                dis.disassemble(co, lasti=-1, file=real_out)
            elif is_unusual_bytecode:
                if hasattr(co, "graal_instr_str") and co.graal_instr_str:
                    real_out.write(co.graal_instr_str)
                    if asm_format in ("extended_bytes", "bytes"):
                        real_out.write("instruction bytecode:\n%s\n" % co.co_code)

            if opc.python_implementation == PythonImplementation.Graal:
                bytecode = Bytecode_Graal(co, opc)
            else:
                bytecode = Bytecode(co, opc, dup_lines=dup_lines)
            real_out.write(
                bytecode.dis(
                    asm_format=asm_format,
                    show_source=show_source,
                )
                + "\n"
            )

            if version_tuple >= (3, 11):
                if bytecode.exception_entries not in (None, []):
                    exception_table = format_exception_table(bytecode, version_tuple)
                    real_out.write(exception_table + "\n")

        for c in co.co_consts:
            if iscode(c):
                queue.append(c)
            pass
        pass


def code_uniquify(basename, co_code) -> str:
    # FIXME: better would be a hash of the co_code
    return "%s_0x%x" % (basename, id(co_code))


def disco_loop_asm_format(
    opc, version_tuple: tuple, co, real_out, fn_name_map, all_fns
) -> None:
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
    if m is not None or co.co_name in all_fns:
        if co.co_name in all_fns:
            basename = co_name
        else:
            basename = m.group(1)
        if basename != "module":
            mapped_name = code_uniquify(basename, co.co_code)
            co_name = mapped_name
            if mapped_name in fn_name_map:
                # We can have two lambdas created that are the same
                # but have different line numbers
                mapped_name += "_%s" % str(co.co_firstlineno)
        fn_name_map[mapped_name] = basename
        co.co_name = mapped_name
        pass
    elif co_name in fn_name_map:
        # FIXME: better would be a hash of the co_code
        mapped_name = code_uniquify(co_name, co.co_code)
        fn_name_map[mapped_name] = co_name
        co.co_name = mapped_name
        pass
    else:
        mapped_name = co.co_name

    co = co.freeze()
    all_fns.add(co_name)
    if co.co_name != "<module>" or co.co_filename:
        real_out.write(
            "\n"
            + format_code_info(
                co,
                version_tuple,
                mapped_name,
                python_implementation=opc.python_implementation,
            )
            + "\n"
        )

    bytecode = Bytecode(co, opc, dup_lines=True)
    real_out.write(bytecode.dis(asm_format="asm") + "\n")


def disassemble_file(
    filename: str,
    outstream=sys.stdout,
    asm_format="classic",
    alternate_opmap=None,
    show_source=False,
    methods=tuple(),
    save_file_offsets: bool = False,
):
    """
    Disassemble Python byte-code file (.pyc).

    If given a Python source file (".py") file, we'll
    try to find the corresponding compiled object.

    If that fails, we'll compile internally for the Python version currently running.
    """
    pyc_filename = None
    file_offsets = {}
    try:
        pyc_filename = check_object_path(filename)
        (
            version_tuple,
            timestamp,
            magic_int,
            co,
            python_implementation,
            source_size,
            sip_hash,
            file_offsets,
        ) = load_module(pyc_filename, save_file_offsets=save_file_offsets)
    except (ImportError, NotImplementedError, ValueError):
        raise
    except Exception:
        # Hack alert: we're using pyc_filename set as a proxy for whether the filename exists.
        # check_object_path() will succeed if the file exists.
        if pyc_filename is None:
            raise
        import os

        stat = os.stat(filename)
        source = open(filename, "r").read()
        co = compile(source, filename, "exec")
        python_implementation = PYTHON_IMPLEMENTATION
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
            magic_int,
            source_size,
            sip_hash,
            header=True,
            show_filename=True,
            python_implementation=python_implementation,
        )
    else:
        disco(
            version_tuple=version_tuple,
            co=co,
            timestamp=timestamp,
            out=outstream,
            python_implementation=python_implementation,
            magic_int=magic_int,
            source_size=source_size,
            sip_hash=sip_hash,
            asm_format=asm_format,
            alternate_opmap=alternate_opmap,
            show_source=show_source,
            methods=methods,
            file_offsets=file_offsets,
        )
    # print co.co_filename
    return (
        filename,
        co,
        version_tuple,
        timestamp,
        magic_int,
        python_implementation,
        source_size,
        sip_hash,
    )


def not_filtered(co: types.CodeType, methods: tuple) -> bool:
    return len(methods) == 0 or co.co_name in methods


def _test() -> None:
    """Simple test program to disassemble a file."""
    argc = len(sys.argv)
    if argc == 1:
        if xdis.PYTHON3:
            disassemble_file(__file__)
            disassemble_file(__file__, methods=("code_uniquify",))
        else:
            sys.stderr.write("usage: %s [-|CPython compiled file [format]]\n" % __file__)
            sys.exit(2)
    elif argc == 3:
        fn, asm_format = sys.argv[1:3]
        disassemble_file(fn, asm_format=asm_format)
    else:
        fn = sys.argv[1]
        disassemble_file(fn)


if __name__ == "__main__":
    _test()
