"""

This module is an adaptation of the GraalPython's Java SourceMap helper

The original assumes Truffle's Source/SourceSection APIs.

   * The get_source_section(source, ...) method expects a "source" object that implements:
       - has_characters() -> bool
      - get_line_length(line: int) -> int
       - create_unavailable_section() -> any
       - create_section(start_line, start_column, end_line, end_column) -> any
   * The SourceMap constructor accepts an optional op_length_fn parameter (callable)
     that takes a single byte value (0..255) and returns the length (int) of the
     instruction at that BCI. If omitted, all instructions are assumed to have length 1.

 - Byte encoding/decoding handles Java's signed byte semantics (values -128..127).
 - This is intended to reproduce logic and encoding used in the Java original. It is
   not tied to any Truffle internals and can be adapted to a concrete environment.

See https://github.com/oracle/graalpython/graalpython/com.oracle.graal.python/src/com/oracle/graal/python/compiler/SourceMap.java
"""

# Signed byte constants (as in Java code)
EXTENDED_NUM = -128
NEXT_LINE = -127
NEXT_LINES = -126
MIN_NUM = -125
MULTIPLIER_NEGATIVE = MIN_NUM + 1  # -124
MAX_NUM = 127
MULTIPLIER_POSITIVE = MAX_NUM  # 127


def _to_signed(byte_value: int) -> int:
    """Convert 0..255 byte to signed -128..127 value like Java byte."""
    return byte_value if byte_value < 128 else byte_value - 256


class SourceMap:
    """
    Encapsulates encoding/decoding of source line/column information for GraalPython bytecode.

    Constructor:
      SourceMap(code: bytes, src_table: bytes, start_line: int, start_column: int,
                op_length_fn: Optional[Callable[[int], int]] = None)

    - code: bytes of bytecode (used to determine map size and iterate instruction BCIs)
    - src_table: the encoded source table bytes produced by Builder
    - start_line, start_column: initial line/column used to start decoding
    - op_length_fn: optional callable taking an opcode byte (0..255) and returning
      the instruction length in bytes. If None, instructions are assumed length 1.
    """

    def __init__(
        self,
        code_object,
        opc,
    ):
        # use Python lists (mutable) to store maps; they match length of code

        bytecode = code_object.co_code
        start_column = code_object.startColumn
        start_line = code_object.startLine
        # cells: tuple = code_object.co_cells
        # freevars: tuple = code_object.co_freevars
        arg_counts = opc.arg_counts

        n = len(bytecode)
        self.startLineMap = [0] * n
        self.endLineMap = [0] * n
        self.startColumnMap = [0] * n
        self.endColumnMap = [0] * n
        self.source_table = code_object.srcOffsetTable
        self.source_table_len = len(self.source_table)

        # op_length_fn determines instruction size; default to 1

        self.source_table_pos = 0

        self.next_column = start_column
        self.next_line = start_line
        offset = 0
        # print(f"XXX0 len: {n}") # debug
        while offset < n:

            # code[offset] is an int 0..255 in Python 3 when indexing bytes
            # print(f"offset: {offset}") # debug
            op_byte = bytecode[offset]
            # print(f"{opc.opname[op_byte]}") # debug
            op_len = arg_counts[op_byte] + 1
            # print(f"op_len: {op_len}") # debug

            try:
                start_line, start_column = self._next_line_and_column()
                end_line, end_column = self._next_line_and_column()
            except EOFError:
                # FIXME: We made a mistake somewhere.
                break

            # fill maps for the bytes covered by this opcode
            for i in range(offset, min(offset + op_len, n)):
                self.startLineMap[i] = start_line
                self.startColumnMap[i] = start_column
                self.endLineMap[i] = end_line
                self.endColumnMap[i] = end_column
            offset += op_len

    def _next_line_and_column(self) -> tuple:
        """
        Get the (line, column) pair delta from self.source_table.

        Java code (which reads from a stream):
            stream.mark(1);
            byte value = (byte) stream.read();
            if (value == NEXT_LINE) { pair[0]++; pair[1] = 0; }
            else if (value == NEXT_LINES) { pair[0] += readNum(stream); pair[1] = 0; }
            else { stream.reset(); }
            pair[1] += readNum(stream);
        """
        if self.source_table_pos >= self.source_table_len:
            raise EOFError("Unexpected end of source table while reading line/column")

        old_pos = self.source_table_pos
        b = self.source_table[self.source_table_pos]
        self.source_table_pos += 1
        v = _to_signed(b)
        if v == NEXT_LINE:
            self.next_line += 1
            self.next_column = 0
        elif v == NEXT_LINES:
            self.next_line += self._get_num()
            self.next_column = 0
        else:
            # reset to before the byte we consumed
            # print("Resetting from %d to %d" % (self.source_table_pos, old_pos))
            self.source_table_pos = old_pos
        self.next_column += self._get_num()
        return self.next_line, self.next_column

    def _get_num(self) -> int:
        """
        Decode a signed (possibly extended) number from the stream.

        This Behavior mirrors Java's readNum using EXTENDED_NUM and multipliers,
        but that code reads from a stream insttead of self.source_table.
        """
        extensions = 0
        while True:
            b = self.source_table[self.source_table_pos]
            self.source_table_pos += 1
            val = _to_signed(b)
            # assert val != -1
            if val == EXTENDED_NUM:
                extensions += 1
            elif val < 0:
                # negative single-byte value (signed)
                return extensions * MULTIPLIER_NEGATIVE + val
            else:
                # non-negative single-byte value
                return extensions * MULTIPLIER_POSITIVE + val


def find_linestarts_graal(code_object, opc, dup_lines: bool) -> dict:
    source_map = SourceMap(code_object, opc)
    bytecode = code_object.co_code
    i = 0
    n = len(bytecode)
    last_lineno = -1
    offset2line = {}
    lines_seen = set()
    last_linemap_offset = len(source_map.startLineMap) - 1
    while i < n:
        opcode = bytecode[i]
        offset = i
        i += opc.arg_counts[opcode] + 1
        if offset >= last_linemap_offset:
            break
        line_number = source_map.startLineMap[offset]
        if line_number != last_lineno:
            if not dup_lines:
                if line_number in lines_seen:
                    continue
                else:
                    lines_seen.add(line_number)
            offset2line[offset] = line_number

        last_lineno = line_number

    return offset2line
