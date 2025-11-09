# from xdis.bytecode import get_optype
from xdis.bytecode import Bytecode
from xdis.cross_dis import get_code_object
from xdis.instruction import Instruction


def get_instructions_bytes_graal(
    bytecode, opc, varnames, names, constants, *args, **kwargs
):
    """
    Iterate over the instructions in a bytecode string.

    Generates a sequence of Instruction namedtuples giving the details of each
    opcode.  Additional information about the code's runtime environment
    e.g., variable names, constants, can be specified using optional
    arguments.
    """
    # source_map = ???

    i = 0
    n = len(bytecode)
    oparg = 0
    # This is for 3.8 Graal 23

    extended_arg_count = 0

    while i < n:
        opcode = bytecode[i]
        opname = opc.opname[opcode]
        optype = get_optype_graal(opcode, opc)

        offset = i
        arg_count = opc.arg_counts[opcode]
        i += 1

        arg = None
        argval = None
        argrepr = ""

        following_args = []
        has_arg = arg_count == 0

        if has_arg:
            argrepr = ""
        else:
            oparg |= bytecode[i]
            i += 1
            if arg_count > 1:
                following_args = []
                for j in range(arg_count - 1):
                    following_args.append(bytecode[i + j])
                    i += 1
                argrepr = "%2d" % oparg

        while True:
            if opcode == opc.opmap["EXTENDED_ARG"]:
                argrepr = ""
                break
            elif opcode == opc.opmap["LOAD_BYTE"]:
                argrepr = "%2d" % oparg
                argval = oparg
                break
            elif optype == "const":
                arg = oparg
                argval = constants[oparg]
            elif opcode == opc.opmap["MAKE_FUNCTION"]:
                if following_args:
                    argrepr = "%2d" % following_args[0]
                argval = constants[oparg]
                argrepr = argval.co_name
                break

            elif opcode in (opc.opmap["LOAD_INT"], opc.opmap["LOAD_LONG"]):
                argrepr = Objects.toString(primitiveConstants[oparg])
                break
            elif opcode == opc.opmap["LOAD_DOUBLE"]:
                argrepr = Objects.toString(
                    Double.longBitsToDouble(primitiveConstants[oparg])
                )
                break
            elif opcode == opc.opmap["LOAD_COMPLEX"]:
                argval = constants[oparg]
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
                if oparg >= len(code.co_cellvars):
                    argrepr = code.co_freevars[
                        oparg - code.co_cellvars.length
                    ].toJavaStringUncached()
                else:
                    argrepr = code.co_cellvars[oparg].toJavaStringUncached()
                break
            elif opcode in (
                opc.opmap["LOAD_FAST"],
                opc.opmap["STORE_FAST"],
                opc.opmap["DELETE_FAST"],
            ):
                argval = argrepr = varnames[oparg]
                break

            elif optype == "name":
                argval = oparg
                argrepr = names[oparg - 1]
                i += 1
                break
            elif opcode == opc.opmap["FORMAT_VALUE"]:
                kind = oparg & FormatOptions.FVC_MASK
                if kind == opc.FormatOptions.FVC_ST:
                    argrepr = "STR"
                    break
                elif kind == opc.FormatOptions.FVC_REP:
                    argrepr = "REPR"
                    break
                elif opcode == opc.FormatOptions.FVC_ASCII:
                    argrepr = "ASCII"
                    break
                elif opcode == opc.FormatOptions.FVC_NONE:
                    argepr = "NONE"
                    break

                if (oparg & FormatOptions.FVS_MASK) == FormatOptions.FVS_HAVE_SPEC:
                    argrepr += " + SPEC"
                    break

            elif opcode == opc.opmap["CALL_METHOD"]:
                argrepr = "%2d" % oparg
                break

            elif opcode == opc.opmap["UNARY_OP"]:
                argrepr = UnaryOps.values()[oparg].toString()
                break

            elif opcode == opc.opmap["BINARY_OP"]:
                argrepr = BinaryOps.values()[oparg].toString()
                break

            elif opcode in (
                opc.opmap["COLLECTION_FROM_STACK"],
                opc.opmap["COLLECTION_ADD_STACK"],
                opc.opmap["COLLECTION_FROM_COLLECTION"],
                opc.opmap["COLLECTION_ADD_COLLECTION"],
                opc.opmap["ADD_TO_COLLECTION"],
            ):
                argrepr = collectionKindToString(oparg)
                break
            elif opcode == opc.opmap["UNPACK_EX"]:
                argrepr = "%d, %d" % (oparg, Byte.toUnsignedInt(following_args[0]))
                break
            elif opcode == opc.opmap["JUMP_BACKWARD"]:
                # fields.computeIfAbsent(offset - oparg, k -> new String[DISASSEMBLY_NUM_COLUMNS])[1] = ">>"
                argval = offset - oparg
                argrepr = "to %d" % argval
                break
            elif opcode in (
                opc.opmap["FOR_ITER"],
                opc.opmap["JUMP_FORWARD"],
                opc.opmap["POP_AND_JUMP_IF_FALSE"],
                opc.opmap["POP_AND_JUMP_IF_TRUE"],
                opc.opmap["JUMP_IF_FALSE_OR_POP"],
                opc.opmap["JUMP_IF_TRUE_OR_POP"],
                opc.opmap["MATCH_EXC_OR_JUMP"],
                opc.opmap["SEND"],
                opc.opmap["THROW"],
            ):
                # fields.computeIfAbsent(offset + oparg, k -> new String[DISASSEMBLY_NUM_COLUMNS])[1] = ">>"
                argval = offset + oparg
                argrepr = "to %d" % argval
                break
            else:
                pass
                # if opcode.quickens:
                #     opcode = opcode.quickens
                #     continue

            if opcode == opc.opmap["EXTENDED_ARG"]:
                oparg <<= 8
            else:
                oparg = 0
            break

        inst_size = (i - offset + 1) + (extended_arg_count * 2)
        start_offset = offset if opc.oppop[opcode] == 0 else None

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
            is_jump_target=False,  # is_jump_target,
            starts_line=False,  # starts_line,
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


