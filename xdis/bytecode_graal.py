# from xdis.bytecode import get_optype

from xdis.bytecode import Bytecode
from xdis.cross_dis import get_code_object
from xdis.instruction import Instruction
from xdis.lineoffsets_graal import find_linestarts_graal
from xdis.opcodes.base_graal import (
    BINARY_OPS,
    COLLECTION_KIND,
    UNARY_OPS,
    get_optype_graal,
)


def get_instructions_bytes_graal(
    code_object,
    opc,
):
    """
    Iterate over the instructions in a bytecode string.

    Generates a sequence of Instruction namedtuples giving the details of each
    opcode.  Additional information about the code's runtime environment
    e.g., variable names, constants, can be specified using optional
    arguments.
    """
    bytecode = code_object.co_code
    constants = code_object.co_consts
    names = code_object.co_names
    varnames = code_object.co_varnames
    cells = code_object.co_cellvars
    freevars = code_object.co_freevars

    i = 0
    n = len(bytecode)

    labels = opc.findlabels(bytecode, opc)
    linestarts = find_linestarts_graal(code_object, opc, dup_lines=True)

    extended_arg_count = 0
    while i < n:
        opcode = ord(bytecode[i])
        opname = opc.opname[opcode]
        optype = get_optype_graal(opcode, opc)
        offset = i
        starts_line = linestarts.get(offset, None)

        arg_count = opc.arg_counts[opcode]
        is_jump_target = i in labels

        # print(
        #     f"offset: {offset} {hex(opcode)} {opname} arg_count: {arg_count}, optype: {optype}"
        # )

        i += 1

        arg = -1
        argval = None
        argrepr = ""

        following_args = []
        has_arg = arg_count == 0

        if has_arg:
            argrepr = ""
        else:
            arg = ord(bytecode[i])
            i += 1
            if arg_count > 1:
                following_args = []
                for j in range(arg_count - 1):
                    following_args.append(bytecode[i + j])
                    i += 1
                argrepr = str(arg)

        while True:
            if opcode == opc.opmap["EXTENDED_ARG"]:
                argrepr = ""
                break
            elif opcode in (opc.opmap["LOAD_BYTE_O"], opc.opmap["LOAD_BYTE_I"]):
                argrepr = str(arg)
                argval = arg
                break
            elif optype == "const":
                arg = arg
                argval = constants[arg]
                argrepr = str(constants[arg])
            elif opcode == opc.opmap["MAKE_FUNCTION"]:
                if following_args:
                    argrepr = str(following_args[0])
                argval = constants[arg]
                argrepr = argval.co_name
                break

            elif opcode in (opc.opmap["LOAD_INT"], opc.opmap["LOAD_LONG"]):
                argrepr = Objects.toString(primitiveConstants[arg])
                break
            elif opcode == opc.opmap["LOAD_DOUBLE"]:
                argrepr = Objects.toString(
                    Double.longBitsToDouble(primitiveConstants[arg])
                )
                break
            elif opcode == opc.opmap["LOAD_COMPLEX"]:
                argval = constants[arg]
                if num[0] == 0.0:
                    argrepr = "%g" % argval[1]
                else:
                    argrepr = "%g%+gj" % (argval[0], argval[1])
                    break
            elif opcode in (
                opc.opmap["LOAD_CLOSURE"],
                opc.opmap["LOAD_DEREF"],
                opc.opmap["STORE_DEREF"],
                opc.opmap["DELETE_DEREF"],
            ):
                if arg >= len(cells):
                    argrepr = freevars[arg - len(cells)]
                else:
                    argrepr = cells[arg]
                break
            elif opcode in (
                opc.opmap["LOAD_FAST"],
                opc.opmap["STORE_FAST"],
                opc.opmap["DELETE_FAST"],
            ):
                argval = argrepr = varnames[arg]
                break

            elif optype == "name":
                argval = arg
                argrepr = names[arg]
                break
            elif opcode == opc.opmap["FORMAT_VALUE"]:
                argval = arg
                kind = arg & 0x3
                if kind ==0x1:
                    argrepr = "STR"
                    break
                elif kind == 0x2:
                    argrepr = "REPR"
                    break
                elif kind == 0x3:
                    argrepr = "ASCII"
                    break
                elif kind == 0:
                    argrepr = "NONE"
                    break

                if (arg & 0x4) == 0x4:
                    argrepr += " + SPEC"
                    break

            elif opcode == opc.opmap["CALL_METHOD"]:
                argrepr = str(arg)
                break

            elif opcode == "unary":
                argval = arg
                argrepr = UNARY_OPS.get(arg, "??")
                break

            elif optype == "binary":
                argval = arg
                argrepr = BINARY_OPS.get(arg, "??")
                break

            elif optype == "collection":
                argval = arg
                argrepr = COLLECTION_KIND.get(arg, "??")
                break
            elif opcode == opc.opmap["UNPACK_EX"]:
                argrepr = "%d, %d" % (arg, Byte.toUnsignedInt(following_args[0]))
                break
            elif optype == "jrel":
                # fields.computeIfAbsent(offset + arg, k -> new String[DISASSEMBLY_NUM_COLUMNS])[1] = ">>"
                arg = arg
                if opcode == opc.opmap["JUMP_BACKWARD"]:
                    argval = offset - arg
                else:
                    argval = offset + arg
                argrepr = "to %d" % argval
                break
            else:
                pass
                # if opcode.quickens:
                #     opcode = opcode.quickens
                #     continue

            if opcode == opc.opmap["EXTENDED_ARG"]:
                arg <<= 8
            else:
                arg = 0
            break

        inst_size = (arg_count + 1) + (extended_arg_count * 2)
        if opc.oppop[opcode] == 0:
            start_offset = offset
        else:
            start_offset = None

        # for (int i = 0 i < exceptionHandlerRanges.length; i += 4) {
        #     int start = exceptionHandlerRanges[i];
        #     int stop = exceptionHandlerRanges[i + 1];
        #     int handler = exceptionHandlerRanges[i + 2];
        #     int stackAtHandler = exceptionHandlerRanges[i + 3];
        #     String[] field = fields.get(handler);
        #     assert field != null;
        #     String handlerStr = String.format("exc handler %d - %d; stack: %d", start, stop, stackAtHandler);
        #     if (field[6] == null) {
        #         field[6] = handlerStr;
        #     } else {
        #         field[6] += " | " + handlerStr;
        #     }
        # }

        # for (i = 0; i < bytecode.length; i++) {
        #     String[] field = fields.get(i);
        #     if (field != null) {
        #         field[5] = field[5] == null ? "" : String.format("(%s)", field[5]);
        #         field[6] = field[6] == null ? "" : String.format("(%s)", field[6]);
        #         field[7] = "";
        #         if (outputCanQuicken != null && (outputCanQuicken[i] != 0 || generalizeInputsMap[i] != null)) {
        #             StringBuilder quickenSb = new StringBuilder();
        #             if (outputCanQuicken[i] != 0) {
        #                 quickenSb.append("can quicken");
        #             }
        #             if (generalizeInputsMap[i] != null) {
        #                 if (quickenSb.length() > 0) {
        #                     quickenSb.append(", ");
        #                 }
        #                 quickenSb.append("generalizes: ");
        #                 for (int j = 0; i < generalizeInputsMap[i].length; i++) {
        #                     if (j > 0) {
        #                         quickenSb.append(", ");
        #                     }
        #                     quickenSb.append(generalizeInputsMap[i][j]);
        #                 }
        #             }
        #             field[7] = quickenSb.toString();
        #         }
        #         formatted = "%-8s %2s %4s %-32s %-3s   %-32s %s %s" % field;
        #         sb.append(formatted.strip());
        #         sb.append('\n');
        #     }
        # }

        yield Instruction(
            is_jump_target=is_jump_target,
            starts_line= starts_line,
            offset=offset,
            opname=opname,
            opcode=opcode,
            has_arg=has_arg,
            arg=arg,
            argval=argval,
            argrepr=argrepr,
            tos_str=None,
            positions=None,
            optype=optype,
            inst_size=inst_size,
            has_extended_arg=extended_arg_count != 0,
            fallthrough=None,
            start_offset=start_offset,
        )


