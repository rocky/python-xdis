def get_instructions_bytes_graal(code, opc):
    """
    Iterate over the instructions in a bytecode string.

    Generates a sequence of Instruction namedtuples giving the details of each
    opcode.  Additional information about the code's runtime environment
    e.g., variable names, constants, can be specified using optional
    arguments.
    """
    bytecode = code.co_code
    varnames = code.co_varnames
    names = code.co_names
    constants = code.co_consts
    # source_map = ???

    i = 0
    n = len(bytecode)
    oparg = 0
    # This is for 3.8 Graal 23
    lines = []
    while i < n:
        offset = i
        opcode = bytecode[i]
        opname = opc.opname[opcode]
        arg_count = opc.arg_counts[opcode]
        i += 1

        field = ["", ""] + ([None] * 4)
        # field[0] = "%3d:%-3d - %3d:%-3d" % (source_map.startFieldMap[instruction_i], source_map.startColumnMap[instruction_i], source_map.endFieldMap[instruction_i], source_map.endColumnMap[instruction_i])
        field[2] = "%3d" % offset
        field[3] = opname
        following_args = []
        if arg_count == 0:
            field[4] = ""
        else:
            oparg |= bytecode[i]
            i += 1
            offset += 1
            if arg_count > 1:
                following_args = []
                for j in range(arg_count -1):
                    following_args.append(bytecode[i+j])
                    i += 1
                field[4] = "%2d" % oparg

        while True:
            if opcode == opc.opmap["EXTENDED_ARG"]:
                field[4] = ""
                break
            elif opcode == opc.opmap["LOAD_BYTE"]:
                field[4] = "%2d" % oparg
                break
            elif opcode in (opc.opmap["LOAD_CONST"],
                            opc.opmap["LOAD_BIGINT"],
                            opc.opmap["LOAD_STRING"],
                            opc.opmap["LOAD_BYTES"],
                            opc.opmap["LOAD_CONST_COLLECTION"],
                            opc.opmap["MAKE_KEYWORD"]):
                field[5] = constants[oparg]
            elif opcode == opc.opmap["MAKE_FUNCTION"]:
                if following_args:
                    field[4] = "%2d" % following_args[0]
                codeUnit = constants[oparg]
                field[5] = codeUnit.co_name
                break

            elif opcode in (opc.opmap["LOAD_INT"], opc.opmap["LOAD_LONG"]):
                field[5] = Objects.toString(primitiveConstants[oparg])
                break
            elif opcode == opc.opmap["LOAD_DOUBLE"]:
                field[5] = Objects.toString(Double.longBitsToDouble(primitiveConstants[oparg]))
                break
            elif opcode == opc.opmap["LOAD_COMPLEX"]:
                num = constants[oparg]
                if num[0] == 0.0:
                    field[5] = "%g" % num[1]
                else:
                    field[5] = "%g%+gj" % (num[0], num[1])
                    break
            elif opcode in (opc.opmap["LOAD_CLOSURE"], opc.opmap["LOAD_DEREF"], opc.opmap["STORE_DEREF"], opc.opmap["DELETE_DEREF"]):
                if oparg >= len(code.co_cellvars):
                    field[5] = freevars[oparg - cellvars.length].toJavaStringUncached()
                else:
                    field[5] = cellvars[oparg].toJavaStringUncached()
                break
            elif opcode in (opc.opmap["LOAD_FAST"], opc.opmap["STORE_FAST"], opc.opmap["DELETE_FAST"]):
                field[5] = varnames[oparg]
                break

            elif opcode in (opc.opmap["LOAD_NAME"],
                            opc.opmap["LOAD_METHOD"],
                            opc.opmap["STORE_NAME"],
                            opc.opmap["DELETE_NAME"],
                            opc.opmap["IMPORT_NAME"],
                            opc.opmap["IMPORT_FROM"],
                            opc.opmap["LOAD_GLOBAL"],
                            opc.opmap["STORE_GLOBAL"],
                            opc.opmap["DELETE_GLOBAL"],
                            opc.opmap["LOAD_ATTR"],
                            opc.opmap["STORE_ATTR"],
                            opc.opmap["DELETE_ATTR"]):
                field[5] = names[oparg - 1]
                i += 1
                break
            elif opcode == opc.opmap["FORMAT_VALUE"]:
                kind = oparg & FormatOptions.FVC_MASK
                if kind == opc.FormatOptions.FVC_ST:
                    field[5] = "STR"
                    break
                elif kind == opc.FormatOptions.FVC_REP:
                    field[5] = "REPR"
                    break
                elif opcode == opc.FormatOptions.FVC_ASCII:
                    field[5] = "ASCII"
                    break
                elif opcode == opc.FormatOptions.FVC_NONE:
                    field[5] = "NONE"
                    break

                if (oparg & FormatOptions.FVS_MASK) == FormatOptions.FVS_HAVE_SPEC:
                    field[5] += " + SPEC"
                    break

            elif opcode == opc.opmap["CALL_METHOD"]:
                field[4] = "%2d" % oparg
                break

            elif opcode == opc.opmap["UNARY_OP"]:
                field[5] = UnaryOps.values()[oparg].toString()
                break

            elif opcode == opc.opmap["BINARY_OP"]:
                field[5] = BinaryOps.values()[oparg].toString()
                break

            elif opcode in (opc.opmap["COLLECTION_FROM_STACK"],
                            opc.opmap["COLLECTION_ADD_STACK"],
                            opc.opmap["COLLECTION_FROM_COLLECTION"],
                            opc.opmap["COLLECTION_ADD_COLLECTION"],
                            opc.opmap["ADD_TO_COLLECTION"]):
                field[4] = "%2d" % oparg
                field[5] = collectionKindToString(oparg)
                break
            elif opcode == opc.opmap["UNPACK_EX"]:
                field[5] = "%d, %d" % (oparg, Byte.toUnsignedInt(following_args[0]))
                break
            elif opcode == opc.opmap["JUMP_BACKWARD"]:
                # fields.computeIfAbsent(offset - oparg, k -> new String[DISASSEMBLY_NUM_COLUMNS])[1] = ">>"
                field[5] = "to %d" % (offset - oparg)
                break
            elif opcode in (opc.opmap["FOR_ITER"],
                            opc.opmap["JUMP_FORWARD"],
                            opc.opmap["POP_AND_JUMP_IF_FALSE"],
                            opc.opmap["POP_AND_JUMP_IF_TRUE"],
                            opc.opmap["JUMP_IF_FALSE_OR_POP"],
                            opc.opmap["JUMP_IF_TRUE_OR_POP"],
                            opc.opmap["MATCH_EXC_OR_JUMP"],
                            opc.opmap["SEND"],
                            opc.opmap["THROW"]):
                # fields.computeIfAbsent(offset + oparg, k -> new String[DISASSEMBLY_NUM_COLUMNS])[1] = ">>"
                field[5] = String.format("to %d", offset + oparg)
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

        lines.append(field)

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
    for i, line in enumerate(lines):
        print("%2d: %s" % (i, line))
