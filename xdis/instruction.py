#  Copyright (c) 2018-2024 by Rocky Bernstein
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

"""Python instruction class
Extracted from Python 3's ``dis`` module but generalized to
allow running on Python 2.
"""

import re
from typing import Any, NamedTuple, Optional, Union

# _Instruction.tos_str.__doc__ = (
#     "If not None, a string representation of the top of the stack (TOS)"
# )
# # Python expressions can be straight-line, operator like-basic block code that take
# # items off a stack and push a value onto the stack. In this case, in a linear scan
# # we can basically build up an expression tree.
# # Note this has to be the last field. Code to set this assumes this.
# _Instruction.start_offset.__doc__ = (
#     "If not None, the offset of the first instruction feeding into the operation"
# )

_OPNAME_WIDTH = 20


class AssembleFormat(NamedTuple):
    """
    A structure to hold the essential information
    that would be shown in a line of assembly under any
    formatting option, e.g. extended-bytes, or classic.

    Fields in the order they in which they are defined in constructing an object:

      is_jump_target: True if other code jumps to here,
                      'loop' if this is a loop beginning, which
                      in Python can be determined jump to an earlier offset.
                      Otherwise, False.
      is_current_instruction: True if we are stopped at this instruction.
      starts_line: Optional Line started by this opcode (if any). Otherwise None.
      offset:  Start index of operation within bytecode sequence.
      opname:  human-readable name for operation.
      opcode:  numeric code for operation.
      has_arg:   True if opcode takes an argument. In that case,
                 ``argepr`` will have that value. False
                 if this opcode doesn't take an argument. When False,
                 don't look at ``argval`` or ``argrepr``.
      arg:     Optional numeric argument to operation (if any). Otherwise, None.

      argrepr: human-readable description of operation argument.

      tos_str:      If not None, a string representation of the top of the stack (TOS).
                    This is obtained by scanning previous instructions and
                    using information there and in their ``tos_str`` fields.
    """

    # True if other code jumps to here, the string "loop" if this is a loop
    # beginning, which in Python can be determined jump to an earlier
    # offset.  Otherwise, False.
    # Note that this is a generalization of Python's "is_jump_target".
    is_jump_target: Union[bool, str]

    is_current_instruction: bool

    starts_line: Optional[int]

    # Offset of the instruction
    offset: int

    # Human readable name for operation
    opname: str

    # Numeric code for operation
    opcode: int

    # True if instruction has an operand, otherwise False.
    has_arg: bool

    # Numeric operand value if operation has an operand. Otherwise, None.
    # This operand value is an index into one of the lists of a code type.
    # The exact table indexed depends on optype.
    arg: Optional[int]

    # String representation of argval if argval is not None.
    argrepr: Optional[str]

    # If not None, a string representation of the top of the stack (TOS)
    tos_str: Optional[str] = None


