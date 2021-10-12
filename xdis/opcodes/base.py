# (C) Copyright 2017, 2019-2021 by Rocky Bernstein
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
Common routines for entering and classifiying opcodes. Inspired by,
limited by, and somewhat compatible with the corresponding
Python opcode.py structures
"""

from copy import deepcopy
from xdis.cross_dis import (
    findlinestarts,
    findlabels,
    get_jump_target_maps,
)
from xdis import wordcode
from xdis.version_info import IS_PYPY, PYTHON_VERSION, PYTHON_VERSION_TRIPLE

cmp_op = (
    "<",
    "<=",
    "==",
    "!=",
    ">",
    ">=",
    "in",
    "not-in",
    "is",
    "is-not",
    "exception-match",
    "BAD",
)

# Opcodes greater than 90 take an instruction operand or "argument"
# as opcode.py likes to call it.
HAVE_ARGUMENT = 90

fields2copy = """
hascompare hascondition
hasconst hasfree hasjabs hasjrel haslocal
hasname hasnargs hasstore hasvargs oppop oppush
nofollow
""".split()


def init_opdata(l, from_mod, version_tuple=None, is_pypy=False):
    """Sets up a number of the structures found in Python's
    opcode.py. Python opcode.py routines assign attributes to modules.
    In order to do this in a modular way here, the local dictionary
    for the module is passed.
    """

    if version_tuple:
        l["python_version"] = version_tuple
    l["is_pypy"] = is_pypy
    l["cmp_op"] = cmp_op
    l["HAVE_ARGUMENT"] = HAVE_ARGUMENT
    l["findlinestarts"] = findlinestarts
    if version_tuple <= (3, 5):
        l["findlabels"] = findlabels
        l["get_jump_targets"] = findlabels
        l["get_jump_target_maps"] = get_jump_target_maps
    else:
        l["findlabels"] = wordcode.findlabels
        l["get_jump_targets"] = wordcode.findlabels
        l["get_jump_target_maps"] = wordcode.get_jump_target_maps

    l["opmap"] = deepcopy(from_mod.opmap)
    l["opname"] = deepcopy(from_mod.opname)

    for field in fields2copy:
        l[field] = list(getattr(from_mod, field))


def compare_op(l, name, op, pop=2, push=1):
    def_op(l, name, op, pop, push)
    l["hascompare"].append(op)


def conditional_op(l, name, op):
    l["hascompare"].append(op)


def const_op(l, name, op, pop=0, push=1):
    def_op(l, name, op, pop, push)
    l["hasconst"].append(op)


def def_op(l, op_name, opcode, pop=-2, push=-2, fallthrough=True):
    l["opname"][opcode] = op_name
    l["opmap"][op_name] = opcode
    l["oppush"][opcode] = push
    l["oppop"][opcode] = pop
    if not fallthrough:
        l["nofollow"].append(opcode)


def free_op(l, name, op, pop=0, push=1):
    def_op(l, name, op, pop, push)
    l["hasfree"].append(op)


def jabs_op(l, name, op, pop=0, push=0, conditional=False, fallthrough=True):
    def_op(l, name, op, pop, push, fallthrough=fallthrough)
    l["hasjabs"].append(op)
    if conditional:
        l["hascondition"].append(op)


def jrel_op(l, name, op, pop=0, push=0, conditional=False, fallthrough=True):
    def_op(l, name, op, pop, push)
    l["hasjrel"].append(op)
    if conditional:
        l["hascondition"].append(op)


def local_op(l, name, op, pop=0, push=1):
    def_op(l, name, op, pop, push)
    l["haslocal"].append(op)


def name_op(l, op_name, op_code, pop=-2, push=-2):
    def_op(l, op_name, op_code, pop, push)
    l["hasname"].append(op_code)


def nargs_op(l, name, op, pop=-2, push=-2, fallthrough=True):
    def_op(l, name, op, pop, push, fallthrough=fallthrough)
    l["hasnargs"].append(op)


def rm_op(l, name, op):
    """Remove an opcode. This is used when basing a new Python release off
    of another one, and there is an opcode that is in the old release
    that was removed in the new release.
    We are pretty aggressive about removing traces of the op.
    """

    # opname is an array, so we need to keep the position in there.
    l["opname"][op] = "<%s>" % op

    if op in l["hasconst"]:
        l["hasconst"].remove(op)
    if op in l["hascompare"]:
        l["hascompare"].remove(op)
    if op in l["hascondition"]:
        l["hascondition"].remove(op)
    if op in l["hasfree"]:
        l["hasfree"].remove(op)
    if op in l["hasjabs"]:
        l["hasjabs"].remove(op)
    if op in l["hasname"]:
        l["hasname"].remove(op)
    if op in l["hasjrel"]:
        l["hasjrel"].remove(op)
    if op in l["haslocal"]:
        l["haslocal"].remove(op)
    if op in l["hasname"]:
        l["hasname"].remove(op)
    if op in l["hasnargs"]:
        l["hasnargs"].remove(op)
    if op in l["hasvargs"]:
        l["hasvargs"].remove(op)
    if op in l["nofollow"]:
        l["nofollow"].remove(op)

    assert l["opmap"][name] == op
    del l["opmap"][name]


def store_op(l, name, op, pop=0, push=1, is_type="def"):
    if is_type == "name":
        name_op(l, name, op, pop, push)
    elif is_type == "local":
        local_op(l, name, op, pop, push)
    elif is_type == "free":
        free_op(l, name, op, pop, push)
    else:
        assert is_type == "def"
        def_op(l, name, op, pop, push)
    l["hasstore"].append(op)


# This is not in Python. The operand indicates how
# items on the pop from the stack. BUILD_TUPLE_UNPACK
# is line this.
def varargs_op(l, op_name, op_code, pop=-1, push=1):
    def_op(l, op_name, op_code, pop, push)
    l["hasvargs"].append(op_code)


# Some of the convoluted code below reflects some of the
# many Python idiocies over the years.


def finalize_opcodes(l):

    # Not sure why, but opcode.py address has opcode.EXTENDED_ARG
    # as well as opmap['EXTENDED_ARG']
    l["EXTENDED_ARG"] = l["opmap"]["EXTENDED_ARG"]

    # In Python 3.6+ this is 8, but we expect
    # those opcodes to set that
    if "EXTENDED_ARG_SHIFT" not in l:
        l["EXTENDED_ARG_SHIFT"] = 16

    l["ARG_MAX_VALUE"] = (1 << l["EXTENDED_ARG_SHIFT"]) - 1
    l["EXTENDED_ARG"] = l["opmap"]["EXTENDED_ARG"]

    l["opmap"] = fix_opcode_names(l["opmap"])

    # Now add in the attributes into the module
    for op in l["opmap"]:
        l[op] = l["opmap"][op]
    l["JUMP_OPs"] = frozenset(l["hasjrel"] + l["hasjabs"])
    l["NOFOLLOW"] = frozenset(l["nofollow"])
    opcode_check(l)
    return


def fix_opcode_names(opmap):
    """
    Python stupidly named some OPCODES with a + which prevents using opcode name
    directly as an attribute, e.g. SLICE+3. So we turn that into SLICE_3 so we
    can then use opcode_23.SLICE_3.  Later Python's fix this.
    """
    return dict([(k.replace("+", "_"), v) for (k, v) in opmap.items()])


def update_pj3(g, l):
    g.update({"PJIF": l["opmap"]["POP_JUMP_IF_FALSE"]})
    g.update({"PJIT": l["opmap"]["POP_JUMP_IF_TRUE"]})
    update_sets(l)


def update_pj2(g, l):
    g.update({"PJIF": l["opmap"]["JUMP_IF_FALSE"]})
    g.update({"PJIT": l["opmap"]["JUMP_IF_TRUE"]})
    update_sets(l)


def update_sets(l):
    l["COMPARE_OPS"] = frozenset(l["hascompare"])
    l["CONDITION_OPS"] = frozenset(l["hascondition"])
    l["CONST_OPS"] = frozenset(l["hasconst"])
    l["FREE_OPS"] = frozenset(l["hasfree"])
    l["JREL_OPS"] = frozenset(l["hasjrel"])
    l["JABS_OPS"] = frozenset(l["hasjabs"])
    l["JUMP_UNCONDITONAL"] = frozenset(
        [l["opmap"]["JUMP_ABSOLUTE"], l["opmap"]["JUMP_FORWARD"]]
    )
    if PYTHON_VERSION_TRIPLE < (3,8,0) and l["python_version"] < (3, 8):
        l["LOOP_OPS"] = frozenset([l["opmap"]["SETUP_LOOP"]])
    else:
        l["LOOP_OPS"] = frozenset()

    l["LOCAL_OPS"] = frozenset(l["haslocal"])
    l["JUMP_OPS"] = (
        l["JABS_OPS"] | l["JREL_OPS"] | l["LOOP_OPS"] | l["JUMP_UNCONDITONAL"]
    )
    l["NAME_OPS"] = frozenset(l["hasname"])
    l["NARGS_OPS"] = frozenset(l["hasnargs"])
    l["VARGS_OPS"] = frozenset(l["hasvargs"])
    l["STORE_OPS"] = frozenset(l["hasstore"])


def extended_format_CALL_FUNCTION(opc, instructions):
    """call_function_inst should be a "CALL_FUNCTION_KW" instruction. Look in
    `instructions` to see if we can find a method name.  If not we'll
    return None.

    """
    # From opcode description: argc indicates the total number of positional and keyword arguments.
    # Sometimes the function name is in the stack arg positions back.
    call_function_inst = instructions[0]
    assert call_function_inst.opname == "CALL_FUNCTION"
    argc = call_function_inst.arg
    (
        name_default,
        pos_args,
    ) = divmod(argc, 256)
    function_pos = pos_args + name_default * 2 + 1
    assert len(instructions) >= function_pos + 1
    for i, inst in enumerate(instructions[1:]):
        if i + 1 == function_pos:
            i += 1
            break
        if inst.is_jump_target:
            i += 1
            break
        # Make sure we are in the same basic block
        # and ... ?
        opcode = inst.opcode
        if inst.optype in ("nargs", "vargs"):
            break
        if inst.opname == "LOAD_ATTR" or inst.optype != "name":
            function_pos += (opc.oppop[opcode] - opc.oppush[opcode]) + 1
        if inst.opname in ("CALL_FUNCTION", "CALL_FUNCTION_KW"):
            break
        pass

    s = ""
    if i == function_pos:
        if instructions[function_pos].opname in (
            "LOAD_CONST",
            "LOAD_GLOBAL",
            "LOAD_ATTR",
            "LOAD_NAME",
        ):
            s = resolved_attrs(instructions[function_pos:])
            s += ": "
            pass
        pass
    s += format_CALL_FUNCTION_pos_name_encoded(call_function_inst.arg)
    return s


def resolved_attrs(instructions):
    resolved = []
    for inst in instructions:
        name = inst.argrepr
        if name:
            if name[0] == "'" and name[-1] == "'":
                name = name[1:-1]
        else:
            name = ""
        resolved.append(name)
        if inst.opname != "LOAD_ATTR":
            break
    return ".".join(reversed(resolved))


def extended_format_ATTR(opc, instructions):
    if instructions[1].opname in (
        "LOAD_CONST",
        "LOAD_GLOBAL",
        "LOAD_ATTR",
        "LOAD_NAME",
    ):
        return "%s.%s" % (instructions[1].argrepr, instructions[0].argrepr)


def extended_format_MAKE_FUNCTION_older(opc, instructions):
    """make_function_inst should be a "MAKE_FUNCTION" or "MAKE_CLOSURE" instruction. TOS
    should have the function or closure name.
    """
    # From opcode description: argc indicates the total number of positional and keyword arguments.
    # Sometimes the function name is in the stack arg positions back.
    assert len(instructions) >= 2
    inst = instructions[0]
    assert inst.opname in ("MAKE_FUNCTION", "MAKE_CLOSURE")
    s = ""
    code_inst = instructions[1]
    if code_inst.opname == "LOAD_CONST" and hasattr(code_inst.argval, "co_name"):
        s += "%s: " % code_inst.argval.co_name
        pass
    s += format_MAKE_FUNCTION_default_argc(inst.arg)
    return s


def extended_format_RAISE_VARARGS_older(opc, instructions):
    raise_inst = instructions[0]
    assert raise_inst.opname == "RAISE_VARARGS"
    assert len(instructions) >= 1
    if instructions[1].opname in (
        "LOAD_CONST",
        "LOAD_GLOBAL",
        "LOAD_ATTR",
        "LOAD_NAME",
    ):
        return resolved_attrs(instructions[1:])
    return format_RAISE_VARARGS_older(raise_inst.argval)


def extended_format_RETURN_VALUE(opc, instructions):
    return_inst = instructions[0]
    assert return_inst.opname == "RETURN_VALUE"
    assert len(instructions) >= 1
    if instructions[1].opname in (
        "LOAD_CONST",
        "LOAD_GLOBAL",
        "LOAD_ATTR",
        "LOAD_NAME",
    ):
        return resolved_attrs(instructions[1:])
    return None


def format_extended_arg(arg):
    return str(arg * (1 << 16))


def format_CALL_FUNCTION_pos_name_encoded(argc):
    """Encoded positional and named args. Used to
    up to about 3.6 where wordcodes are used and
    a different encoding occurs. Pypy36 though
    sticks to this encoded version though."""
    name_default, pos_args = divmod(argc, 256)
    return "%d positional, %d named" % (pos_args, name_default)


# After Python 3.2
def format_MAKE_FUNCTION_arg(argc):
    name_and_annotate, pos_args = divmod(argc, 256)
    annotate_args, name_default = divmod(name_and_annotate, 256)
    return "%d positional, %d name and default, %d annotations" % (
        pos_args,
        name_default,
        annotate_args,
    )


# Up to and including Python 3.2
def format_MAKE_FUNCTION_default_argc(argc):
    return "%d default parameters" % argc


# Up until 3.7
def format_RAISE_VARARGS_older(argc):
    assert 0 <= argc <= 3
    if argc == 0:
        return "reraise"
    elif argc == 1:
        return "exception"
    elif argc == 2:
        return "exception, parameter"
    elif argc == 3:
        return "exception, parameter, traceback"


def opcode_check(l):
    """When the version of Python we are running happens
    to have the same opcode set as the opcode we are
    importing, we perform checks to make sure our opcode
    set matches exactly.
    """
    if PYTHON_VERSION_TRIPLE[:2] == l["python_version"][:2] and IS_PYPY == l["is_pypy"]:
        try:
            import dis

            opmap = fix_opcode_names(dis.opmap)
            # print(set(opmap.items()) - set(l['opmap'].items()))
            # print(set(l['opmap'].items()) - set(opmap.items()))

            assert all(item in opmap.items() for item in l["opmap"].items())
            assert all(item in l["opmap"].items() for item in opmap.items())
        except:
            pass


def dump_opcodes(opmap):
    """Utility for dumping opcodes"""
    op2name = {}
    for k in opmap.keys():
        op2name[opmap[k]] = k
    for i in sorted(op2name.keys()):
        print("%-3s %s" % (str(i), op2name[i]))
