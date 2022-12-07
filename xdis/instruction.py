#  Copyright (c) 2018-2022 by Rocky Bernstein
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
Extracted from Python 3 dis module but generalized to
allow running on Python 2.
"""

import re
from collections import namedtuple

_Instruction = namedtuple(
    "_Instruction",
    "opname opcode optype inst_size arg argval argrepr has_arg offset starts_line is_jump_target has_extended_arg",
)
#_Instruction.opname.__doc__ = "Human readable name for operation"
#_Instruction.opcode.__doc__ = "Numeric code for operation"
#_Instruction.arg.__doc__ = "Numeric argument to operation (if any), otherwise None"
#_Instruction.argval.__doc__ = "Resolved arg value (if known), otherwise same as arg"
#_Instruction.argrepr.__doc__ = "Human readable description of operation argument"
#_Instruction.has_arg.__doc__ = "True if instruction has an operand, otherwise False"
#_Instruction.offset.__doc__ = "Start index of operation within bytecode sequence"
#_Instruction.starts_line.__doc__ = (
#    "Line started by this opcode (if any), otherwise None"
#)
#_Instruction.is_jump_target.__doc__ = (
#    "True if other code jumps to here, otherwise False"
#)
#_Instruction.has_extended_arg.__doc__ = (
#    "True there were EXTENDED_ARG opcodes before this, otherwise False"
#)

_OPNAME_WIDTH = 20
_OPARG_WIDTH = 6


class Instruction(_Instruction):
    """Details for a bytecode operation

    Defined fields:
      opname - human-readable name for operation
      opcode - numeric code for operation
      optype - opcode classification. One of
         compare, const, free, jabs, jrel, local, name, nargs
      inst_size - number of bytes the instruction occupies
      arg - numeric argument to operation (if any), otherwise None
      argval - resolved arg value (if known), otherwise same as arg
      argrepr - human-readable description of operation argument
      has_arg - True if opcode takes an argument. In that case,
                ``argval`` and ``argepr`` will have that value. False
                if this opcode doesn't take an argument. When False,
                don't look at ``argval`` or ``argrepr``.
      offset - Start index of operation within bytecode sequence.
      starts_line - Line started by this opcode (if any), otherwise None
      is_jump_target - True if other code jumps to here,
                       'loop' if this is a loop beginning, which
                       in Python can be determined jump to an earlier offset.
                       Otherwise, False.
      has_extended_arg - True if the instruction was built from EXTENDED_ARG
                         opcodes.
      fallthrough - True if the instruction can (not must) fall through to the next
                    instruction. Note conditionals are in this category, but
                    returns, raise, and unconditional jumps are not.
    """

    # FIXME: remove has_arg from initialization but keep it as a field.

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
                # Must by Python 3.6 or later
                if self.has_arg:
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
            # The ``argrepr`` value when the instruction was created generally has all the information we require.
            # However, for "asm" format, want additional explicit information linking operands to tables.
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
                    if new_repr:
                        argrepr = new_repr
                pass
            if not argrepr:
                if asm_format != "asm" or self.opname == "MAKE_FUNCTION":
                    fields.append(repr(self.arg))
                pass
            else:
                # Column: Opcode argument details
                fields.append("(%s)" % argrepr)
                pass
            pass
        elif asm_format in ("extended", "extended-bytes"):
            op = self.opcode
            if (
                hasattr(opc, "opcode_extended_fmt")
                and opc.opname[op] in opc.opcode_extended_fmt
            ):
                new_repr = opc.opcode_extended_fmt[opc.opname[op]](
                    opc, list(reversed(instructions))
                )
                if new_repr:
                    fields.append("(%s)" % new_repr)
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