class Bytecode_Graal(Bytecode):
    """Bytecode operations involving a Python code object.

    Instantiate this with a function, method, string of code, or a code object
    (as returned by compile()).

    Iterating over these yields the bytecode operations as Instruction instances.
    """

    def __init__(self, x, opc, first_line=None, current_offset=None):
        self.codeobj = co = get_code_object(x)
        self._line_offset = 0
        self._cell_names = tuple()
        if first_line is None:
            self.first_line = co.co_firstlineno
        else:
            self.first_line = first_line
            self._line_offset = first_line - co.co_firstlineno
        pass

        self._linestarts = find_linestarts_graal(co, opc, dup_lines=True)
        self._original_object = x
        self.opc = opc
        self.opnames = opc.opname
        self.current_offset = current_offset

        if opc.version_tuple >= (3, 11) and hasattr(co, "co_exceptiontable"):
            self.exception_entries = None
            # self.exception_entries = parse_exception_table(co.co_exceptiontable)
        else:
            self.exception_entries = None

    def __iter__(self):
        co = self.codeobj
        return get_instructions_bytes_graal(
            co.co_code,
            self.opc,
        )

    def __repr__(self):
        return "%s({%r)" % (self.__class__.__name__, self._original_object)

    def get_instructions(self, x):
        """Iterator for the opcodes in methods, functions or code

        Generates a series of Instruction named tuples giving the details of
        each operation in the supplied code.

        If *first_line* is not None, it indicates the line number that should
        be reported for the first source line in the disassembled code.
        Otherwise, the source line information (if any) is taken directly from
        the disassembled code object.
        """
        code_object = get_code_object(x)
        return get_instructions_bytes_graal(code_object, self.opc)
