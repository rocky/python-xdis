The C programs are modified from a c program used in Maynard Python
assembler for Python 3.3-3.6

The following is from Maynard:

Copyright 2013-2015 by Larry Hastings

When you create a bytecode function in Python, you have to tell Python
how deep the function's stack will ever go.  To do that, you need to
know how each opcode will affect the stack--that opcode's "stack
effect".

Prior to Python 3.4, Python programmers didn't have any way to look up
the stack effect of a bytecode.  I (Larry Hastings) wrote these
compute_stackeffect tools so that Maynard could calculate stack
effects.

Python 3.4 added a new function, opcode.stack_effect().  So these
tools were only necessary to support Python 3.1, 3.2, and 3.3.
