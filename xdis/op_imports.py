# (C) Copyright 2018-2019, 2021-2023 by Rocky Bernstein
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

"""Facilitates for importing Python opcode maps for a given Python version"""
import copy
import sys

from xdis.magics import canonic_python_version
from xdis.opcodes import (
    opcode_10,
    opcode_11,
    opcode_12,
    opcode_13,
    opcode_14,
    opcode_15,
    opcode_16,
    opcode_20,
    opcode_21,
    opcode_22,
    opcode_23,
    opcode_24,
    opcode_25,
    opcode_26,
    opcode_26pypy,
    opcode_27,
    opcode_27pypy,
    opcode_30,
    opcode_31,
    opcode_32,
    opcode_32pypy,
    opcode_33,
    opcode_33pypy,
    opcode_34,
    opcode_35,
    opcode_35pypy,
    opcode_36,
    opcode_36pypy,
    opcode_37,
    opcode_37pypy,
    opcode_38,
    opcode_38pypy,
    opcode_39,
    opcode_39pypy,
    opcode_310,
    opcode_310pypy,
    opcode_311,
    opcode_312,
)
from xdis.version_info import IS_PYPY, version_tuple_to_str

# FIXME
op_imports = {
    1.0: opcode_10,
    "1.0": opcode_10,
    1.1: opcode_11,
    "1.1": opcode_11,
    1.2: opcode_12,
    "1.2": opcode_12,
    1.3: opcode_13,
    "1.3": opcode_13,
    1.4: opcode_14,
    "1.4": opcode_14,
    1.5: opcode_15,
    "1.5": opcode_15,
    1.6: opcode_16,
    "1.6": opcode_16,
    "2.0": opcode_20,
    2.0: opcode_20,
    "2.1": opcode_21,
    2.1: opcode_21,
    "2.2": opcode_22,
    2.2: opcode_22,
    "2.3a0": opcode_23,
    2.3: opcode_23,
    "2.4b1": opcode_24,
    2.4: opcode_24,
    "2.5c2": opcode_25,
    2.5: opcode_25,
    "2.6a1": opcode_26,
    2.6: opcode_26,
    "2.7": opcode_27,
    2.7: opcode_27,
    "2.7.18candidate1": opcode_27,
    "3.0": opcode_30,
    3.0: opcode_30,
    "3.0a5": opcode_30,
    "3.1": opcode_31,
    "3.1a0+": opcode_31,
    3.1: opcode_31,
    "3.2": opcode_32,
    "3.2a2": opcode_32,
    3.2: opcode_32,
    "3.3a4": opcode_33,
    3.3: opcode_33,
    "3.4": opcode_34,
    "3.4rc2": opcode_34,
    3.4: opcode_34,
    "3.5": opcode_35,
    "3.5.1": opcode_35,
    "3.5.2": opcode_35,
    "3.5.3": opcode_35,
    "3.5.4": opcode_35,
    3.5: opcode_35,
    "3.6rc1": opcode_36,
    3.6: opcode_36,
    "3.7.0beta3": opcode_37,
    "3.7.0.beta3": opcode_37,
    "3.7.0": opcode_37,
    3.7: opcode_37,
    "3.8.0alpha0": opcode_38,
    "3.8.0a0": opcode_38,
    "3.8.0a3+": opcode_38,
    "3.8.0alpha3": opcode_38,
    "3.8.0beta2": opcode_38,
    "3.8.0rc1+": opcode_38,
    "3.8.0candidate1": opcode_38,
    "3.8": opcode_38,
    "3.9.0alpha1": opcode_39,
    "3.9.0alpha2": opcode_39,
    "3.9.0beta5": opcode_39,
    "3.9": opcode_39,
    3.9: opcode_39,
    "3.10.0rc2": opcode_310,
    "3.10": opcode_310,
    "3.11": opcode_311,
    "3.11.0": opcode_311,
    "3.11.1": opcode_311,
    "3.11.2": opcode_311,
    "3.11.3": opcode_311,
    "3.11.4": opcode_311,
    "3.11.5": opcode_311,
    "3.11a7e": opcode_311,
    "3.12.0rc2": opcode_312,
    "3.12.0": opcode_312,
    "2.6pypy": opcode_26pypy,
    "2.7pypy": opcode_27pypy,
    "2.7.12pypy": opcode_27pypy,
    "3.2pypy": opcode_32pypy,
    "3.3pypy": opcode_33pypy,
    "3.5pypy": opcode_35pypy,
    "3.6pypy": opcode_36pypy,
    "3.6.1pypy": opcode_36pypy,
    "3.7pypy": opcode_37pypy,
    "3.8.0pypy": opcode_38pypy,
    "3.8pypy": opcode_38pypy,
    "3.8.12pypy": opcode_38pypy,
    "3.8.13pypy": opcode_38pypy,
    "3.8.14pypy": opcode_38pypy,
    "3.8.15pypy": opcode_38pypy,
    "3.8.16pypy": opcode_38pypy,
    "3.8.17pypy": opcode_38pypy,
    "3.9pypy": opcode_39pypy,
    "3.9.15pypy": opcode_39pypy,
    "3.9.16pypy": opcode_39pypy,
    "3.9.17pypy": opcode_39pypy,
    "3.9.18pypy": opcode_39pypy,
    "3.10pypy": opcode_310pypy,
    "3.10.12pypy": opcode_310pypy,
}

for k, v in canonic_python_version.items():
    if v in op_imports:
        op_imports[k] = op_imports[v]


