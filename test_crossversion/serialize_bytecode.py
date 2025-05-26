from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Callable, TextIO

from config import SYS_VERSION_TUPLE

import xdis
from xdis import disassemble_file, iscode


# Util to format shorthand code obj name
# Used so we do not compare memory addrs
def _fmt_codeobj(co):
    return f"<codeobj {co.co_name}>"


def _iter_nested_bytecodes(bytecode, bytecode_constructor: Callable):
    """
    iterate over a bytecode and its child bytecodes

    :param bytecode: bytecode object to iterate, will be yielded on first call
    :param bytecode_constructor: constructor to create child bytecodes with
    """
    bc_stack = [bytecode]
    while bc_stack:
        bc = bc_stack.pop()
        bc_stack.extend(bytecode_constructor(obj) for obj in bc.codeobj.co_consts if iscode(obj))
        yield bc


def _get_headers_to_serialize(bytecode_version: tuple):
    headers_to_serialize = [
        "co_argcount",
        "co_cellvars",
        "co_code",
        "co_consts",
        "co_firstlineno",
        "co_flags",
        "co_freevars",
        "co_kwonlyargcount",
        "co_name",
        "co_names",
        "co_nlocals",
        "co_posonlyargcount",
        "co_stacksize",
        "co_varnames",
    ]

    if bytecode_version >= (3, 10):
        headers_to_serialize.append("co_lines")
    if bytecode_version >= (3, 11):
        headers_to_serialize.append("co_qualname")
        # headers_to_serialize.append("co_positions"), not fully supported in xdis
    return headers_to_serialize


def _format_headers(bytecode, bytecode_version: tuple, headers_to_serialize: list[str] | None) -> str:
    """
    Format important headers (attrs) of bytecode.

    :param bytecode: bytecode object
    :param bytecode_version: bytecode version tuple to track version specific headers
    :param headers: list bytecode headers that we want to specifically format, excluding the other headers. By default, tests all params.
    """

    # default format for each attr
    header_fmt = "{name} : {val}"

    # format headers
    formatted_headers = []
    headers = headers_to_serialize if headers_to_serialize is not None else _get_headers_to_serialize(bytecode_version)
    for attr_name in headers:
        # check for missing attrs
        if not hasattr(bytecode.codeobj, attr_name):
            logging.warning(f"Codeobj missing test_attr {attr_name}")
            continue

        attr_val = getattr(bytecode.codeobj, attr_name)

        # handle const attrs and some callables
        if attr_name == "co_consts":
            # filter code objects in co_consts
            val = [f"<codeobj {const.co_name}" if iscode(const) else const for const in attr_val]
        elif attr_name in ("co_lines", "co_positions"):
            val = list(attr_val())
        else:
            val = attr_val

        # format header string
        formatted_headers.append(header_fmt.format(name=attr_name[3:], val=val))

    return "\n".join(formatted_headers)


def _format_insts(bytecode, bytecode_version: tuple) -> str:
    """Format all instructions in given bytecode."""
    # TODO revisit ignoring argrepr and argvals in tests
    # we are ignoring argrepr and val for now, as xdis will sometimes include additional info there

    # default format for each instruction
    inst_fmt = "{inst.opcode} {inst.opname} : {inst.arg} {argval}"
    insts = []
    for inst in bytecode:
        # skip cache
        if inst.opname == "CACHE":
            continue

        # filter and format argvals
        if iscode(inst.argval):
            argval = _fmt_codeobj(inst.argval)
        else:
            argval = inst.argval

        insts.append(inst_fmt.format(inst=inst, argval=argval))

    return "\n".join(insts)


def format_bytecode(bytecode, bytecode_version: tuple, headers_to_serialize: list[str] | None = None, serialize_insts: bool = True) -> str:
    """
    Create complete formatted string of bytecode.

    :param bytecode: bytecode object
    :param bytecode_version: tuple of bytecode version to track version specific formatting
    :param headers: list of bytecode headers we want to format in output. If None or not defined, we format all params by default.
    :param serialize_insts: bool to determine if we serialize instructions or ignore them and dont output.
    """

    outstr = f"BYTECODE {bytecode.codeobj.co_name}\n"
    outstr += "ATTRS:\n"
    outstr += _format_headers(bytecode, bytecode_version, headers_to_serialize) + "\n"
    if serialize_insts:
        outstr += "INSTS:\n"
        outstr += _format_insts(bytecode, bytecode_version) + "\n"
    return outstr


def serialize_pyc(pyc: Path, use_xdis: bool = False, output_file: TextIO | None = sys.stdout, headers: list[str] | None = None, serialize_insts: bool = True) -> str:
    """
    Serialize a pyc to text for testing, using dis or xdis.

    :param pyc: path of pyc file
    :param use_xdis: boolean if we serialize with xdis, default use dis (meaning pyc must be same version as running python)
    :param output_file: file to write output to
    :param headers: list of bytecode headers we want to format in output. Default is None, where we format all params.
    :param serialize_insts: bool to determine if we format instructions or ignore them and dont output save.
    """

    # create a code object in xdis or dis, and a constructor to make bytecodes with
    if use_xdis:
        # using xdis
        from os import devnull

        # write to null so no disassembly output
        with open(devnull, "w") as fnull:
            # create xdis code obj
            (_, code_object, version_tuple, _, _, is_pypy, _, _) = disassemble_file(str(pyc), fnull, asm_format="classic")
        # get corresponding opcode class
        opc = xdis.get_opcode(version_tuple, is_pypy, None)
        # create xdis bytecode constructor
        bytecode_constructor = lambda codeobj: xdis.Bytecode(codeobj, opc)
        bytecode_version = version_tuple
    else:
        # using dis
        import dis
        import marshal

        # load code obj
        code_object = marshal.loads(pyc.read_bytes()[16:])
        # create dis bytecode constructor
        bytecode_constructor = lambda codeobj: dis.Bytecode(codeobj)
        bytecode_version = SYS_VERSION_TUPLE

    # iter bytecodes and create list of formatted bytecodes strings
    formatted_bytecodes = []
    init_bytecode = bytecode_constructor(code_object)
    for bc in _iter_nested_bytecodes(init_bytecode, bytecode_constructor):
        formatted_bytecodes.append(format_bytecode(bc, bytecode_version, headers, serialize_insts))

    # write formatted bytecodes
    full_formatted_bytecode = "\n".join(formatted_bytecodes)
    if output_file:
        output_file.write(full_formatted_bytecode)

    return full_formatted_bytecode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="serialize_bytecode")
    parser.add_argument(
        "-x",
        "--use_xdis",
        help="Use xdis to serialize bytecode",
        action="store_true",
    )
    parser.add_argument(
        "--headers",
        help="List of specific code object params to test, defaults to all parameters. Should be 'co_*', for example, 'co_lines'",
        nargs="*",
    )
    parser.add_argument(
        "--skip_insts",
        help="Do not test accuracy of instructions",
        action="store_false",
    )
    parser.add_argument("pyc", help="PYC file to serialize.")
    args = parser.parse_args()

    # verify pyc path
    pyc_path = Path(args.pyc)
    assert pyc_path.exists(), "PYC does not exist"

    # setup logger
    logging.basicConfig(format="%(levelname)s: %(message)s")

    serialize_pyc(pyc_path, args.use_xdis, headers=args.headers if args.headers else None, serialize_insts=args.skip_insts)
