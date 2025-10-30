#!/usr/bin/env python
# (C) Copyright 2025 by Rocky Bernstein
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

Check that we can read in or unmarshal a Python bytecode file and
then write it or marshal it back and the files are identical.

As
Input is a Python bytecode file. A file of this kind usually the has
file extension ".pyc" or ".pyo".

This steps taken are:
- loads it or unmarshals it with xdis.load.load_module_from_file_object()
- writes it or marshals back out using xdis.load.write_bytecode_file() to a temporary file
- compares the original and written files by raw bytes and by the
  module/code-object structure they contain

Usage:
   test_writing_pyc.py path/to/bytecode_file.pyc

"""

import filecmp
import os
import os.path as osp
import sys
import tempfile

from xdis.load import load_module_from_file_object, write_bytecode_file
from xdis.version_info import version_tuple_to_str

# For later:
# from xdis.unmarshal import (
#     _VersionIndependentUnmarshaller,
#     FLAG_REF,
#     UNMARSHAL_DISPATCH_TABLE,
# )


def compare_consts(c1: tuple, c2: tuple) -> bool:
    """Compare tuples of constants, recursing into code objects when found."""
    if len(c1) != len(c2):
        return False
    for a, b in zip(c1, c2):
        # If code object-like, compare as code objects
        if hasattr(a, "co_code") and hasattr(b, "co_code"):
            if not compare_code_objects(a, b):
                return False
        else:
            if a != b:
                return False
    return True

def compare_showing_error(orig_path: str, new_path: str):
    """
      Compare file contents sizes if those mismatch and the first hex offset that the differ.
    """
    orig_bytes = open(orig_path, "rb").read()
    new_bytes = open(new_path, "rb").read()
    orig_n = len(orig_bytes)
    new_n = len(new_bytes)
    if orig_n != new_n:
        print("MISMATCH: original has %s bytes; new has %s bytes" % (orig_n, new_n), file=sys.stderr)

    for i, (old_byte, new_byte) in enumerate(zip(orig_bytes, new_bytes)):
        if (old_byte != new_byte):
            print("MISMATCH at %s: old %s; new: %s" % (hex(i), hex(old_byte), hex(new_byte)), file=sys.stderr)
            return


def get_code_attrs(co) -> dict:
    """
    Extract a set of attributes from a code object that are stable for comparison.
    This is defensive: only include an attribute if it exists on the object.
    """
    attrs = {}
    for name in (
        "co_argcount",
        "co_posonlyargcount",
        "co_kwonlyargcount",
        "co_nlocals",
        "co_stacksize",
        "co_flags",
        "co_code",
        "co_consts",
        "co_names",
        "co_varnames",
        "co_freevars",
        "co_cellvars",
        "co_filename",
        "co_name",
    ):
        if hasattr(co, name):
            attrs[name] = getattr(co, name)
    return attrs


def compare_code_objects(a, b):
    """
    Compare two code objects by a selection of attributes.
    This function attempts to be permissive across Python implementations
    by only using attributes when present and by comparing constants recursively.
    """
    attrs_a = get_code_attrs(a)
    attrs_b = get_code_attrs(b)

    if set(attrs_a.keys()) != set(attrs_b.keys()):
        # If the sets of attributes differ, still try to compare the
        # intersection of attributes to be less strict across implementations.
        common_keys = sorted(set(attrs_a.keys()).intersection(attrs_b.keys()))
    else:
        common_keys = sorted(attrs_a.keys())

    for key in common_keys:
        va = attrs_a[key]
        vb = attrs_b[key]
        if key == "co_consts":
            if not compare_consts(tuple(va), tuple(vb)):
                return False
        else:
            if va != vb:
                return False
    return True


# For later
# def r_object(self, bytes_for_s: bool = False):
#     """
#     Replacement r_object for classification
#     """
#     byte1 = ord(self.fp.read(1))

#     # FLAG_REF indicates whether we "intern" or
#     # save a reference to the object.
#     # byte1 without that reference is the
#     # marshal type code, an ASCII character.
#     save_ref = False
#     if byte1 & FLAG_REF:
#         # Since 3.4, "flag" is the marshal.c name
#         save_ref = True
#         byte1 = byte1 & (FLAG_REF - 1)
#     marshal_type = chr(byte1)

#     # print(marshal_type)  # debug

#     if marshal_type in UNMARSHAL_DISPATCH_TABLE:
#         func_suffix = UNMARSHAL_DISPATCH_TABLE[marshal_type]
#         unmarshal_func = getattr(self, "t_" + func_suffix)
#         return unmarshal_func(save_ref, bytes_for_s)
#     else:
#         mess = ("Unknown type %i (hex %x) %c\n"
#                 % (ord(marshal_type), ord(marshal_type), marshal_type))
#         raise TypeError(mess)
#     return

def load_meta_and_code_from_filename(path: str):
    """
    Open path and use load_module_from_file_object to get:
    (version_tuple, timestamp, magic_int, co, is_pypy, source_size, sip_hash, file_offsets)
    """
    with open(path, "rb") as fp:
        return load_module_from_file_object(fp, filename=path, get_code=True)


