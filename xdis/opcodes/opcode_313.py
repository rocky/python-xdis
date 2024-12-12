"""
CPython 3.13 bytecode opcodes
"""

import xdis.opcodes.opcode_312 as opcode_312
from xdis.opcodes.base import def_op, finalize_opcodes, init_opdata, rm_op, update_pj3

version_tuple = (3, 13)
python_implementation = "CPython"

loc = locals()

init_opdata(loc, opcode_312, version_tuple)

# extend op tables for new pseudo ops
loc["opname"].extend(["<267>"])
loc["oppop"].extend([0])
loc["oppush"].extend([0])

# have argument changed in 3.13
HAVE_ARGUMENT = 44

# fmt: off
## Lots of ops changed opcodes in 3.13 so this is long...
## These are removed or replaced since 3.12...
#           OP NAME                      OPCODE
#----------------------------------------------
rm_op(loc, "POP_TOP"                          , 1)
rm_op(loc, "PUSH_NULL"                        , 2)
rm_op(loc, "INTERPRETER_EXIT"                 , 3)
rm_op(loc, "END_FOR"                          , 4)
rm_op(loc, "END_SEND"                         , 5)
rm_op(loc, "NOP"                              , 9)
rm_op(loc, "UNARY_NEGATIVE"                   , 11)
rm_op(loc, "UNARY_NOT"                        , 12)
rm_op(loc, "UNARY_INVERT"                     , 15)
rm_op(loc, "BINARY_SUBSCR"                    , 25)
rm_op(loc, "BINARY_SLICE"                     , 26)
rm_op(loc, "STORE_SLICE"                      , 27)
rm_op(loc, "GET_LEN"                          , 30)
rm_op(loc, "MATCH_MAPPING"                    , 31)
rm_op(loc, "MATCH_SEQUENCE"                   , 32)
rm_op(loc, "MATCH_KEYS"                       , 33)
rm_op(loc, "PUSH_EXC_INFO"                    , 35)
rm_op(loc, "CHECK_EXC_MATCH"                  , 36)
rm_op(loc, "CHECK_EG_MATCH"                   , 37)
rm_op(loc, "WITH_EXCEPT_START"                , 49)
rm_op(loc, "GET_AITER"                        , 50)
rm_op(loc, "GET_ANEXT"                        , 51)
rm_op(loc, "BEFORE_ASYNC_WITH"                , 52)
rm_op(loc, "BEFORE_WITH"                      , 53)
rm_op(loc, "END_ASYNC_FOR"                    , 54)
rm_op(loc, "CLEANUP_THROW"                    , 55)
rm_op(loc, "DELETE_SUBSCR"                    , 61)
rm_op(loc, "GET_ITER"                         , 68)
rm_op(loc, "GET_YIELD_FROM_ITER"              , 69)
rm_op(loc, "LOAD_BUILD_CLASS"                 , 71)
rm_op(loc, "LOAD_ASSERTION_ERROR"             , 74)
rm_op(loc, "RETURN_GENERATOR"                 , 75)
rm_op(loc, "RETURN_VALUE"                     , 83)
rm_op(loc, "SETUP_ANNOTATIONS"                , 85)
rm_op(loc, "LOAD_LOCALS"                      , 87)
rm_op(loc, "POP_EXCEPT"                       , 89)
rm_op(loc, "STORE_NAME"                       , 90)
rm_op(loc, "DELETE_NAME"                      , 91)
rm_op(loc, "UNPACK_SEQUENCE"                  , 92)
rm_op(loc, "FOR_ITER"                         , 93)
rm_op(loc, "UNPACK_EX"                        , 94)
rm_op(loc, "STORE_ATTR"                       , 95)
rm_op(loc, "DELETE_ATTR"                      , 96)
rm_op(loc, "STORE_GLOBAL"                     , 97)
rm_op(loc, "DELETE_GLOBAL"                    , 98)
rm_op(loc, "SWAP"                             , 99)
rm_op(loc, "LOAD_CONST"                       , 100)
rm_op(loc, "LOAD_NAME"                        , 101)
rm_op(loc, "BUILD_TUPLE"                      , 102)
rm_op(loc, "BUILD_LIST"                       , 103)
rm_op(loc, "BUILD_SET"                        , 104)
rm_op(loc, "BUILD_MAP"                        , 105)
rm_op(loc, "COMPARE_OP"                       , 107)
rm_op(loc, "IMPORT_NAME"                      , 108)
rm_op(loc, "IMPORT_FROM"                      , 109)
rm_op(loc, "JUMP_FORWARD"                     , 110)
rm_op(loc, "POP_JUMP_IF_FALSE"                , 114)
rm_op(loc, "POP_JUMP_IF_TRUE"                 , 115)
rm_op(loc, "LOAD_GLOBAL"                      , 116)
rm_op(loc, "IS_OP"                            , 117)
rm_op(loc, "CONTAINS_OP"                      , 118)
rm_op(loc, "RERAISE"                          , 119)
rm_op(loc, "COPY"                             , 120)
rm_op(loc, "RETURN_CONST"                     , 121)
rm_op(loc, "BINARY_OP"                        , 122)
rm_op(loc, "SEND"                             , 123)
rm_op(loc, "LOAD_FAST"                        , 124)
rm_op(loc, "STORE_FAST"                       , 125)
rm_op(loc, "DELETE_FAST"                      , 126)
rm_op(loc, "LOAD_FAST_CHECK"                  , 127)
rm_op(loc, "POP_JUMP_IF_NOT_NONE"             , 128)
rm_op(loc, "POP_JUMP_IF_NONE"                 , 129)
rm_op(loc, "RAISE_VARARGS"                    , 130)
rm_op(loc, "GET_AWAITABLE"                    , 131)
rm_op(loc, "MAKE_FUNCTION"                    , 132)
rm_op(loc, "BUILD_SLICE"                      , 133)
rm_op(loc, "JUMP_BACKWARD_NO_INTERRUPT"       , 134)
rm_op(loc, "MAKE_CELL"                        , 135)
rm_op(loc, "LOAD_DEREF"                       , 137)
rm_op(loc, "STORE_DEREF"                      , 138)
rm_op(loc, "DELETE_DEREF"                     , 139)
rm_op(loc, "JUMP_BACKWARD"                    , 140)
rm_op(loc, "LOAD_SUPER_ATTR"                  , 141)
rm_op(loc, "CALL_FUNCTION_EX"                 , 142)
rm_op(loc, "LOAD_FAST_AND_CLEAR"              , 143)
rm_op(loc, "EXTENDED_ARG"                     , 144)
rm_op(loc, "LIST_APPEND"                      , 145)
rm_op(loc, "SET_ADD"                          , 146)
rm_op(loc, "MAP_ADD"                          , 147)
rm_op(loc, "YIELD_VALUE"                      , 150)
rm_op(loc, "RESUME"                           , 151)
rm_op(loc, "MATCH_CLASS"                      , 152)
rm_op(loc, "FORMAT_VALUE"                     , 155)
rm_op(loc, "BUILD_CONST_KEY_MAP"              , 156)
rm_op(loc, "BUILD_STRING"                     , 157)
rm_op(loc, "LIST_EXTEND"                      , 162)
rm_op(loc, "SET_UPDATE"                       , 163)
rm_op(loc, "DICT_MERGE"                       , 164)
rm_op(loc, "DICT_UPDATE"                      , 165)
rm_op(loc, "CALL"                             , 171)
rm_op(loc, "KW_NAMES"                         , 172)
rm_op(loc, "CALL_INTRINSIC_1"                 , 173)
rm_op(loc, "CALL_INTRINSIC_2"                 , 174)
rm_op(loc, "LOAD_FROM_DICT_OR_GLOBALS"        , 175)
rm_op(loc, "LOAD_FROM_DICT_OR_DEREF"          , 176)
rm_op(loc, "LOAD_CLOSURE"                     , 136)  # now a psuedo-instruction replaced with LOAD_FAST
rm_op(loc, "COPY_FREE_VARS"                   , 149)
rm_op(loc, "INSTRUMENTED_LOAD_SUPER_ATTR"     , 237)
rm_op(loc, "INSTRUMENTED_POP_JUMP_IF_NONE"    , 238)
rm_op(loc, "INSTRUMENTED_POP_JUMP_IF_NOT_NONE", 239)
rm_op(loc, "INSTRUMENTED_RESUME"              , 240)
rm_op(loc, "INSTRUMENTED_CALL"                , 241)
rm_op(loc, "INSTRUMENTED_RETURN_VALUE"        , 242)
rm_op(loc, "INSTRUMENTED_YIELD_VALUE"         , 243)
rm_op(loc, "INSTRUMENTED_CALL_FUNCTION_EX"    , 244)
rm_op(loc, "INSTRUMENTED_JUMP_FORWARD"        , 245)
rm_op(loc, "INSTRUMENTED_JUMP_BACKWARD"       , 246)
rm_op(loc, "INSTRUMENTED_RETURN_CONST"        , 247)
rm_op(loc, "INSTRUMENTED_FOR_ITER"            , 248)
rm_op(loc, "INSTRUMENTED_POP_JUMP_IF_FALSE"   , 249)
rm_op(loc, "INSTRUMENTED_END_FOR"             , 251)
rm_op(loc, "INSTRUMENTED_END_SEND"            , 252)
rm_op(loc, "INSTRUMENTED_INSTRUCTION"         , 253)
rm_op(loc, "SETUP_FINALLY"                    , 256)
rm_op(loc, "SETUP_CLEANUP"                    , 257)
rm_op(loc, "POP_BLOCK"                        , 259)
rm_op(loc, "JUMP"                             , 260)
rm_op(loc, "JUMP_NO_INTERRUPT"                , 261)
rm_op(loc, "LOAD_METHOD"                      , 262)
rm_op(loc, "LOAD_SUPER_METHOD"                , 263)
rm_op(loc, "LOAD_ZERO_SUPER_METHOD"           , 264)
rm_op(loc, "LOAD_ZERO_SUPER_ATTR"             , 265)
rm_op(loc, "STORE_FAST_MAYBE_NULL"            , 266)

