#define PYTHON_VERSION "2.5"

#include "header.h"
#include "opcode25.h"

/*
 * When computing the stack effect for Python,
 * open up Python-x.x/Python/compile.c and copy
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
		case UNARY_CONVERT:
		case UNARY_INVERT:
			return 0;

		case LIST_APPEND:
			return -2;

		case BINARY_POWER:
		case BINARY_MULTIPLY:
		case BINARY_DIVIDE:
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

		case SLICE+0:
			return 1;
		case SLICE+1:
			return 0;
		case SLICE+2:
			return 0;
		case SLICE+3:
			return -1;

		case STORE_SLICE+0:
			return -2;
		case STORE_SLICE+1:
			return -3;
		case STORE_SLICE+2:
			return -3;
		case STORE_SLICE+3:
			return -4;

		case DELETE_SLICE+0:
			return -1;
		case DELETE_SLICE+1:
			return -2;
		case DELETE_SLICE+2:
			return -2;
		case DELETE_SLICE+3:
			return -3;

		case INPLACE_ADD:
		case INPLACE_SUBTRACT:
		case INPLACE_MULTIPLY:
		case INPLACE_DIVIDE:
		case INPLACE_MODULO:
			return -1;
		case STORE_SUBSCR:
			return -3;
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
		case PRINT_ITEM:
			return -1;
		case PRINT_NEWLINE:
			return 0;
		case PRINT_ITEM_TO:
			return -2;
		case PRINT_NEWLINE_TO:
			return -1;
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
		case LOAD_LOCALS:
			return 1;
		case RETURN_VALUE:
			return -1;
		case IMPORT_STAR:
			return -1;
		case EXEC_STMT:
			return -3;
		case YIELD_VALUE:
			return 0;

		case POP_BLOCK:
			return 0;
		case END_FINALLY:
			return -1; /* or -2 or -3 if exception occurred */
		case BUILD_CLASS:
			return -2;

		case STORE_NAME:
			return -1;
		case DELETE_NAME:
			return 0;
		case UNPACK_SEQUENCE:
			return oparg-1;
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
		case JUMP_IF_FALSE:
		case JUMP_IF_TRUE:
		case JUMP_ABSOLUTE:
			return 0;

		case LOAD_GLOBAL:
			return 1;

		case CONTINUE_LOOP:
			return 0;
		case SETUP_LOOP:
			return 0;
		case SETUP_EXCEPT:
		case SETUP_FINALLY:
			return 3; /* actually pushed by an exception */

		case LOAD_FAST:
			return 1;
		case STORE_FAST:
			return -1;
		case DELETE_FAST:
			return 0;

		case RAISE_VARARGS:
			return -oparg;
#define NARGS(o) (((o) % 256) + 2*((o) / 256))
		case CALL_FUNCTION:
			return -NARGS(oparg);
		case CALL_FUNCTION_VAR:
		case CALL_FUNCTION_KW:
			return -NARGS(oparg)-1;
		case CALL_FUNCTION_VAR_KW:
			return -NARGS(oparg)-2;
#undef NARGS
		case MAKE_FUNCTION:
			return -oparg;
		case BUILD_SLICE:
			if (oparg == 3)
				return -2;
			else
				return -1;

		case MAKE_CLOSURE:
			return -oparg;
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