class Instruction(NamedTuple):
    """Details for a bytecode operation

    The order of the fields below follows roughly how the values might be displayed
    in an assembly listing.

      is_jump_target: True if other code jumps to here,
                      'loop' if this is a loop beginning, which
                      in Python can be determined jump to an earlier offset.
                      Otherwise, False.

      starts_line: Optional Line started by this opcode (if any). Otherwise None.

      offset:  Start index of operation within bytecode sequence.

      opname:  human-readable name for operation.
      opcode:  numeric code for operation.

      has_arg:   True if opcode takes an argument. In that case,
                 ``argval`` and ``argepr`` will have that value. False
                 if this opcode doesn't take an argument. When False,
                 don't look at ``argval`` or ``argrepr``.

      arg:     Optional numeric argument to operation (if any). Otherwise, None.

      argval:  resolved arg value (if known). Otherwise, the same as ``arg``.
      argrepr: human-readable description of operation argument.

      tos_str:      If not None, a string representation of the top of the stack (TOS).
                    This is obtained by scanning previous instructions and
                    using information there and in their ``tos_str`` fields.

      positions: Optional dis.Positions object holding the start and end locations that
                 are covered by this instruction. This not implemented yet.

      optype:    Opcode classification. One of:
                    "compare", "const", "free", "jabs", "jrel", "local",
                    "name", or "nargs".

      inst_size: number of bytes the instruction occupies

      has_extended_arg: True if the instruction was built from EXTENDED_ARG
                        opcodes.

      fallthrough:  True if the instruction can (not must) fall through to the next
                    instruction. Note conditionals are in this category, but
                    returns, raise, and unconditional jumps are not.

      start_offset: if not None the instruction with the lowest offset that
                    pushes a stack entry that is consume by this opcode
    """

    # Numeric code for operation
    opcode: int

    # Human readable name for operation
    opname: str

    # Numeric operand value if operation has an operand, otherwise None.
    # This operand value is an index into one of the lists of a code type.
    # The exact table indexed depends on optype.
    arg: Optional[int]

    # Resolved operand value (if known). This is obtained indexing the appropriate list
    # indicated by optype using value arg.
    # If for some reason we can't extract a value this way ``argval`` has value as
    # ``arg``.
    argval: Any

    # String representation of argval if argval is not None.
    argrepr: str

    # Offset of the instruction
    offset: int

    starts_line: Optional[int]

    # True if other code jumps to here, the string "loop" if this is a loop
    # beginning, which in Python can be determined jump to an earlier
    # offset.  Otherwise, False.
    # Note that this is a generalization of Python's "is_jump_target".
    is_jump_target: Union[bool, str]

    # dis.Positions object holding the start and end locations that
    # are covered by this instruction.
    # FIXME: Implement. The below is just a placeholder.
    #
    positions: Optional[Any]

    # The following values are our own extended information not found (yet) #
    # in Python's Instruction structure.                                    #

    # First, values which can be computed or derived from the above,
    # along with an opcode structure. These We add these in an
    # instruction to make the instruction self sufficient.

    # opcode classification. One of:
    #   compare, const, free, jabs, jrel, local, name, nargs
    optype: str

    # True if instruction has an operand, otherwise False.
    has_arg: bool

    # The number of bytes this instruction consumes.
    inst_size: int

    # True there were EXTENDED_ARG opcodes before this, otherwise False
    has_extended_arg: Optional[bool] = None

    # True if the instruction can (not must) fall through to the next
    # instruction. Note conditionals are in this category, but
    # returns, raise, and unconditional jumps are not.
    fallthrough: Optional[bool] = None

    # If not None, a string representation of the top of the stack (TOS)
    tos_str: Optional[str] = None

    # Python expressions can be straight-line, operator like-basic block code that take
    # items off a stack and push a value onto the stack. In this case, in a linear scan
    # we can basically build up an expression tree.
    # Note this has to be the last field. Code to set this assumes this.
    start_offset: Optional[int] = None

    def disassemble(
        self,
        opc,
        lineno_width=3,
        mark_as_current=False,
        asm_format="classic",
        instructions=[],
    ):
        """Format instruction details for inclusion in disassembly output

        *lineno_width* sets the width of the line number field (0 omits it)
        *mark_as_current* inserts a '-->' marker arrow as part of the line
        """
        fields = []
        indexed_operand = frozenset(["name", "local", "compare", "free"])

        # Column: Source code line number
        if lineno_width:
            if self.starts_line is not None:
                if asm_format == "asm":
                    lineno_fmt = "%%%dd:\n" % lineno_width
                    fields.append(lineno_fmt % self.starts_line)
                    fields.append(" " * lineno_width)
                    if self.is_jump_target:
                        fields.append(" " * (lineno_width - 1))
                else:
                    lineno_fmt = "%%%dd:" % lineno_width
                    fields.append(lineno_fmt % self.starts_line)
            else:
                fields.append(" " * (lineno_width + 1))

        # Column: Current instruction indicator
        if mark_as_current and asm_format != "asm":
            fields.append("-->")
        else:
            fields.append("   ")

        # Column: Jump target marker
        if self.is_jump_target:
            if asm_format != "asm":
                fields.append(">>")
            else:
                fields = ["L%d:\n" % self.offset] + fields
                if not self.starts_line:
                    fields.append(" ")
        else:
            fields.append("  ")

        # Column: Instruction offset from start of code sequence
        if asm_format != "asm":
            fields.append(repr(self.offset).rjust(4))

        # Column: Instruction bytes
        if asm_format in ("extended-bytes", "bytes"):
            hex_bytecode = "|%02x" % self.opcode
            if self.inst_size == 1:
                # Not 3.6 or later
                hex_bytecode += " " * (2 * 3)
            if self.inst_size == 2:
                # Must be Python 3.6 or later
                if self.has_arg and self.arg is not None:
                    hex_bytecode += " %02x" % (self.arg % 256)
                else:
                    hex_bytecode += " 00"
            elif self.inst_size == 3:
                # Not 3.6 or later
                hex_bytecode += " %02x %02x" % divmod(self.arg, 256)

            fields.append(hex_bytecode + "|")

        # Column: Opcode name
        fields.append(self.opname.ljust(_OPNAME_WIDTH))

        # Column: Opcode argument
        if self.arg is not None:
            argrepr = self.argrepr
            # The ``argrepr`` value when the instruction was created
            # generally has all the information we require.  However,
            # for "asm" format, want additional explicit information
            # linking operands to tables.
            if asm_format == "asm":
                if self.optype in ("jabs", "jrel"):
                    assert self.argrepr.startswith("to ")
                    jump_target = self.argrepr[len("to ") :]
                    fields.append("L" + jump_target)
                elif self.optype in indexed_operand:
                    fields.append(repr(self.arg))
                    fields.append("(%s)" % argrepr)
                    argrepr = None
                elif self.optype == "const" and not re.search(r"\s", argrepr):
                    fields.append(repr(self.arg))
                    fields.append("(%s)" % argrepr)
                    argrepr = None
                elif self.optype == "const" and not re.search(r"\s", argrepr):
                    fields.append(repr(self.arg))
                    fields.append("(%s)" % argrepr)
                    argrepr = None
                else:
                    fields.append(repr(self.arg))
            elif asm_format in ("extended", "extended-bytes"):
                op = self.opcode
                if (
                    hasattr(opc, "opcode_extended_fmt")
                    and opc.opname[op] in opc.opcode_extended_fmt
                ):
                    new_repr = opc.opcode_extended_fmt[opc.opname[op]](
                        opc, list(reversed(instructions))
                    )
                    start_offset = None
                    if isinstance(new_repr, tuple) and len(new_repr) == 2:
                        new_repr, start_offset = new_repr
                    if new_repr:
                        # Add tos_str info to tos_str field of instruction.
                        # This the last field in instruction.
                        new_instruction = list(instructions[-1])
                        new_instruction[-2] = new_repr
                        new_instruction[-1] = start_offset
                        del instructions[-1]
                        instructions.append(Instruction(*new_instruction))
                        argrepr = new_repr
                        start_offset = start_offset
                pass
            if not argrepr:
                if asm_format != "asm" or self.opname == "MAKE_FUNCTION":
                    fields.append(repr(self.arg))
                pass
            else:
                # Column: Opcode argument details
                if len(instructions) > 0:
                    argval = instructions[-1].argval
                    if instructions[-1].tos_str is None or (
                        self.argrepr is not None
                        and self.argrepr == instructions[-1].tos_str
                    ):
                        fields.append(f"({self.argrepr})")
                    else:
                        prefix = "" if self.argrepr is None else f"({self.argrepr}) ; "
                        if self.opcode in opc.operator_set:
                            prefix += "TOS = "
                        fields.append(f"{prefix}{instructions[-1].tos_str}")
                    pass
                pass
            pass
        elif asm_format in ("extended", "extended-bytes"):
            op = self.opcode
            if (
                hasattr(opc, "opcode_extended_fmt")
                and opc.opname[op] in opc.opcode_extended_fmt
            ):
                new_repr, start_offset = opc.opcode_extended_fmt[opc.opname[op]](
                    opc, list(reversed(instructions))
                )
                if new_repr:
                    new_instruction = list(instructions[-1])
                    new_instruction[-2] = new_repr
                    new_instruction[-1] = start_offset
                    del instructions[-1]
                    instructions.append(Instruction(*new_instruction))
                    argval = instructions[-1].argval
                    prefix = "" if argval is None else f"({argval}) | "
                    if self.opcode in opc.operator_set:
                        prefix += "TOS = "
                    fields.append(f"{prefix}{new_repr}")
            pass

        return " ".join(fields).rstrip()

    def format_to_assembly_line(
        self,
        current_instruction_line,
    ) -> AssembleFormat:
        """
        Format instruction into a structure that can be easily
        turned a structure contains the essential information
        that would be shown as a line in an assembly listing
        """
        return AssembleFormat(
            self.is_jump_target,
            current_instruction_line == self.starts_line,
            self.starts_line,
            self.offset,
            self.opname,
            self.opcode,
            self.has_arg,
            self.arg,
            self.argrepr,
            self.tos_str,
        )

    def is_jump(self):
        """
        Return True if instruction is some sort of jump.
        """
        return self.optype in ("jabs", "jrel")

    def jumps_forward(self):
        """
        Return True if instruction is jump backwards
        """
        return self.is_jump() and self.offset < self.argval


# if __name__ == '__main__':
#     pass
