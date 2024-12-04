import types
from copy import deepcopy

from xdis.codetype.code311 import Code311, Code311FieldTypes
from xdis.version_info import PYTHON_VERSION_TRIPLE, version_tuple_to_str

Code312FieldNames = Code311FieldTypes.copy()
Code312FieldTypes = deepcopy(Code311FieldTypes)


class Code312(Code311):
    """Class for a Python 3.13+ code object
    New CPython "undocumented" changes make this necessary to parse the co_linetable with co_lines().
    See: https://github.com/python/cpython/blob/aaed91cabcedc16c089c4b1c9abb1114659a83d3/Objects/codeobject.c#L1245C1-L1245C17
    """

    def __init__(
        self,
        co_argcount,
        co_posonlyargcount,
        co_kwonlyargcount,
        co_nlocals,
        co_stacksize,
        co_flags,
        co_consts,
        co_code,
        co_names,
        co_varnames,
        co_freevars,
        co_cellvars,
        co_filename,
        co_name,
        co_qualname,
        co_firstlineno,
        co_linetable,
        co_exceptiontable,
    ):
        # Keyword argument parameters in the call below is more robust.
        # Since things change around, robustness is good.
        super(Code312, self).__init__(
            co_argcount=co_argcount,
            co_posonlyargcount=co_posonlyargcount,
            co_kwonlyargcount=co_kwonlyargcount,
            co_nlocals=co_nlocals,
            co_stacksize=co_stacksize,
            co_flags=co_flags,
            co_consts=co_consts,
            co_code=co_code,
            co_names=co_names,
            co_varnames=co_varnames,
            co_freevars=co_freevars,
            co_cellvars=co_cellvars,
            co_filename=co_filename,
            co_name=co_name,
            co_qualname=co_qualname,
            co_firstlineno=co_firstlineno,
            co_linetable=co_linetable,
            co_exceptiontable=co_exceptiontable,
        )
        self.fieldtypes = Code312FieldTypes
        if type(self) == Code312:
            self.check()

    def to_native(self):
        if not (PYTHON_VERSION_TRIPLE >= (3, 12)):
            raise TypeError(
                "Python Interpreter needs to be in 3.12 or greater; is %s"
                % version_tuple_to_str()
            )

        code = deepcopy(self)
        code.freeze()
        try:
            code.check()
        except AssertionError as e:
            raise TypeError(e)

        return types.CodeType(
            code.co_argcount,
            code.co_posonlyargcount,
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
            code.co_qualname,
            code.co_firstlineno,
            code.co_linetable,
            code.co_exceptiontable,
            code.co_freevars,
            code.co_cellvars,
        )
