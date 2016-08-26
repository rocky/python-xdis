# History of CPython opcodes changes.

Opcodes are generally mentioned in the Python Library Reference manual. See
that for more information.

Here we have the various changes in CPython opcodes. This is embodies in the code
in directory xdis/opcodes

## Python 2.4

### Added

* NOP
* LIST_APPEND
* YIELD_VALUE

### Removed

* YIELD_STMT
* FOR_LOOP
* SET_LINENO

## Python 2.5

## Python 2.6

### Added

* STORE_MAP

## Python 2.7

`JUMP_IF_FALSE` and `JUMP_IF_TRUE` semantics change a little and become
`JUMP_IF_FALSE_OR_POP` and `JUMP_IF_TRUE_OR_POP`. Later in 3.0 `JUMP_IF_FALSE` and
`JUMP_IF_TRUE` come back.


### Added

* BUILD_SET
* JUMP_IF_FALSE_OR_POP
* JUMP_IF_TRUE_OR_POP
* POP_JUMP_IF_FALSE
* POP_JUMP_IF_TRUE
* SETUP_WITH
* SET_ADD
* MAP_ADD

### Removed

* JUMP_IF_FALSE
* JUMP_IF_TRUE

## Python 3.0

`JUMP_IF_FALSE` and JUMP_IF_TRUE` come back from Python 2.6. Custom slice operators
and print operators are removed.

### Added

* STORE_LOCALS
* LOAD_BUILD_CLASS
* POP_EXCEPT
* UNPACK_EX
* JUMP_IF_FALSE
* JUMP_IF_TRUE

### Removed

* UNARY_CONVERT
* BINARY_DIVIDE
* SLICE+0
* SLICE+1
* SLICE+2
* SLICE+3
* STORE_SLICE+0
* STORE_SLICE+1
* STORE_SLICE+2
* STORE_SLICE+3
* DELETE_SLICE+0
* DELETE_SLICE+1
* DELETE_SLICE+2
* DELETE_SLICE+3
* INPLACE_DIVIDE
* PRINT_ITEM
* PRINT_NEWLINE
* PRINT_ITEM_TO
* PRINT_NEWLINE_TO
* LOAD_LOCALS
* EXEC_STMT
* BUILD_CLASS
* JUMP_IF_FALSE_OR_POP
* JUMP_IF_TRUE_OR_POP
* POP_JUMP_IF_FALSE
* POP_JUMP_IF_TRUE
* SETUP_WITH
* MAP_ADD

## Python 3.1

### Added

* JUMP_IF_FALSE_OR_POP
* JUMP_IF_TRUE_OR_POP
* POP_JUMP_IF_FALSE
* POP_JUMP_IF_TRUE
* MAP_ADD

### Removed

* JUMP_IF_FALSE
* JUMP_IF_TRUE

## Python 3.2

### Renamed

* DUP_TOP_TWO from DUP_TOPX_2

### Added

* DELETE_DEREF
* SETUP_WITH

### Removed
* ROT_FOUR

## Python 3.3

No changes

## Python 3.4

No changes

## Python 3.5

Added:

* BINARY_MATRIX_MULTIPLY
* INPLACE_MATRIX_MULTIPLY
* GET_AITER
* GET_ANEXT
* BEFORE_ASYNC_WITH
* GET_YIELD_FROM_ITER
* GET_AWAITABLE
* WITH_CLEANUP_START
* WITH_CLEANUP_FINISH
* BUILD_LIST_UNPACK
* BUILD_MAP_UNPACK
* BUILD_MAP_UNPACK_WITH_CALL
* BUILD_TUPLE_UNPACK
* BUILD_SET_UNPACK
* SETUP_ASYNC_WITH

## Python 3.6

Added:

* FORMAT_VALUE  (used in format specifiers)
* BUILD_CONST_KEY_MAP (in 3.6.0a3)

Removed:

* MAKE_CLOSURE
