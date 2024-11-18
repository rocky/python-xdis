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
from collections import namedtuple

_Instruction = namedtuple(
    "_Instruction",
    (
        "is_jump_target starts_line offset opname opcode has_arg arg argval argrepr "
        # The below do not have Python 3.6+ Instruction equvalents.
        "tos_str positions optype inst_size has_extended_arg fallthrough start_offset"
    ),
)
_OPNAME_WIDTH = 20


class Instruction(_Instruction):
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

      Note: the following fields have to appear in the order below and be at the end.
      disassembly may replace (delete and insert) an instruction, and it assumes
      the ending fields are as follows:

      tos_str:      If not None, a string representation of the top of the stack (TOS).
                    This is obtained by scanning previous instructions and
                    using information there and in their ``tos_str`` fields.

      start_offset: if not None the instruction with the lowest offset that
                    pushes a stack entry that is consume by this opcode
    """

    def disassemble(
        self,
        opc,
        line_starts=None,
        lineno_width=3,
        mark_as_current=False,
        asm_format="classic",
        instructions=[],
    ):
        """
        Format instruction details for inclusion in disassembly output.

        ``line_starts`` when it exists is a dictionary mapping a bytecode offsets to
        line numbers.

        ``lineno_width`` sets the width of the line number field (0 omits it)

        ``mark_as_current`` inserts a '-->' marker arrow as part of the line.
        """
        fields = []
        indexed_operand = frozenset(["name", "local", "compare", "free"])
        opcode = self.opcode

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
            hex_bytecode = "|%02x" % opcode
            if self.inst_size == 1:
                # Not 3.6 or later
                hex_bytecode += " " * (2 * 3)
            if self.inst_size == 2:
                # Must be Python 3.6 or later
                if self.has_arg and self.arg is not None:
                    hex_bytecode += " %02x" % (self.arg % 256)
                else:
                    hex_bytecode += " 00"
            elif self.inst_size == 3 and self.arg is not None:
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
                if self.is_jump() and self.argrepr is not None:
                    assert self.argrepr.startswith("to ")
                    jump_target = self.argrepr[len("to ") :]
                    fields.append("L" + jump_target)
                elif self.optype in indexed_operand:
                    fields.append(repr(self.arg))
                    fields.append("(%s)" % argrepr)
                    argrepr = None
                elif (
                    self.optype == "const"
                    and argrepr is not None
                    and not re.search(r"\s", argrepr)
                ):
                    fields.append(repr(self.arg))
                    fields.append("(%s)" % argrepr)
                    argrepr = None
                else:
                    fields.append(repr(self.arg))
            elif asm_format in ("extended", "extended-bytes"):
                if (
                    self.is_jump()
                    and line_starts is not None
                    and line_starts.get(self.argval) is not None
                ):
                    new_instruction = list(self)
                    new_instruction[-2] = "To line %s" % line_starts[self.argval]
                    # Here and below we use self.__class__ instead of Instruction
                    # so that other kinds of compatible namedtuple Instructions
                    # can be used. In particular, the control-flow project
                    # defines such an ExtendedInstruction namedtuple
                    self = self.__class__(*new_instruction)
                    del instructions[-1]
                    instructions.append(self)
                elif (
                    hasattr(opc, "opcode_extended_fmt")
                    and self.opname in opc.opcode_extended_fmt
                ):
                    new_repr = opc.opcode_extended_fmt.get(self.opname, lambda opc, instr: None)(
                        opc, list(reversed(instructions))
                    )
                    start_offset = None
                    if isinstance(new_repr, tuple) and len(new_repr) == 2:
                        new_repr, start_offset = new_repr
                    if new_repr:
                        # Add tos_str info to tos_str field of instruction.
                        # This the last field in instruction.
                        new_instruction = list(self)
                        new_instruction[-1] = start_offset
                        new_instruction[9] = new_repr
                        del instructions[-1]
                        # See comment above abut the use of self.__class__
                        self = self.__class__(*new_instruction)
                        instructions.append(self)
                        argrepr = new_repr
                elif opcode in opc.nullaryloadop:
                    new_instruction = list(self)
                    new_instruction[9] = self.argrepr
                    start_offset = new_instruction[-1] = self.offset
                    del instructions[-1]
                    # See comment above abut the use of self.__class__
                    self = self.__class__(*new_instruction)
                    instructions.append(self)
                pass
            if not argrepr:
                if asm_format != "asm" or self.opname == "MAKE_FUNCTION":
                    fields.append(repr(self.arg))
                pass
            else:
                # Column: Opcode argument details
                if len(instructions) > 0:
                    argval = self.argval
                    if self.tos_str is None:
                        fields.append("(%s)" % argrepr)
                    else:
                        if self.optype in ("vargs", "encoded_arg"):
                            prefix = "%s ; " % self.argval
                        elif self.argrepr is None:
                            prefix = ""
                        else:
                            prefix = "(%s) ; " % self.argrepr
                        if self.opcode in opc.operator_set | opc.callop:
                            prefix += "TOS = "
                        fields.append("%s%s" % (prefix, self.tos_str))
                    pass
                elif self.argrepr is not None:
                    fields.append(self.argrepr)
                pass
            pass
        elif asm_format in ("extended", "extended-bytes"):
            if (
                hasattr(opc, "opcode_extended_fmt")
                and self.opname in opc.opcode_extended_fmt
            ):
                new_repr, start_offset = opc.opcode_extended_fmt.get(self.opname, (None, 0))(
                    opc, list(reversed(instructions))
                )
                if new_repr:
                    new_instruction = list(self)
                    new_instruction[9] = new_repr
                    new_instruction[-1] = start_offset
                    del instructions[-1]
                    # See comment above abut the use of self.__class__
                    instructions.append(self.__class__(*new_instruction))
                    argval = self.argval
                    prefix = "" if argval is None else "(%s) | " % argval
                    if self.opcode in opc.operator_set:
                        prefix += "TOS = "
                    fields.append("%s%s" % (prefix, new_repr))

                pass
            elif (
                hasattr(opc, "opcode_arg_fmt")
                and self.opname in opc.opcode_arg_fmt
            ) and self.argrepr is not None:
                fields.append(self.argrepr)
                pass
            pass

        return " ".join(fields).rstrip()

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
