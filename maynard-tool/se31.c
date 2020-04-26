#define PYTHON_VERSION "3.1"

#include "header.h"
#include "opcode31.h"

/*
 * When computing the stack effect for Python 3.x,
 * open up Python-3.x/Python/compile.c and copy
 * the static function "opcode_stack_effect" below.
 */
/* -----8x-------------8x-------------8x----- */
/* PASTE FUNCTION HERE */
static int
opcode_stack_effect(int opcode, int oparg)
{
    switch (opcode) {
        case POP_TOP:
            return -1;
        case ROT_TWO:
        case ROT_THREE:
            return 0;
        case DUP_TOP:
            return 1;
        case ROT_FOUR:
            return 0;

        case UNARY_POSITIVE:
        case UNARY_NEGATIVE:
        case UNARY_NOT:
        case UNARY_INVERT:
            return 0;

        case SET_ADD:
        case LIST_APPEND:
            return -1;
        case MAP_ADD:
            return -2;

        case BINARY_POWER:
        case BINARY_MULTIPLY:
        case BINARY_MODULO:
        case BINARY_ADD:
        case BINARY_SUBTRACT:
        case BINARY_SUBSCR:
        case BINARY_FLOOR_DIVIDE:
        case BINARY_TRUE_DIVIDE:
            return -1;
        case INPLACE_FLOOR_DIVIDE:
        case INPLACE_TRUE_DIVIDE:
            return -1;

        case INPLACE_ADD:
        case INPLACE_SUBTRACT:
        case INPLACE_MULTIPLY:
        case INPLACE_MODULO:
            return -1;
        case STORE_SUBSCR:
            return -3;
        case STORE_MAP:
            return -2;
        case DELETE_SUBSCR:
            return -2;

        case BINARY_LSHIFT:
        case BINARY_RSHIFT:
        case BINARY_AND:
        case BINARY_XOR:
        case BINARY_OR:
            return -1;
        case INPLACE_POWER:
            return -1;
        case GET_ITER:
            return 0;

        case PRINT_EXPR:
            return -1;
        case LOAD_BUILD_CLASS:
            return 1;
        case INPLACE_LSHIFT:
        case INPLACE_RSHIFT:
        case INPLACE_AND:
        case INPLACE_XOR:
        case INPLACE_OR:
            return -1;
        case BREAK_LOOP:
            return 0;
        case WITH_CLEANUP:
            return -1; /* XXX Sometimes more */
        case STORE_LOCALS:
            return -1;
        case RETURN_VALUE:
            return -1;
        case IMPORT_STAR:
            return -1;
        case YIELD_VALUE:
            return 0;

        case POP_BLOCK:
            return 0;
        case POP_EXCEPT:
            return 0;  /* -3 except if bad bytecode */
        case END_FINALLY:
            return -1; /* or -2 or -3 if exception occurred */

        case STORE_NAME:
            return -1;
        case DELETE_NAME:
            return 0;
        case UNPACK_SEQUENCE:
            return oparg-1;
        case UNPACK_EX:
            return (oparg&0xFF) + (oparg>>8);
        case FOR_ITER:
            return 1;

        case STORE_ATTR:
            return -2;
        case DELETE_ATTR:
            return -1;
        case STORE_GLOBAL:
            return -1;
        case DELETE_GLOBAL:
            return 0;
        case DUP_TOPX:
            return oparg;
        case LOAD_CONST:
            return 1;
        case LOAD_NAME:
            return 1;
        case BUILD_TUPLE:
        case BUILD_LIST:
        case BUILD_SET:
            return 1-oparg;
        case BUILD_MAP:
            return 1;
        case LOAD_ATTR:
            return 0;
        case COMPARE_OP:
            return -1;
        case IMPORT_NAME:
            return 0;
        case IMPORT_FROM:
            return 1;

        case JUMP_FORWARD:
        case JUMP_IF_TRUE_OR_POP:  /* -1 if jump not taken */
        case JUMP_IF_FALSE_OR_POP:  /*  "" */
        case JUMP_ABSOLUTE:
            return 0;

        case POP_JUMP_IF_FALSE:
        case POP_JUMP_IF_TRUE:
            return -1;

        case LOAD_GLOBAL:
            return 1;

        case CONTINUE_LOOP:
            return 0;
        case SETUP_LOOP:
            return 0;
        case SETUP_EXCEPT:
        case SETUP_FINALLY:
            return 6; /* can push 3 values for the new exception
                + 3 others for the previous exception state */

        case LOAD_FAST:
            return 1;
        case STORE_FAST:
            return -1;
        case DELETE_FAST:
            return 0;

        case RAISE_VARARGS:
            return -oparg;
#define NARGS(o) (((o) % 256) + 2*(((o) / 256) % 256))
        case CALL_FUNCTION:
            return -NARGS(oparg);
        case CALL_FUNCTION_VAR:
        case CALL_FUNCTION_KW:
            return -NARGS(oparg)-1;
        case CALL_FUNCTION_VAR_KW:
            return -NARGS(oparg)-2;
        case MAKE_FUNCTION:
            return -NARGS(oparg) - ((oparg >> 16) & 0xffff);
        case MAKE_CLOSURE:
            return -1 - NARGS(oparg) - ((oparg >> 16) & 0xffff);
#undef NARGS
        case BUILD_SLICE:
            if (oparg == 3)
                return -2;
            else
                return -1;

        case LOAD_CLOSURE:
            return 1;
        case LOAD_DEREF:
            return 1;
        case STORE_DEREF:
            return -1;
        default:
            fprintf(stderr, "opcode = %d\n", opcode);
            Py_FatalError("opcode_stack_effect()");

    }
    return 0; /* not reachable */
}
/* -----8x-------------8x-------------8x----- */

#include "main.h"
