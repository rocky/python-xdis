.PHONY: all clean

C_PROGRAMS=se26 se27 se31 se32 se33
#: Build all C programs
all: $(C_PROGRAMS)

clean:
	rm -v $(C_PROGRAMS) || true

#: Build C programs to list stack-effects which are not operand-dependent
$(C_PROGRAMS): main.h
	gcc -ggdb $@.c -o $@
	./$@ > ../pytest/stackeffect/$@.py
