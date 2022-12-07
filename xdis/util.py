# Much of this is borrowed from Python's Lib/dis.py

from math import copysign


def code2num(code, i):
    if isinstance(code, str):
        return ord(code[i])
    else:
        return code[i]


def num2code(num):
    return num & 0xFF, num >> 8


# The `inspect` module interrogates this dictionary to build its
# list of CO_* constants. It is also used by pretty_flags to
# turn the co_flags field into a human-readable list.
COMPILER_FLAG_NAMES = {
    0x00000001: "OPTIMIZED",
    0x00000002: "NEWLOCALS",
    0x00000004: "VARARGS",
    0x00000008: "VARKEYWORDS",
    0x00000010: "NESTED",
    0x00000020: "GENERATOR",
    0x00000040: "NOFREE",
    # These are in Python 3.5 +
    0x00000080: "COROUTINE",
    0x00000100: "ITERABLE_COROUTINE",
    # These are in Python 3.6+
    0x00000200: "ASYNC_GENERATOR",
    # These are used only in Python 2.x */
    0x00001000: "GENERATOR_ALLOWED",
    0x00002000: "FUTURE_DIVISION",
    0x00004000: "ABSOLUTE_IMPORT",
    0x00008000: "FUTURE_WITH_STATEMENT",
    0x00010000: "FUTURE_PRINT_FUNCTION",
    0x00020000: "FUTURE_UNICODE_LITERALS",
    0x00040000: "FUTURE_BARRY_AS_DBFL",
    0x00080000: "FUTURE_GENERATOR_STOP",
}

# These are PYPY specific
PYPY_COMPILER_FLAG_NAMES = {
    0x00100000: "PYPY_KILL_DOCSTRING",
    0x00200000: "PYPY_YIELD_INSIDE_TRY",
    0x00000400: "PYPY_ONLY_AST",
    0x00000800: "PYPY_IGNORE_COOKIE",
    0x10000000: "PYPY_ACCEPT_NULL_BYTES",
}

# Invert above dictionary, so we can look up a bit value
# from the compile flag name
COMPILER_FLAG_BIT = dict(
    (v, k) for (k, v) in COMPILER_FLAG_NAMES.items()
)

# Allow us to access by just name, prefixed with CO. e.g
# CO_OPTIMIZED, CO_NOFREE
globals().update(dict(("CO_" + k, v) for (k, v) in COMPILER_FLAG_BIT.items()))


def co_flags_is_async(co_flags):
    """
    Return True iff co_flags indicates an async function.
    """
    return co_flags & (
        COMPILER_FLAG_BIT["COROUTINE"]
        | COMPILER_FLAG_BIT["ITERABLE_COROUTINE"]
        | COMPILER_FLAG_BIT["ASYNC_GENERATOR"]
    )


def code_has_star_arg(code):
    """Return True iff
    the code object has a variable positional parameter (*args-like)"""
    return (code.co_flags & 4) != 0


def code_has_star_star_arg(code):
    """Return True iff
    The code object has a variable keyword parameter (**kwargs-like)."""
    return (code.co_flags & 8) != 0


def is_negative_zero(n):
    """Returns true if n is -0.0"""
    return n == 0.0 and copysign(1, n) == -1


def better_repr(v):
    """Work around Python's not orthogonal and unhelpful repr() for primitive float
    and complex."""
    if isinstance(v, float):
        # float values 'nan' and 'inf' are not directly
        # representable in Python before Python 3.5. In Python 3.5
        # it is accessible via a library constant math.inf.  We
        # will canonicalize representation of these value as
        # float('nan') and float('inf')
        if str(v) in frozenset(["nan", "-nan", "inf", "-inf"]):
            return "float('%s')" % v
        elif is_negative_zero(v):
            return "-0.0"
        return repr(v)
    elif isinstance(v, complex):
        real = better_repr(v.real)
        imag = better_repr(v.imag)
        # FIXME: we could probably use repr() in most cases
        # sort out when that's possible.
        # The below round trips, and Python's repr() isn't.
        return "complex(%s, %s)" % (real, imag)
    elif isinstance(v, tuple):
        if len(v) == 1:
            return "(%s,)" % better_repr(v[0])
        return "(%s)" % ", ".join(better_repr(i) for i in v)
    elif isinstance(v, list):
        if len(v) == 1:
            return "[%s,]" % better_repr(v[0])
        return "[%s]" % ", ".join(better_repr(i) for i in v)
    # TODO: elif deal with sets and dicts
    else:
        return repr(v)