## new or redefined ops
#            OP NAME                              OPCODE POP PUSH
# ---------------------------------------------------------------
def_op(loc, "BEFORE_ASYNC_WITH"                , 1   , 0 , 1)
def_op(loc, "BEFORE_WITH"                      , 2   , 0 , 1)
def_op(loc, "BINARY_SLICE"                     , 4   , 2 , 0)
def_op(loc, "BINARY_SUBSCR"                    , 5   , 2 , 1)
def_op(loc, "CHECK_EG_MATCH"                   , 6   , 0 , 0)
def_op(loc, "CHECK_EXC_MATCH"                  , 7   , 0 , 0)
def_op(loc, "CLEANUP_THROW"                    , 8   , 2 , 1)
def_op(loc, "DELETE_SUBSCR"                    , 9   , 2 , 0)
def_op(loc, "END_ASYNC_FOR"                    , 10  , 2 , 0)
def_op(loc, "END_FOR"                          , 11  , 1 , 0)
def_op(loc, "END_SEND"                         , 12  , 1 , 0)
def_op(loc, "EXIT_INIT_CHECK"                  , 13  , 1 , 0)
def_op(loc, "FORMAT_WITH_SPEC"                 , 15  , 1 , 0)
def_op(loc, "GET_AITER"                        , 16  , 1 , 1)
def_op(loc, "GET_ANEXT"                        , 18  , 0 , 1)
def_op(loc, "GET_ITER"                         , 19  , 1 , 1)
def_op(loc, "GET_LEN"                          , 20  , 0 , 1)
def_op(loc, "GET_YIELD_FROM_ITER"              , 21  , 1 , 1)
def_op(loc, "INTERPRETER_EXIT"                 , 22  , 1 , 0)
def_op(loc, "LOAD_ASSERTION_ERROR"             , 23  , 0 , 1)
def_op(loc, "LOAD_BUILD_CLASS"                 , 24  , 0 , 1)
def_op(loc, "LOAD_LOCALS"                      , 25  , 0 , 1)
def_op(loc, "MAKE_FUNCTION"                    , 26  , -2, 1)
def_op(loc, "MATCH_KEYS"                       , 27  , 0 , 1)
def_op(loc, "MATCH_MAPPING"                    , 28  , 0 , 1)
def_op(loc, "MATCH_SEQUENCE"                   , 29  , 0 , 1)
def_op(loc, "NOP"                              , 30  , 0 , 0)
def_op(loc, "POP_EXCEPT"                       , 31  , 1 , 0)
def_op(loc, "POP_TOP"                          , 32  , 1 , 0)
def_op(loc, "PUSH_EXC_INFO"                    , 33  , 0 , 1)
def_op(loc, "PUSH_NULL"                        , 34  , 0 , 1)
def_op(loc, "RETURN_GENERATOR"                 , 35  , 0 , 1)
def_op(loc, "RETURN_VALUE"                     , 36  , 1 , 0)
def_op(loc, "SETUP_ANNOTATIONS"                , 37  , 1 , 1)
def_op(loc, "STORE_SLICE"                      , 38  , 4 , 0)
def_op(loc, "STORE_SUBSCR"                     , 39  , 3 , 0)
def_op(loc, "UNARY_INVERT"                     , 41  , 1 , 1)
def_op(loc, "UNARY_NEGATIVE"                   , 42  , 1 , 1)
def_op(loc, "UNARY_NOT"                        , 43  , 1 , 1)
def_op(loc, "WITH_EXCEPT_START"                , 44  , 0 , 1)
def_op(loc, "BINARY_OP"                        , 45  , 2 , 1)
def_op(loc, "BUILD_CONST_KEY_MAP"              , 46  , -2, 1)
def_op(loc, "BUILD_LIST"                       , 47  , -1, 1)
def_op(loc, "BUILD_MAP"                        , 48  , -1, -1)
def_op(loc, "BUILD_SET"                        , 49  , -1, 1)
def_op(loc, "BUILD_SLICE"                      , 50  , 2 , 1)
def_op(loc, "BUILD_STRING"                     , 51  , -2, 2)
def_op(loc, "BUILD_TUPLE"                      , 52  , -1, 1)
def_op(loc, "CALL"                             , 53  , 1 , 0)
def_op(loc, "CALL_FUNCTION_EX"                 , 54  , -2, 1)
def_op(loc, "CALL_INTRINSIC_1"                 , 55  , 1 , 1)
def_op(loc, "CALL_INTRINSIC_2"                 , 56  , 2 , 1)
def_op(loc, "COMPARE_OP"                       , 58  , 2 , 1)
def_op(loc, "CONTAINS_OP"                      , 59  , 2 , 1)
def_op(loc, "COPY"                             , 61  , 0 , 1)
def_op(loc, "COPY_FREE_VARS"                   , 62  , 0 , 0)
def_op(loc, "DELETE_ATTR"                      , 63  , 1 , 0)
def_op(loc, "DELETE_DEREF"                     , 64  , 0 , 0)
def_op(loc, "DELETE_FAST"                      , 65  , 0 , 0)
def_op(loc, "DELETE_GLOBAL"                    , 66  , 0 , 0)
def_op(loc, "DELETE_NAME"                      , 67  , 0 , 0)
def_op(loc, "DICT_MERGE"                       , 68  , 2 , 1)
def_op(loc, "DICT_UPDATE"                      , 69  , 2 , 1)
def_op(loc, "ENTER_EXECUTOR"                   , 70  , 0 , 0)
def_op(loc, "EXTENDED_ARG"                     , 71  , 0 , 0)
def_op(loc, "FOR_ITER"                         , 72  , 0 , 1)
def_op(loc, "GET_AWAITABLE"                    , 73  , 0 , 0)
def_op(loc, "IMPORT_FROM"                      , 74  , 0 , 1)
def_op(loc, "IMPORT_NAME"                      , 75  , 2 , 1)
def_op(loc, "IS_OP"                            , 76  , 2 , 1)
def_op(loc, "JUMP_BACKWARD"                    , 77  , 0 , 0)
def_op(loc, "JUMP_BACKWARD_NO_INTERRUPT"       , 78  , 0 , 0)
def_op(loc, "JUMP_FORWARD"                     , 79  , 0 , 0)
def_op(loc, "LIST_APPEND"                      , 80  , 2 , 1)
def_op(loc, "LIST_EXTEND"                      , 81  , 2 , 1)
def_op(loc, "LOAD_ATTR"                        , 82  , 1 , 1)
def_op(loc, "LOAD_CONST"                       , 83  , 0 , 1)
def_op(loc, "LOAD_DEREF"                       , 84  , 0 , 1)
def_op(loc, "LOAD_FAST"                        , 85  , 0 , 1)
def_op(loc, "LOAD_FAST_AND_CLEAR"              , 86  , 0 , 1)
def_op(loc, "LOAD_FAST_CHECK"                  , 87  , 0 , 1)
def_op(loc, "LOAD_FAST_LOAD_FAST"              , 88  , 0 , 2)
def_op(loc, "LOAD_FROM_DICT_OR_DEREF"          , 89  , 1 , 1)
def_op(loc, "LOAD_FROM_DICT_OR_GLOBALS"        , 90  , 1 , 1)
def_op(loc, "LOAD_GLOBAL"                      , 91  , 0 , 1)
def_op(loc, "LOAD_NAME"                        , 92  , 0 , 1)
def_op(loc, "LOAD_SUPER_ATTR"                  , 93  , 3 , 1)
def_op(loc, "MAKE_CELL"                        , 94  , 0 , 0)
def_op(loc, "MAP_ADD"                          , 95  , 3 , 1)
def_op(loc, "MATCH_CLASS"                      , 96  , 3 , 1)
def_op(loc, "POP_JUMP_IF_FALSE"                , 97  , 1 , 0)
def_op(loc, "POP_JUMP_IF_NONE"                 , 98  , 1 , 0)
def_op(loc, "POP_JUMP_IF_NOT_NONE"             , 99  , 1 , 0)
def_op(loc, "POP_JUMP_IF_TRUE"                 , 100 , 1 , 0)
def_op(loc, "RAISE_VARARGS"                    , 101 , -1, 1)
def_op(loc, "RERAISE"                          , 102 , 1 , 0)
def_op(loc, "RETURN_CONST"                     , 103 , 0 , 0)
def_op(loc, "SEND"                             , 104 , 0 , 0)
def_op(loc, "SET_ADD"                          , 105 , 1 , 0)
def_op(loc, "SET_UPDATE"                       , 107 , 2 , 1)
def_op(loc, "STORE_ATTR"                       , 108 , 2 , 0)
def_op(loc, "STORE_DEREF"                      , 109 , 1 , 0)
def_op(loc, "STORE_FAST"                       , 110 , 1 , 0)
def_op(loc, "STORE_FAST_LOAD_FAST"             , 111 , 1 , 1)
def_op(loc, "STORE_FAST_STORE_FAST"            , 112 , 2 , 0)
def_op(loc, "STORE_GLOBAL"                     , 113 , 1 , 0)
def_op(loc, "STORE_NAME"                       , 114 , 1 , 0)
def_op(loc, "SWAP"                             , 115 , 0 , 0)
def_op(loc, "UNPACK_EX"                        , 116 , 0 , 0)
def_op(loc, "UNPACK_SEQUENCE"                  , 117 , 0 , -1)
def_op(loc, "YIELD_VALUE"                      , 118 , 1 , 1)
def_op(loc, "RESUME"                           , 149 , 0 , 0)
def_op(loc, "INSTRUMENTED_RESUME"              , 236 , 1 , 1)
def_op(loc, "INSTRUMENTED_END_FOR"             , 237 , 2 , 1)
def_op(loc, "INSTRUMENTED_END_SEND"            , 238 , 1 , 0)
def_op(loc, "INSTRUMENTED_RETURN_VALUE"        , 239 , 1 , 0)
def_op(loc, "INSTRUMENTED_RETURN_CONST"        , 240 , 1 , 1)
def_op(loc, "INSTRUMENTED_YIELD_VALUE"         , 241 , 1 , 1)
def_op(loc, "INSTRUMENTED_LOAD_SUPER_ATTR"     , 242 , 2 , 0)
def_op(loc, "INSTRUMENTED_FOR_ITER"            , 243 , 1 , 1)
def_op(loc, "INSTRUMENTED_CALL"                , 244 , 1 , 1)
def_op(loc, "INSTRUMENTED_CALL_KW"             , 245 , 2 , 2)
def_op(loc, "INSTRUMENTED_CALL_FUNCTION_EX"    , 246 , 1 , 1)
def_op(loc, "INSTRUMENTED_INSTRUCTION"         , 247 , 1 , 1)
def_op(loc, "INSTRUMENTED_JUMP_FORWARD"        , 248 , 1 , 1)
def_op(loc, "INSTRUMENTED_JUMP_BACKWARD"       , 249 , 1 , 1)
def_op(loc, "INSTRUMENTED_POP_JUMP_IF_FALSE"   , 251 , 1 , 1)
def_op(loc, "INSTRUMENTED_POP_JUMP_IF_NONE"    , 252 , 1 , 1)
def_op(loc, "INSTRUMENTED_POP_JUMP_IF_NOT_NONE", 253 , 1 , 1)
def_op(loc, "JUMP"                             , 256 , 0 , 0)
def_op(loc, "JUMP_NO_INTERRUPT"                , 257 , 0 , 0)
def_op(loc, "LOAD_CLOSURE"                     , 258 , 0 , 1)
def_op(loc, "LOAD_METHOD"                      , 259 , 0 , 1)
def_op(loc, "LOAD_SUPER_METHOD"                , 260 , 1 , 0)
def_op(loc, "LOAD_ZERO_SUPER_ATTR"             , 261 , 1 , 0)
def_op(loc, "LOAD_ZERO_SUPER_METHOD"           , 262 , 1 , 0)
def_op(loc, "POP_BLOCK"                        , 263 , 1 , 1)
def_op(loc, "SETUP_CLEANUP"                    , 264 , 0 , 2)
def_op(loc, "SETUP_FINALLY"                    , 265 , 0 , 1)
def_op(loc, "SETUP_WITH"                       , 266 , 0 , 1)
def_op(loc, "STORE_FAST_MAYBE_NULL"            , 267 , 1 , 0)

