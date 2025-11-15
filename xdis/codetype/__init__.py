# (C) Copyright 2020-2021, 2023-2025 by Rocky Bernstein
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
from collections import namedtuple

from xdis.codetype.base import CodeBase
from xdis.codetype.code13 import Code13
from xdis.codetype.code15 import Code15
from xdis.codetype.code20 import Code2
from xdis.codetype.code30 import Code3
from xdis.codetype.code38 import Code38
from xdis.codetype.code38graal import Code38Graal
from xdis.codetype.code310 import Code310
from xdis.codetype.code310graal import Code310Graal
from xdis.codetype.code311 import Code311, Code311FieldNames
from xdis.codetype.code311graal import Code311Graal
from xdis.version_info import IS_GRAAL, IS_PYPY, PYTHON_VERSION_TRIPLE

__docformat__ = "restructuredtext"


def codeType2Portable(code, version_triple=PYTHON_VERSION_TRIPLE, is_graal: bool=False, other_fields: dict={}):
    """Converts a native types.CodeType code object into a
    corresponding more flexible xdis Code type.
    """
    if isinstance(code, CodeBase):
        return code
    if not (isinstance(code, types.CodeType) or isinstance(code, CodeTypeUnion)):
        raise TypeError(
            "parameter expected to be a types.CodeType type; is %s instead" % type(code)
        )
    line_table_field = (
        "co_lnotab" if hasattr(code, "co_lnotab") else "co_linetable"
    )
    line_table = getattr(code, line_table_field)

    if version_triple >= (3, 0):
        if version_triple < (3, 8):
            return Code3(
                code.co_argcount,
                code.co_kwonlyargcount,
                code.co_nlocals,
                code.co_stacksize,
                code.co_flags,
                code.co_code,
                code.co_consts,
                code.co_names,
                code.co_varnames,
                code.co_filename,
                code.co_name,
                code.co_firstlineno,
                line_table,
                code.co_freevars,
                code.co_cellvars,
                # THINK ABOUT: If collection_order isn't defined, i.e. native code
                # type, should we try to extract it?
                code.collection_order if hasattr(code, "collection_order") else {},
                code.reference_objects if hasattr(code, "reference_objects") else set(),
                version_triple=version_triple,
            )
        elif version_triple < (3, 10):
            if is_graal:
                other_fields = {}
                # other_fields["condition_profileCount"]=code.condition_profileCount if hasattr(code, "condition_profileCount") else -1,
                # other_fields["endColumn"]=code.endColumn if hasattr(code, "endColumn") else -1,
                # other_fields["endLine"]=code.endLine if hasattr(code, "endLine") else -1,
                # other_fields["exception_handler_ranges"]=code.exception_handler_ranges if hasattr(code, "exception_handler_ranges") else tuple(),
                # other_fields["generalizeInputsMap"]=code.generalizeInputsMap if hasattr(code, "generalizeInputsMap") else {},
                # other_fields["generalizeVarsMap"]=code.generalizeVarsMap if hasattr(code, "generalizeVarsMap") else {},
                # other_fields["outputCanQuicken"]=code.outputCanQuicken if hasattr(code, "outputCanQuicken") else b"",
                # other_fields["primitiveConstants"]=code.primitiveConstants if hasattr(code, "primitiveConstants") else tuple(),
                # other_fields["srcOffsetTable"]=code.srcOffsetTable if hasattr(code, "srcOffsetTable") else b"",
                # other_fields["startColumn"]=code.startColumn if hasattr(code, "startColumn") else -1,
                # other_fields["startLine"]=code.startLine if hasattr(code, "startLine") else -1,
                # other_fields["variableShouldUnbox"]=code.variableShouldUnbox if hasattr(code, "variableShouldUnbox") else b"",
                return Code38Graal(
                    co_argcount=code.co_argcount,
                    co_posonlyargcount=code.co_posonlyargcount,
                    co_kwonlyargcount=code.co_kwonlyargcount,
                    co_nlocals=code.co_nlocals,
                    co_stacksize=code.co_stacksize,
                    co_flags=code.co_flags,
                    co_consts=code.co_consts,
                    co_code=code.co_code,
                    co_names=code.co_names,
                    co_varnames=code.co_varnames,
                    co_freevars=code.co_freevars,
                    co_cellvars=code.co_cellvars,
                    co_filename=code.co_filename,
                    co_name=code.co_name,
                    co_firstlineno=code.co_firstlineno,
                    co_lnotab=line_table,
                    version_triple=version_triple,
                    other_fields=other_fields,
                )
            else:
                return Code38(
                    co_argcount=code.co_argcount,
                    co_posonlyargcount=code.co_posonlyargcount,
                    co_kwonlyargcount=code.co_kwonlyargcount,
                    co_nlocals=code.co_nlocals,
                    co_stacksize=code.co_stacksize,
                    co_flags=code.co_flags,
                    co_code=code.co_code,
                    co_consts=code.co_consts,
                    co_names=code.co_names,
                    co_varnames=code.co_varnames,
                    co_freevars=code.co_freevars,
                    co_cellvars=code.co_cellvars,
                    co_filename=code.co_filename,
                    co_name=code.co_name,
                    co_firstlineno=code.co_firstlineno,
                    co_lnotab=line_table,
                    version_triple=version_triple,
                )
        elif version_triple[:2] == (3, 10) or IS_PYPY and version_triple[:2] == (3, 11):
            if is_graal:
                return Code310Graal(
                    co_argcount=code.co_argcount,
                    co_posonlyargcount=code.co_posonlyargcount,
                    co_kwonlyargcount=code.co_kwonlyargcount,
                    co_nlocals=code.co_nlocals,
                    co_stacksize=code.co_stacksize,
                    co_flags=code.co_flags,
                    co_code=code.co_code,
                    co_consts=code.co_consts,
                    co_names=code.co_names,
                    co_varnames=code.co_varnames,
                    co_freevars=code.co_freevars,
                    co_cellvars=code.co_cellvars,
                    co_filename=code.co_filename,
                    co_name=code.co_name,
                    co_firstlineno=code.co_firstlineno,
                    co_linetable=line_table,
                    version_triple=version_triple,
                    other_fields=other_fields,
                )
            else:
                return Code310(
                    co_argcount=code.co_argcount,
                    co_posonlyargcount=code.co_posonlyargcount,
                    co_kwonlyargcount=code.co_kwonlyargcount,
                    co_nlocals=code.co_nlocals,
                    co_stacksize=code.co_stacksize,
                    co_flags=code.co_flags,
                    co_code=code.co_code,
                    co_consts=code.co_consts,
                    co_names=code.co_names,
                    co_varnames=code.co_varnames,
                    co_freevars=code.co_freevars,
                    co_cellvars=code.co_cellvars,
                    co_filename=code.co_filename,
                    co_name=code.co_name,
                    co_firstlineno=code.co_firstlineno,
                    co_linetable=line_table,
                    version_triple=version_triple,
                )
        elif version_triple[:2] >= (3, 11):
            if is_graal:

                return Code311Graal(
                    co_argcount=code.co_argcount,
                    co_posonlyargcount=code.co_posonlyargcount,
                    co_kwonlyargcount=code.co_kwonlyargcount,
                    co_nlocals=code.co_nlocals,
                    co_stacksize=code.co_stacksize,
                    co_flags=code.co_flags,
                    co_consts=code.co_consts,
                    co_code=code.co_code,
                    co_names=code.co_names,
                    co_varnames=code.co_varnames,
                    co_freevars=code.co_freevars,
                    co_cellvars=code.co_cellvars,
                    co_filename=code.co_filename,
                    co_name=code.co_name,
                    co_qualname=code.co_qualname,
                    co_firstlineno=code.co_firstlineno,
                    co_linetable=line_table,
                    co_exceptiontable=code.co_exceptiontable,
                    version_triple=version_triple,
                    other_fields=other_fields,
                )
            else:
                return Code311(
                    co_argcount=code.co_argcount,
                    co_posonlyargcount=code.co_posonlyargcount,
                    co_kwonlyargcount=code.co_kwonlyargcount,
                    co_nlocals=code.co_nlocals,
                    co_stacksize=code.co_stacksize,
                    co_flags=code.co_flags,
                    co_consts=code.co_consts,
                    co_code=code.co_code,
                    co_names=code.co_names,
                    co_varnames=code.co_varnames,
                    co_freevars=code.co_freevars,
                    co_cellvars=code.co_cellvars,
                    co_filename=code.co_filename,
                    co_name=code.co_name,
                    co_qualname=code.co_qualname,
                    co_firstlineno=code.co_firstlineno,
                    co_linetable=line_table,
                    co_exceptiontable=code.co_exceptiontable,
                    version_triple=version_triple,
                )
    elif version_triple > (2, 0):
        # 2.0 .. 2.7
        return Code2(
            co_argcount=code.co_argcount,
            co_nlocals=code.co_nlocals,
            co_stacksize=code.co_stacksize,
            co_flags=code.co_flags,
            co_code=code.co_code,
            co_consts=code.co_consts,
            co_names=code.co_names,
            co_varnames=code.co_varnames,
            co_filename=code.co_filename,
            co_name=code.co_name,
            co_firstlineno=code.co_firstlineno,
            co_lnotab=code.co_lnotab,
            co_freevars=code.co_freevars,  # not in 1.x
            co_cellvars=code.co_cellvars,  # not in 1.x
            # THINK ABOUT: If collection_order isn't defined, i.e. native code
            # type, should we try to extract it?
            collection_order=(
                code.collection_order if hasattr(code, "collection_order") else {}
            ),
            reference_objects=(
                code.reference_objects if hasattr(code, "reference_objects") else set()
            ),
            version_triple=version_triple,
        )
    else:
        # 1.0 .. 1.5
        if version_triple < (1, 5):
            # 1.0 .. 1.3
            return Code13(
                code.co_argcount,
                code.co_nlocals,
                code.co_flags,
                code.co_code,
                code.co_consts,
                code.co_names,
                code.co_varnames,
                code.co_filename,
                code.co_name,
            )
        else:
            return Code15(
                code.co_argcount,
                code.co_nlocals,
                code.co_stacksize,  # not in 1.0..1.4
                code.co_flags,
                code.co_code,
                code.co_consts,
                code.co_names,
                code.co_varnames,
                code.co_filename,
                code.co_name,
                code.co_firstlineno,  # Not in 1.0..1.4
                code.co_lnotab,  # Not in 1.0..1.4
            )


