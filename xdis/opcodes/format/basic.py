# (C) Copyright 2023, 2025 by Rocky Bernstein
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
Routines for formatting opcodes.
"""

def format_extended_arg(arg):
    return str(arg * (1 << 16))


def format_CALL_FUNCTION_pos_name_encoded(argc):
    """Encoded positional and named args. Used to
    up to about 3.6 where wordcodes are used and
    a different encoding occurs. Pypy36 though
    sticks to this encoded version though."""
    name_default, pos_args = divmod(argc, 256)
    return "%d positional, %d named" % (pos_args, name_default)


def format_IS_OP(arg: int) -> str:
    return "is" if arg == 0 else "is not"


def format_MAKE_FUNCTION_10_27(argc: int) -> str:
    """
    ``argc`` is the operand  of a  "MAKE_FUNCTION" or "MAKE_CLOSURE" instruction.

    This code works for Python versions up to and including 2.7.
    Python docs for MAKE_FUNCTION and MAKE_CLOSURE the was changed in 33, but testing
    shows that the change was really made in Python 3.0 or so.
    """
    return f"{argc} default parameters"


# Up until 3.7
def format_RAISE_VARARGS_older(argc) -> str:
    assert 0 <= argc <= 3
    if argc == 0:
        return "reraise"
    elif argc == 1:
        return "exception"
    elif argc == 2:
        return "exception, parameter"
    elif argc == 3:
        return "exception, parameter, traceback"
    return ""

def format_ROT_FOUR(_: int) -> str:
    return "TOS, TOS1, TOS2, TOS3 = TOS1, TOS2, TOS3, TOS"


def format_ROT_THREE(_: int) -> str:
    return "TOS, TOS1, TOS2 = TOS1, TOS2, TOS"


def format_ROT_TWO(_: int) -> str:
    # We add a space at the end as a sentinal to use in get_instruction_tos_str()
    return "TOS, TOS1 = TOS1, TOS"



opcode_arg_fmt_base = opcode_arg_fmt34 = {
    "CALL_FUNCTION": format_CALL_FUNCTION_pos_name_encoded,
    "CALL_FUNCTION_KW": format_CALL_FUNCTION_pos_name_encoded,
    "CALL_FUNCTION_VAR_KW": format_CALL_FUNCTION_pos_name_encoded,
    "EXTENDED_ARG": format_extended_arg,
    "RAISE_VARARGS": format_RAISE_VARARGS_older,
    "ROT_FOUR": format_ROT_FOUR,
    "ROT_THREE": format_ROT_THREE,
    "ROT_TWO": format_ROT_TWO,
}
