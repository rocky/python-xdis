/* main()  portion of the se programs */
int main(int c, char *v[])
{
    int i;
    printf("# Python %s Stack effects\n\n", PYTHON_VERSION);
    printf("[\n");
    for (i = 0; i < 256; i++) {
	int effect;
	int j;
	fatal_error = false;
	effect = opcode_stack_effect(i, 0);
	if (fatal_error == true) {
	    printf("  %d, # %d\n", NOTFIXED, i);
	    continue;
	}
	if (HAS_ARG(i)) {
	    int opargs_to_try[] = { -1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 256, 1000, 0xffff, 0};
	    for (j = 0; opargs_to_try[j]; j++) {
		int with_oparg = opcode_stack_effect(i, opargs_to_try[j]);
		if (effect != with_oparg) {
		    effect = NOTFIXED;
		    break;
		}
	    }
	} else {
	    effect = opcode_stack_effect(i, 0);
	}
	if (effect != NOTFIXED)
	    printf("  %4d, # %d,\n", effect, i);
	else
	    printf("  %d, # %d\n", NOTFIXED, i);
    }
    printf("]\n");
}