def portableCodeType(version_triple=PYTHON_VERSION_TRIPLE, is_graal=IS_GRAAL):
    """
    Return the portable CodeType version for the supplied Python release version.
    `version` is a floating-point number, like 2.7, or 3.9. If no version
    number is supplied we'll use the current interpreter version.
    """
    if version_triple >= (3, 0):
        if version_triple < (3, 8):
            # 3.0 .. 3.7
            return Code3
        elif version_triple < (3, 10):
            # 3.8 ... 3.9
            return Code38
        elif version_triple[:2] == (3, 10) or IS_PYPY and version_triple[:2] == (3, 11):
            # 3.10
            if is_graal:
                return Code310Graal
            else:
                return Code310
        elif version_triple[:2] >= (3, 11):
            # 3.11 ...
            if is_graal:
                return Code311Graal
            else:
                return Code311
    elif version_triple > (2, 0):
        # 2.0 .. 2.7
        return Code2
    else:
        # 1.0 .. 1.5
        if version_triple <= (1, 3):
            return Code13
        else:
            return Code15


# In contrast to Code3, Code2, etc. you can use CodeTypeUnint for building
# an incomplete code type, which might be converted to another code type
# later.
CodeTypeUnionFields = tuple(
    Code311FieldNames.split()
    + ["collection_order", "reference_objects", "version_triple", "other_fields"]
)
CodeTypeUnion = namedtuple("CodeTypeUnion", CodeTypeUnionFields)


