# (C) Copyright 2017 by Rocky Bernstein
from xdis import PYTHON3
import inspect, types
class Code3:
    """Class for a Python3 code object used when a Python interpreter less than 3 is
    working on Python3 bytecode. It also functions as an object that can be used
    to build or write a Python3 code object, since we allow mutable structures.
    When done mutating, call method freeze().

    For convenience in generating code objects, fields like
    `co_consts`, co_names which are (immutable) tuples in the end-result can be stored
    instead as (mutable) lists. Likewise the line number table `co_lnotab`
    can be stored as a simple list of offset, line_number tuples.
    """
    def __init__(self, co_argcount, co_kwonlyargcount, co_nlocals,
                 co_stacksize, co_flags, co_code,
                 co_consts, co_names, co_varnames, co_filename, co_name,
                 co_firstlineno, co_lnotab, co_freevars, co_cellvars):
        self.co_argcount = co_argcount
        self.co_kwonlyargcount = co_kwonlyargcount
        self.co_nlocals = co_nlocals
        self.co_stacksize = co_stacksize
        self.co_flags = co_flags
        self.co_code = co_code
        self.co_consts = co_consts
        self.co_names = co_names
        self.co_varnames = co_varnames
        self.co_filename = co_filename
        self.co_name = co_name
        self.co_firstlineno = co_firstlineno
        self.co_lnotab = co_lnotab
        self.co_freevars = co_freevars
        self.co_cellvars = co_cellvars

    def encode_lineno_tab(self):
        cur_line = self.co_firstlineno
        co_lnotab = b''

        for offset, line_number in self.co_lnotab:
            while offset >= 256:
                co_lnotab.append(chr(255))
                co_lnotab.append(chr(0))
                offset -= 255
            while line_number >= 256:
                co_lnotab.append(chr(0))
                co_lnotab.append(chr(255))
                line_number -= 255
                cur_line += 255
            co_lnotab += bytearray([offset])
            co_lnotab += bytearray([line_number - cur_line])
            cur_line = line_number

        self.co_lnotab = co_lnotab

    def freeze(self):
        for field in 'co_consts co_names co_varnames'.split():
            val = getattr(self, field)
            if isinstance(val, list):
                setattr(self, field, tuple(val))

        if isinstance(self.co_lnotab, list):
            # We assume we have a list of tuples:
            # (offset, linenumber) which we convert
            # into the encoded format
            self.encode_lineno_tab()


        if PYTHON3:
            args = (self.co_argcount,
                    self.co_kwonlyargcount,
                    self.co_nlocals,
                    self.co_stacksize,
                    self.co_flags,
                    self.co_code,
                    self.co_consts,
                    self.co_names,
                    self.co_varnames,
                    self.co_filename,
                    self.co_name,
                    self.co_firstlineno,
                    self.co_lnotab,
                    self.co_freevars,
                    self.co_cellvars)
            return types.CodeType(*args)
        else:
            return self


    def check(self):
        for field in 'co_argcount co_nlocals co_flags co_firstlineno'.split():
            val = getattr(self, field)
            assert isinstance(val, int), \
                "%s should be int, is %s" % (field, type(val))
        for field in 'co_consts co_names co_varnames'.split():
            val = getattr(self, field)
            assert isinstance(val, tuple), \
                "%s should be tuple, is %s" % (field, type(val))


class Code2:
    """Class for a Python2 code object used when a Python 3 interpreter is
    working on Python2 bytecode. It also functions as an object that can be used
    to build or write a Python3 code object, since we allow mutable structures.
    When done mutating, call method freeze().

    For convenience in generating code objects, fields like
    `co_consts`, co_names which are (immutable) tuples in the end-result can be stored
    instead as (mutable) lists. Likewise the line number table `co_lnotab`
    can be stored as a simple list of offset, line_number tuples.

    """
    def __init__(self, co_argcount, co_kwonlyargcount, co_nlocals, co_stacksize,
                 co_flags, co_code,
                 co_consts, co_names, co_varnames, co_filename, co_name,
                 co_firstlineno, co_lnotab, co_freevars, co_cellvars):
        self.co_argcount = co_argcount
        # Note: There is no kwonlyargcount in Python2
        self.co_kwonlyargcount = co_kwonlyargcount
        self.co_nlocals = co_nlocals
        self.co_stacksize = co_stacksize
        self.co_flags = co_flags
        self.co_code = co_code
        self.co_consts = co_consts
        self.co_names = co_names
        self.co_varnames = co_varnames
        self.co_filename = co_filename
        self.co_name = co_name
        self.co_firstlineno = co_firstlineno
        self.co_lnotab = co_lnotab
        self.co_freevars = co_freevars
        self.co_cellvars = co_cellvars
        return

    def encode_lineno_tab(self):
        cur_line = self.co_firstlineno
        co_lnotab = ''

        for offset, line_number in self.co_lnotab:
            while offset >= 256:
                co_lnotab.append(chr(255))
                co_lnotab.append(chr(0))
                offset -= 255
            while line_number >= 256:
                co_lnotab.append(chr(0))
                co_lnotab.append(chr(255))
                line_number -= 255
                cur_line += 255
            co_lnotab += chr(offset)
            co_lnotab += chr(line_number - cur_line)
            cur_line = line_number

        self.co_lnotab = co_lnotab


    def freeze(self):
        for field in 'co_consts co_names co_varnames'.split():
            val = getattr(self, field)
            if isinstance(val, list):
                setattr(self, field, tuple(val))

        if isinstance(self.co_lnotab, list):
            # We assume we have a list of tuples:
            # (offset, linenumber) which we convert
            # into the encoded format

            # FIXME: handle PYTHON 3
            self.encode_lineno_tab()


        if PYTHON3:
            delattr(self, 'co_kwonlyargcount')
            return self
        else:
            args = (self.co_argcount,
                    self.co_nlocals,
                    self.co_stacksize,
                    self.co_flags,
                    self.co_code,
                    self.co_consts,
                    self.co_names,
                    self.co_varnames,
                    self.co_filename,
                    self.co_name,
                    self.co_firstlineno,
                    self.co_lnotab,
                    self.co_freevars,
                    self.co_cellvars)
            return types.CodeType(*args)


    def check(self):
        for field in 'co_argcount co_nlocals co_flags co_firstlineno'.split():
            val = getattr(self, field)
            assert isinstance(val, int), \
                "%s should be int, is %s" % (field, type(val))
        for field in 'co_consts co_names co_varnames'.split():
            val = getattr(self, field)
            assert isinstance(val, tuple), \
                "%s should be tuple, is %s" % (field, type(val))


def iscode(obj):
    """A replacement for inspect.iscode() which we can't used because we may be
    using a different version of Python than the version of Python used
    in creating the byte-compiled objects. Here, the code types may mismatch.
    """
    return inspect.iscode(obj) or isinstance(obj, Code3) or isinstance(obj, Code2)

def code_has_star_arg(code):
    """Return True iff
    the code object has a variable positional parameter (*args-like)"""
    return (code.co_flags & 4) != 0

def code_has_star_star_arg(code):
    """Return True iff
    The code object has a variable keyword parameter (**kwargs-like)."""
    return (code.co_flags & 8) != 0
