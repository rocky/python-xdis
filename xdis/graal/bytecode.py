from xdis.instruction import Instruction


def get_source_map():
    return


def from_op_code(bytecode, bci):
    return Instruction()


def compute_if_absent(bci):
    return []


def get_instructions_bytes(bytecode):
    """Iterate over the instructions in a bytecode string.

    Generates a sequence of Instruction namedtuples giving the details of each
    opcode.  Additional information about the code's runtime environment
    (e.g. variable names, constants) can be specified using optional
    arguments.

    """

    # StringBuilder sb = new StringBuilder();

    # HashMap<Integer, String[]> lines = new HashMap<>();

    # sb.append("Disassembly of ").append(qualname).append(":\n");

    # List<String> flagNames = new ArrayList<>();
    #     if (isGenerator()) {
    #         flagNames.add("CO_GENERATOR");
    #     }
    # if (isCoroutine()) {
    #     flagNames.add("CO_COROUTINE");
    # }
    # if (isAsyncGenerator()) {
    #     flagNames.add("CO_ASYNC_GENERATOR");
    # }
    # if (!flagNames.isEmpty()) {
    #     sb.append("Flags: ").append(String.join(" | ", flagNames)).append("\n");
    # }

    bci = 0
    oparg = 0
    map = get_source_map()
    while bci < len(bytecode):
        opcode = from_op_code(bytecode[bci])
        bci += 1

        pass

    return
