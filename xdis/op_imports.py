# (C) Copyright 2018-2019, 2021-2022 by Rocky Bernstein
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

"""Facilitates importing opmaps for the a given Python version"""
import copy
import sys
from xdis.magics import canonic_python_version

from xdis.opcodes import opcode_10 as opcode_10
from xdis.opcodes import opcode_11 as opcode_11
from xdis.opcodes import opcode_12 as opcode_12
from xdis.opcodes import opcode_13 as opcode_13
from xdis.opcodes import opcode_14 as opcode_14
from xdis.opcodes import opcode_15 as opcode_15
from xdis.opcodes import opcode_16 as opcode_16
from xdis.opcodes import opcode_20 as opcode_20
from xdis.opcodes import opcode_21 as opcode_21
from xdis.opcodes import opcode_22 as opcode_22
from xdis.opcodes import opcode_23 as opcode_23
from xdis.opcodes import opcode_24 as opcode_24
from xdis.opcodes import opcode_25 as opcode_25
from xdis.opcodes import opcode_26 as opcode_26
from xdis.opcodes import opcode_27 as opcode_27
from xdis.opcodes import opcode_30 as opcode_30
from xdis.opcodes import opcode_31 as opcode_31
from xdis.opcodes import opcode_32 as opcode_32
from xdis.opcodes import opcode_33 as opcode_33
from xdis.opcodes import opcode_34 as opcode_34
from xdis.opcodes import opcode_35 as opcode_35
from xdis.opcodes import opcode_36 as opcode_36
from xdis.opcodes import opcode_37 as opcode_37
from xdis.opcodes import opcode_38 as opcode_38
from xdis.opcodes import opcode_39 as opcode_39
from xdis.opcodes import opcode_310 as opcode_310

from xdis.opcodes import opcode_26pypy as opcode_26pypy
from xdis.opcodes import opcode_27pypy as opcode_27pypy
from xdis.opcodes import opcode_32pypy as opcode_32pypy
from xdis.opcodes import opcode_33pypy as opcode_33pypy
from xdis.opcodes import opcode_35pypy as opcode_35pypy
from xdis.opcodes import opcode_36pypy as opcode_36pypy
from xdis.opcodes import opcode_37pypy as opcode_37pypy
from xdis.opcodes import opcode_38pypy as opcode_38pypy
from xdis.opcodes import opcode_39pypy as opcode_39pypy

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
    "3.9pypy": opcode_39pypy,
    "3.9.15pypy": opcode_39pypy,
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
    if variant is None:
        try:
            import platform

            variant = platform.python_implementation()
            if platform in ("Jython", "Pyston"):
                vers_str += variant
                pass
        except:
            # Python may be too old, e.g. < 2.6 or implementation may
            # just not have platform
            pass
    else:
        vers_str += variant

    return op_imports[canonic_python_version[vers_str]]


def remap_opcodes(op_obj, alternate_opmap):
    # All these lists are 255 in length, with index i corresponding to opcode i
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