# Note: default values of `None` indicate a required parameter.
# default values of -1, (None,) or "" indicate an unsupplied parameter.
def to_portable(
    co_argcount=-1,
    co_posonlyargcount=-1,  # 3.8 .. 3.10
    co_kwonlyargcount=-1,  # 3.0+
    co_nlocals=0,
    co_stacksize=-1,  # 1.5+
    co_flags=0,
    co_code="",  # 3.0+ this type changes from <str> to <bytes>
    co_consts=tuple(),
    co_names=tuple(),
    co_varnames=tuple(),
    co_filename="??",
    co_name=None,
    co_qualname="??",
    co_firstlineno: int = -1,
    co_lnotab: str = "",  # 1.5+; 3.0+ this type changes from <str> to <bytes>
    # In 3.11 it is different
    co_freevars=tuple(),  # 2.0+
    co_cellvars=tuple(),  # 2.0+
    co_exceptiontable=None,  # 3.11+
    version_triple=PYTHON_VERSION_TRIPLE,
    collection_order={},
    reference_objects=set(),
    other_fields: dict={},
):
    is_graal = "srcOffsetTable" in other_fields
    code = CodeTypeUnion(
        co_argcount=co_argcount,
        co_posonlyargcount=co_posonlyargcount,
        co_kwonlyargcount=co_kwonlyargcount,
        co_nlocals=co_nlocals,
        co_stacksize=co_stacksize,
        co_flags=co_flags,
        co_code=co_code,
        co_consts=co_consts,
        co_names=co_names,
        co_varnames=co_varnames,
        co_filename=co_filename,
        co_name=co_name,
        co_qualname=co_name if co_qualname is None else co_qualname,
        co_firstlineno=co_firstlineno,
        co_linetable=co_lnotab,
        co_lnotab=co_lnotab,
        co_freevars=co_freevars,
        co_cellvars=co_cellvars,
        co_exceptiontable=co_exceptiontable,
        collection_order=collection_order,
        reference_objects=reference_objects,
        version_triple=version_triple,
        other_fields=other_fields,
    )
    return codeType2Portable(code, version_triple, is_graal=is_graal, other_fields=other_fields)


if __name__ == "__main__":
    x = codeType2Portable(to_portable.__code__)
    print(x)
