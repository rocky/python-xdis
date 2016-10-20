# Test write_bytecode_file
from xdis.load import write_bytecode_file
from xdis.bytecode import list2bytecode
a = """
def fact():
    a = 8
    a = 0
"""
def test_write_bytecode_file():
    import xdis.opcodes.opcode_27  as opcode_27
    # import xdis.opcodes.opcode_34  as opcode_34
    consts = (None, 2)
    varnames = ('a',)
    instructions = [
        ('LOAD_CONST', 2),
        ('STORE_FAST', 'a'),
        ('LOAD_FAST', 'a'),
        ('RETURN_VALUE',)
    ]

    bc = list2bytecode(instructions, opcode_27, varnames, consts)
    print(bc)
    c = compile(a, '<string>', 'exec')
    fn_code = c.co_consts[0]
    import types
    opt_fn_code = types.CodeType(fn_code.co_argcount,
                                 # c.co_kwonlyargcount,  Add this in Python3
                                 fn_code.co_nlocals,
                                 fn_code.co_stacksize,
                                 fn_code.co_flags,
                                 # These are changed
                                 bc,
                                 consts,

                                 fn_code.co_names,
                                 varnames,
                                 fn_code.co_filename,
                                 fn_code.co_name,
                                 fn_code.co_firstlineno,
                                 fn_code.co_lnotab,   # In general, You should adjust this
                                 fn_code.co_freevars,
                                 fn_code.co_cellvars)
    co_consts = list(c.co_consts)
    co_consts[0] = opt_fn_code
    c1 = types.CodeType(c.co_argcount,
                        # c.co_kwonlyargcount,  Add this in Python3
                        c.co_nlocals,
                        c.co_stacksize,
                        c.co_flags,
                        c.co_code,
                        tuple(co_consts),
                        c.co_names,
                        c.co_varnames,
                        c.co_filename,
                        c.co_name,
                        c.co_firstlineno,
                        c.co_lnotab,   # In general, You should adjust this
                        c.co_freevars,
                        c.co_cellvars)

    write_bytecode_file("/tmp/test3.pyc", c1, 62211, 10)
    return

test_write_bytecode_file()