## These are new since 3.12...
#            OP NAME                              OPCODE POP PUSH
# ---------------------------------------------------------------
def_op(loc, "FORMAT_SIMPLE"         , 14 , 1 , 1)
def_op(loc, "TO_BOOL"               , 40 , 0 , 0)
def_op(loc, "CALL_KW"               , 57 , -2, 1)
def_op(loc, "CONVERT_VALUE"         , 60 , 1 , 1)
def_op(loc, "SET_FUNCTION_ATTRIBUTE", 106, 2 , 1)

# fmt: on

### update opinfo tables
# completely redefined tables
loc["hasarg"] = [
    45,
    46,
    47,
    48,
    49,
    50,
    51,
    52,
    53,
    54,
    55,
    56,
    57,
    58,
    59,
    60,
    61,
    62,
    63,
    64,
    65,
    66,
    67,
    68,
    69,
    70,
    71,
    72,
    73,
    74,
    75,
    76,
    77,
    78,
    79,
    80,
    81,
    82,
    83,
    84,
    85,
    86,
    87,
    88,
    89,
    90,
    91,
    92,
    93,
    94,
    95,
    96,
    97,
    98,
    99,
    100,
    101,
    102,
    103,
    104,
    105,
    106,
    107,
    108,
    109,
    110,
    111,
    112,
    113,
    114,
    115,
    116,
    117,
    118,
    149,
    236,
    240,
    241,
    242,
    243,
    244,
    245,
    248,
    249,
    250,
    251,
    252,
    253,
    256,
    257,
    258,
    259,
    260,
    261,
    262,
    264,
    265,
    266,
    267,
]
loc["hascompare"] = [58]
loc["hasconst"] = [83, 103, 240]
loc["haslocal"] = [65, 85, 86, 87, 88, 110, 111, 112, 258, 267]
loc["hasname"] = [
    63,
    66,
    67,
    74,
    75,
    82,
    90,
    91,
    92,
    93,
    108,
    113,
    114,
    259,
    260,
    261,
    262,
]
loc["hasfree"] = [64, 84, 89, 94, 109]
# add new table "hasjump"
loc.update({"hasjump": [72, 77, 78, 79, 97, 98, 99, 100, 104, 256, 257]})
loc["hasjrel"] = loc["hasjump"]

### update formatting
opcode_arg_fmt = opcode_312.opcode_arg_fmt312.copy()
opcode_extended_fmt = opcode_312.opcode_extended_fmt312.copy()
for fmt_table in (opcode_arg_fmt, opcode_extended_fmt):
    fmt_table.pop("MAKE_FUNCTION")  # MAKE_FUNCTION formatting not in 3.13
opcode_arg_fmt313 = opcode_arg_fmt
opcode_extended_fmt313 = opcode_extended_fmt


# update any calls to findlinestarts to include the version tuple
def findlinestarts_313(code, dup_lines=False):
    lastline = False  # None is a valid line number
    for start, _, line in code.co_lines():
        if line is not lastline:
            lastline = line
            yield start, line


findlinestarts = findlinestarts_313

update_pj3(globals(), loc)
finalize_opcodes(loc)