def get_opcode_module(version_info=None, variant=None):
    if version_info is None:
        version_info = sys.version_info
        if variant is None and IS_PYPY:
            variant = "pypy"
            pass
        pass
    elif isinstance(version_info, float):
        int_vers = int(version_info * 10)
        version_info = [int_vers // 10, int_vers % 10]

    vers_str = version_tuple_to_str(version_info)
    if len(version_info) > 3 and version_info[3] != "final":
        vers_str += version_tuple_to_str(version_info, start=3)

    if vers_str not in canonic_python_version:
        vers_str = version_tuple_to_str(version_info[:2])

    if variant is None:
        try:
            import platform

            variant = platform.python_implementation()
            if platform in ("Jython", "Pyston"):
                vers_str += variant
                pass
        except ImportError:
            # Python may be too old, e.g. < 2.6 or implementation may
            # just not have the ``platform`` attribute.
            pass
    elif variant != "Graal":
        vers_str += variant

    return op_imports[canonic_python_version[vers_str]]


def remap_opcodes(op_obj, alternate_opmap):
    # All these lists are 255 in length, with index, ``i``, corresponding to opcode ``i``
    if hasattr(op_obj, "REMAPPED") and op_obj.REMAPPED:
        return op_obj

    positional_opcode_lists = [
        "opname",  # Opcode's name
        "oppop",  # How many items this opcode pops off the stack
        "oppush",  # How many items this opcode pushes onto the stack
    ]

    # These lists contain all the opcodes that fit a certain description
    categorized_opcode_lists = [
        "hascompare",
        "hascondition",
        "hasconst",
        "hasfree",
        "hasjabs",
        "hasjrel",
        "haslocal",
        "hasname",
        "hasnargs",
        "hasvargs",
        "nofollow",
    ]

    new_opmap = copy.deepcopy(op_obj.opmap)
    new_lists = {}
    for list_name in positional_opcode_lists:
        if hasattr(op_obj, list_name):
            new_lists[list_name] = copy.deepcopy(getattr(op_obj, list_name))
    for list_name in categorized_opcode_lists:
        if hasattr(op_obj, list_name):
            new_lists[list_name] = copy.deepcopy(getattr(op_obj, list_name))

    new_frozensets = {}
    for i in dir(op_obj):
        item = getattr(op_obj, i)
        if isinstance(item, frozenset):
            item = list(item)
            new_frozensets[i] = copy.deepcopy(item)

    opcodes_with_args = {}
    for opname, opcode in op_obj.opmap.items():
        if opcode >= op_obj.HAVE_ARGUMENT:
            opcodes_with_args[opname] = opcode

    for opname, alt_opcode in alternate_opmap.items():
        if opname not in op_obj.opmap:
            raise KeyError(
                "The opname {} was not found in Python's original opmap for version {}".format(
                    opname, op_obj.version
                )
            )
        else:
            original_opcode = op_obj.opmap[opname]
            new_opmap[opname] = alt_opcode
            if original_opcode == alt_opcode:
                continue

            if hasattr(op_obj, opname):
                setattr(op_obj, opname, alt_opcode)

            for list_name in positional_opcode_lists:
                if not hasattr(op_obj, list_name):
                    continue
                new_opcode_list = new_lists[list_name]
                original_list = getattr(op_obj, list_name)
                new_opcode_list[alt_opcode] = original_list[original_opcode]

            for list_name in categorized_opcode_lists:
                if not hasattr(op_obj, list_name):
                    continue
                new_opcode_list = new_lists[list_name]
                original_list = getattr(op_obj, list_name)
                if original_opcode in original_list:
                    new_opcode_list[original_list.index(original_opcode)] = alt_opcode

            for set_name, frozen_set_list in new_frozensets.items():
                if original_opcode in getattr(op_obj, set_name):
                    idx = list(getattr(op_obj, set_name)).index(original_opcode)
                    frozen_set_list[idx] = alt_opcode

    new_opcodes_with_args = {}
    for opname in opcodes_with_args.keys():
        new_opcodes_with_args[opname] = new_opmap[opname]
    lowest_opcode_with_arg = min(new_opcodes_with_args.values())
    setattr(op_obj, "HAVE_ARGUMENT", lowest_opcode_with_arg)
    if hasattr(op_obj, "PJIF"):
        if hasattr(op_obj, "POP_JUMP_IF_FALSE") and "POP_JUMP_IF_FALSE" in new_opmap:
            # 2.7 and later
            setattr(op_obj, "PJIF", new_opmap["POP_JUMP_IF_FALSE"])
        if hasattr(op_obj, "JUMP_IF_FALSE") and "JUMP_IF_FALSE" in new_opmap:
            setattr(op_obj, "PJIF", new_opmap["JUMP_IF_FALSE"])
    if hasattr(op_obj, "PJIT"):
        if hasattr(op_obj, "POP_JUMP_IF_TRUE") and "POP_JUMP_IF_TRUE" in new_opmap:
            # 2.7 and later
            setattr(op_obj, "PJIT", new_opmap["POP_JUMP_IF_TRUE"])
        if hasattr(op_obj, "JUMP_IF_TRUE") and "JUMP_IF_TRUE" in new_opmap:
            setattr(op_obj, "PJIT", new_opmap["JUMP_IF_TRUE"])

    for new_list_name, new_list in new_lists.items():
        setattr(op_obj, new_list_name, new_list)
    for new_frozenset_name, new_frozenset in new_frozensets.items():
        setattr(op_obj, new_frozenset_name, frozenset(new_frozenset))

    setattr(op_obj, "opmap", new_opmap)
    setattr(op_obj, "REMAPPED", True)
    return op_obj


if __name__ == "__main__":
    print(get_opcode_module())
