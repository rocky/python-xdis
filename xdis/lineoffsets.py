"""
For a given source or bytecode file or code object, retrieve
  * linenumbers,
  * bytecode offsets, and
  * nested functions (code objects)

This is useful for example in debuggers that want to set breakpoints only
at valid locations.
"""

from collections import namedtuple

from xdis.bytecode import get_instructions_bytes
from xdis.codetype.base import iscode
from xdis.load import check_object_path, load_module
from xdis.op_imports import get_opcode_module

# Information about a single line in a particular piece of code
#  Note that a code can have several lines with the same value but
# different code.

# For example:
#     x = 1; y = 2

# will have two lines with the same line number each of the two statements.
# We will have a LineInCode object for each
LineOffsets = namedtuple("LineOffsets", ["line_number", "offsets", "code"])
LineOffsetsCompact = namedtuple("LineOffsetsCompact", ["name", "offsets"])


class LineOffsetInfo(object):
    def __init__(self, opc, code, include_children=False):
        if not iscode(code):
            raise TypeError(
                "code parameter %s needs to be a code type; is %s" % (code, type(code))
            )

        self.code = code
        self.name = code.co_name
        self.opc = opc
        self.children = {}
        self.lines = []
        self.offsets = []
        self.linestarts = dict(opc.findlinestarts(code, dup_lines=True))
        self.instructions = []
        self.include_children = include_children
        self._populate_lines()
        return

    def _populate_lines(self):
        code = self.code
        code_map = {code.co_name: code}
        last_line_info = None
        for instr in get_instructions_bytes(
            bytecode=code.co_code,
            opc=self.opc,
            varnames=code.co_varnames,
            names=code.co_names,
            constants=code.co_consts,
            cells=code.co_cellvars + code.co_freevars,
            linestarts=self.linestarts,
        ):
            offset = instr.offset
            self.offsets.append(offset)
            self.instructions.append(instr)
            if instr.starts_line:
                if last_line_info:
                    self.lines.append(last_line_info)
                    pass
                last_line_info = LineOffsets(instr.starts_line, [offset], code)
            elif last_line_info is not None:
                last_line_info.offsets.append(offset)
                pass
            pass
        self.lines.append(last_line_info)
        if self.include_children:
            for c in code.co_consts:
                if iscode(c):
                    code_map[c.co_name] = c
                    code_info = LineOffsetInfo(self.opc, c, True)
                    code_map.update(code_info.code_map)
                    self.children[code_info.name] = code_info
                    self.lines += code_info.lines
                    pass
                pass
            pass
        self.code_map = code_map

    def __str__(self):
        return str(self.line_numbers())

    def line_numbers(self, include_dups=True, include_offsets=False):
        """Return all of the valid lines for a given piece of code"""
        if include_offsets:
            lines = {}
            for li in self.lines:
                number = li.line_number
                lines[number] = lines.get(number, [])
                lines[number].append(LineOffsetsCompact(li.code.co_name, li.offsets))
                pass
            pass
        else:
            lines = list(self.linestarts.values())
        if not include_dups:
            return sorted(list(set(lines)))
        if isinstance(lines, list):
            return sorted(lines)
        return lines

    pass


def lineoffsets_in_file(filename, toplevel_only=False):
    obj_path = check_object_path(filename)
    version, timestamp, magic_int, code, pypy, source_size, sip_hash = load_module(
        obj_path
    )
    if pypy:
        variant = "pypy"
    else:
        variant = None
    opc = get_opcode_module(version, variant)
    return LineOffsetInfo(opc, code, not toplevel_only)
    pass


def lineoffsets_in_module(module, toplevel_only=False):
    return lineoffsets_in_file(module.__file__, toplevel_only)


if __name__ == "__main__":

    def multi_line():
        # We have two statements on the same line
        x = 1
        y = 2
        return x, y

    def foo():
        def bar():
            return 5

        return bar()

    def print_code_info(code_info):
        children = code_info.children.keys()
        if len(children):
            print("%s has %d children" % (code_info.name, len(children)))
            for child in code_info.children.keys():
                print("\t%s" % child)
                pass
            print("\n")
        else:
            print("%s has no children" % (code_info.name))

        print(
            "\tlines with children and dups:\n\t%s"
            % code_info.line_numbers(include_dups=True)
        )
        print(
            "\tlines without children and without dups:\n\t%s"
            % code_info.line_numbers(include_dups=False)
        )
        print("Offsets in %s" % code_info.name, code_info.offsets)
        lines = code_info.line_numbers(include_offsets=True)
        for line_num, li in lines.items():
            print(
                "\tline: %4d: %s" % (line_num, ", ".join([str(i.offsets) for i in li]))
            )
        print("=" * 30)
        for mod, code in code_info.code_map.items():
            print(mod, ":", code)
        print("=" * 30)
        for li in code_info.lines:
            print(li)
            pass
        return

    opc = get_opcode_module()
    print_code_info(lineoffsets_in_file(__file__))
    # print_code_info(LineOffsetInfo(opc, multi_line.__code__, include_children=True))