def roundtrip_pyc(input_path: str, unlink_on_success: bool) -> int:

    # parser = argparse.ArgumentParser(
    #     description="Load a .pyc with xdis, rewrite it to a temporary file, and compare."
    # )
    # parser.add_argument("pycfile", help="Path to the .pyc (or other bytecode) file")
    # args = parser.parse_args(argv)

    if not osp.exists(input_path):
        print("ERROR: file does not exist: %s" % input_path, file=sys.stderr)
        return 2
    if not osp.isfile(input_path):
        print("ERROR: not a file: %s" % input_path, file=sys.stderr)
        return 2

    # Load original using the file-object loader (it will close the file for us)
    try:
        (
            orig_version,
            orig_timestamp,
            orig_magic_int,
            orig_co,
            orig_is_pypy,
            orig_source_size,
            orig_sip_hash,
            orig_file_offsets,
        ) = load_meta_and_code_from_filename(input_path)
    except Exception as e:
        print("ERROR: failed to load original bytecode file: %s" % input_path, file=sys.stderr)
        return 3

    tf_name_base = osp.basename(input_path)
    if tf_name_base.endswith(".pyc"):
        tf_name_base = tf_name_base[: -len(".pyc")]
    elif tf_name_base.endswith(".pyc"):
        tf_name_base = tf_name_base[: -len(".pyo")]

    version_str = version_tuple_to_str(orig_version)
    tf_name_base += ("-%s-" % version_str)

    # Write to a temporary file using write_bytecode_file
    tf = tempfile.NamedTemporaryFile(prefix=tf_name_base, suffix=".pyc", delete=False)
    tf_name = tf.name
    tf.close()  # write_bytecode_file will open/write the file itself

    try:
        write_bytecode_file(
            tf_name,
            orig_co,
            orig_magic_int,
            compilation_ts=orig_timestamp,
            filesize=orig_source_size or 0,
        )
    except TypeError:
        # Older/newer signatures might name the timestamp param differently; try without names
        try:
            write_bytecode_file(
                tf_name, orig_co, orig_magic_int, orig_timestamp, orig_source_size or 0
            )
        except Exception as e:
            print("ERROR: failed to load original bytecode file %s: %s" % (input_path, e), file=sys.stderr)
            # Cleanup
            try:
                os.unlink(tf_name)
            except Exception:
                pass
            return 4
    except Exception as e:
        print("ERROR: failed to write bytecode file: %s", e, file=sys.stderr)
        try:
            os.unlink(tf_name)
        except Exception:
            pass
        return 4

    # Compare raw bytes first
    same_bytes = False
    try:
        same_bytes = filecmp.cmp(input_path, tf_name, shallow=False)
    except Exception as e:
        print("WARNING: could not do raw byte comparison: %s" % e, file=sys.stderr)

    print("Original file:", input_path)
    print("Rewritten file:", tf_name)
    print("Raw-bytes identical:", same_bytes)
    if same_bytes:
        if unlink_on_success:
            os.unlink(tf_name)
        return 0

    compare_showing_error(input_path, tf_name)

    # Now compare by loading both and comparing metadata and code-object structure
    try:
        (
            new_version,
            new_timestamp,
            new_magic_int,
            new_co,
            new_is_pypy,
            new_source_size,
            new_sip_hash,
            new_file_offsets,
        ) = load_meta_and_code_from_filename(tf_name)
    except Exception as e:
        print(
            f"ERROR: failed to load rewritten bytecode file {tf_name}:\n\t{e}",
            file=sys.stderr,
        )
        return 5

    meta_equal = (
        orig_version == new_version
        and orig_magic_int == new_magic_int
        and (orig_timestamp == new_timestamp)
        and (orig_source_size == new_source_size)
        and (orig_sip_hash == new_sip_hash)
    )

    print(
        "Metadata equal (version, magic, timestamp, source_size, sip_hash):", meta_equal
    )
    print("Original is PyPy:", orig_is_pypy, "Rewritten is PyPy:", new_is_pypy)

    # Compare code objects
    codes_equal = compare_code_objects(orig_co, new_co)
    print("Code objects structurally equal:", codes_equal)

    # Compare file_offsets if present
    offsets_equal = orig_file_offsets == new_file_offsets
    print("File offsets equal:", offsets_equal)

    # all_identical = same_bytes and meta_equal and codes_equal and offsets_equal
    # if all_identical:
    #     print(
    #         "RESULT: files are identical both as raw bytes and in contained module/code objects."
    #     )
    #     ret = 0
    # else:
    #     print("RESULT: files differ.")
    #     # Helpful diagnostic: show which pieces disagree
    #     if not same_bytes:
    #         print("- raw-bytes differ")
    #     if not meta_equal:
    #         print("- metadata differs")
    #         print(
    #             "  original:",
    #             (
    #                 orig_version,
    #                 orig_magic_int,
    #                 orig_timestamp,
    #                 orig_source_size,
    #                 orig_sip_hash,
    #             ),
    #         )
    #         print(
    #             "  rewritten:",
    #             (
    #                 new_version,
    #                 new_magic_int,
    #                 new_timestamp,
    #                 new_source_size,
    #                 new_sip_hash,
    #             ),
    #         )
    #     if not codes_equal:
    #         print("- code objects differ (some attributes compared):")
    #         # attempt to print a short diff of co_code lengths and names
    #         try:
    #             print("  orig co_code len:", len(getattr(orig_co, "co_code", b"")))
    #             print("  new  co_code len:", len(getattr(new_co, "co_code", b"")))
    #             print("  orig co_names:", getattr(orig_co, "co_names", None))
    #             print("  new  co_names:", getattr(new_co, "co_names", None))
    #         except Exception:
    #             pass
    #     if not offsets_equal:
    #         print("- file offsets differ")
    #     ret = 1

    # Do not delete the temporary file automatically; leave it for inspection.
    print("Temporary rewritten file left at:", tf_name)
    return 1

def main() -> int:
    bad_count = 0
    for file in sys.argv[1:]:
        bad_count += roundtrip_pyc(file, unlink_on_success=False)
    return bad_count


if __name__ == "__main__":
    main()