def get_optype_graal(opcode: int, opc) -> str:
    """Helper to determine what class of instructions ``opcode`` is in.
    Return is a string in:
       compare, const, free, jabs, jrel, local, name, nargs, or ??
    """
    if opcode in opc.COMPARE_OPS:
        return "compare"
    elif opcode in opc.CONST_OPS:
        return "const"
    elif opcode in opc.FREE_OPS:
        return "free"
    elif opcode in opc.JABS_OPS:
        return "jabs"
    elif opcode in opc.JREL_OPS:
        return "jrel"
    # elif opcode in opc.LOCAL_OPS:
    #     return "local"
    elif opcode in opc.NAME_OPS:
        return "name"
    elif opcode in opc.NARGS_OPS:
        return "nargs"
    # This has to come after NARGS_OPS. Some are in both?
    elif opcode in opc.VARGS_OPS:
        return "vargs"
    elif opcode in opc.ENCODED_ARG_OPS:
        return "encoded_arg"

    return "??"


class Bytecode_Graal(Bytecode):
    """Bytecode operations involving a Python code object.

    Instantiate this with a function, method, string of code, or a code object
    (as returned by compile()).

    Iterating over these yields the bytecode operations as Instruction instances.
    """

    def __init__(self, x, opc, first_line=None, current_offset=None) -> None:
        self.codeobj = co = get_code_object(x)
        self._line_offset = 0
        self._cell_names = tuple()
        if first_line is None:
            self.first_line = co.co_firstlineno
        else:
            self.first_line = first_line
            self._line_offset = first_line - co.co_firstlineno
        pass

        # self._linestarts = dict(opc.findlinestarts(co, dup_lines=dup_lines))
        self._linestarts = None
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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._original_object!r})"

    def get_instructions(self, x):
        """Iterator for the opcodes in methods, functions or code

        Generates a series of Instruction named tuples giving the details of
        each operation in the supplied code.

        If *first_line* is not None, it indicates the line number that should
        be reported for the first source line in the disassembled code.
        Otherwise, the source line information (if any) is taken directly from
        the disassembled code object.
        """
        co = get_code_object(x)
        return get_instructions_bytes_graal(
            co.co_code,
            self.opc,
        )
