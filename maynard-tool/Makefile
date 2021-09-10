.PHONY: all clean

# Python 2.5 is the earliest version that has opcode_stack_effect
C_PROGRAMS=se25 se26 se27 se30 se31 se32 se33

#: Build all C programs
all: $(C_PROGRAMS)

clean:
	rm -v $(C_PROGRAMS) || true

#: Build C programs to list stack-effects which are not operand-dependent
$(C_PROGRAMS): main.h
	gcc -ggdb $@.c -o $@
	./$@ > ../pytest/stackeffect/$@.py
