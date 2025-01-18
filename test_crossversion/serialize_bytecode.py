from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable, TextIO

import xdis
from xdis import disassemble_file, iscode

# Util to format shorthand code obj name
# Used so we do not compare memory addrs
_fmt_codeobj = lambda co: f"<codeobj {co.co_name}>"


def _iter_nested_bytecodes(bytecode, bytecode_constructor: Callable):
    """
    iterate over a bytecode and its child bytecodes
    bytecode: bytecode object to iterate, will be yielded on first call
    bytecode_constructor: constructor to create child bytecodes with
    """
    bc_stack = [bytecode]
    while bc_stack:
        bc = bc_stack.pop()
        bc_stack.extend(
            bytecode_constructor(obj) for obj in bc.codeobj.co_consts if iscode(obj)
        )
        yield bc


def _format_headers(bytecode) -> str:
    """Format important headers (attrs) of bytecode."""

    # TODO add an automated way to filter attrs not used in dis that may be present in xdis
    # simple solution may just be a header in a serialized pyc stating what is being saved

    # headers of the codeobj to serialize
    headers_to_serialize = [
        "co_argcount",
        "co_cellvars",
        "co_code",
        "co_consts",
        "co_firstlineno",
        "co_flags",
        "co_freevars",
        "co_kwonlyargcount",
        "co_linetable",
        # "co_lnotab",  # not in dis >3.11, see todo above
        "co_name",
        "co_names",
        "co_nlocals",
        "co_posonlyargcount",
        "co_stacksize",
        "co_varnames",
    ]
    # default format for each attr
    header_fmt = "{name} : {val}"

    # format headers
    formatted_headers = []
    for attr in headers_to_serialize:
        if not hasattr(bytecode.codeobj, attr):
            print(f"Warning: Codeobj missing test_attr {attr}")
            continue
        val = getattr(bytecode.codeobj, attr)
        # filter code objects in co_consts
        if attr == "co_consts":
            val = [
                f"<codeobj {const.co_name}" if iscode(const) else const for const in val
            ]
        # format header string
        formatted_headers.append(header_fmt.format(name=attr[3:], val=val))

    return "\n".join(formatted_headers)


def _format_insts(bytecode) -> str:
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
            insts.append(inst_fmt.format(inst=inst, argval=argval))
        else:
            insts.append(inst_fmt.format(inst=inst, argval=inst.argval))

    return "\n".join(insts)


def format_bytecode(bytecode) -> str:
    """Create complete formatted string of bytecode."""
    outstr = f"BYTECODE {bytecode.codeobj.co_name}\n"
    outstr += "ATTRS:\n"
    outstr += _format_headers(bytecode) + "\n"
    outstr += "INSTS:\n"
    outstr += _format_insts(bytecode) + "\n"
    return outstr


def serialize_pyc(
    pyc: Path, use_xdis: bool = False, output_file: TextIO | None = sys.stdout
) -> str:
    """Serialize a pyc to text for testing, using dis or xdis."""

    # create a code object in xdis or dis, and a constructor to make bytecodes with
    if use_xdis:
        # write to null so no disassembly output
        from os import devnull

        with open(devnull, "w") as fnull:
            # create xdis code obj
            (_, code_object, version_tuple, _, _, is_pypy, _, _) = disassemble_file(
                str(pyc), fnull
            )
        # get corresponding opcode class
        opc = xdis.get_opcode(version_tuple, is_pypy, None)
        # create xdis bytecode constructor
        bytecode_constructor = lambda codeobj: xdis.Bytecode(codeobj, opc)
    else:
        import dis
        import marshal

        # load code obj
        code_object = marshal.loads(pyc.read_bytes()[16:])
        # create dis bytecode constructor
        bytecode_constructor = lambda codeobj: dis.Bytecode(codeobj)

    # iter bytecodes
    formatted_bytecodes = []
    init_bytecode = bytecode_constructor(code_object)
    for bc in _iter_nested_bytecodes(init_bytecode, bytecode_constructor):
        formatted_bytecodes.append(format_bytecode(bc))

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
    parser.add_argument("pyc", help="PYC file to serialize.")
    args = parser.parse_args()

    pyc_path = Path(args.pyc)
    assert pyc_path.exists(), "PYC does not exist"

    serialize_pyc(pyc_path, args.use_xdis)
