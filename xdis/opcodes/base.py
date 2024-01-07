# (C) Copyright 2017, 2019-2023 by Rocky Bernstein
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
Common routines for entering and classifying opcodes. Inspired by,
limited by, and somewhat compatible with the corresponding
Python opcode.py structures
"""

from copy import copy

from xdis import wordcode
from xdis.cross_dis import findlabels, findlinestarts, get_jump_target_maps
from xdis.version_info import IS_PYPY, PYTHON_VERSION_TRIPLE

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

# opcodes that perform a binary operator of the top two stack entries
binaryop = set([])

hascompare = []
hascondition = []  # conditional operator; has jump offset
hasconst = []
hasfree = []
hasjabs = []
hasjrel = []
haslocal = []
hasname = []
hasnargs = []  # For function-like calls
hasstore = []  # Some sort of store operation
hasvargs = []  # Similar but for operators BUILD_xxx
nofollow = []  # Instruction doesn't fall to the next opcode

nullaryop = set([])  # Instruction do not consume a stack entry

# opmap[opcode_name] => opcode_number
opmap = {}

# opcode[i] => opcode name
opname = [""] * 256

# oppush[op] => number of stack entries pushed
oppush = [0] * 256

# oppop[op] => number of stack entries popped
oppop = [0] * 256

# opcodes that perform a unary operation of the top stack entry
unaryop = set()
# Opcodes greater than 90 take an instruction operand or "argument"

# as opcode.py likes to call it.
HAVE_ARGUMENT = 90

fields2copy = """
binaryop
hascompare hascondition
hasconst hasfree hasjabs hasjrel haslocal
hasname hasnargs hasstore hasvargs oppop oppush
nofollow nullaryop unaryop
""".split()


def init_opdata(loc, from_mod, version_tuple=None, is_pypy=False):
    """Sets up a number of the structures found in Python's
    opcode.py. Python opcode.py routines assign attributes to modules.
    In order to do this in a modular way here, the local dictionary
    for the module is passed.
    """

    if version_tuple is not None:
        loc["python_version"] = version_tuple
    loc["is_pypy"] = is_pypy
    loc["cmp_op"] = cmp_op
    loc["HAVE_ARGUMENT"] = HAVE_ARGUMENT
    loc["findlinestarts"] = findlinestarts
    if version_tuple is None or version_tuple <= (3, 5):
        loc["findlabels"] = findlabels
        loc["get_jump_targets"] = findlabels
        loc["get_jump_target_maps"] = get_jump_target_maps
    else:
        loc["findlabels"] = wordcode.findlabels
        loc["get_jump_targets"] = wordcode.findlabels
        loc["get_jump_target_maps"] = wordcode.get_jump_target_maps

    if from_mod is not None:
        loc["opmap"] = copy(from_mod.opmap)
        loc["opname"] = copy(from_mod.opname)
        for field in fields2copy:
            loc[field] = copy(getattr(from_mod, field))
        pass
    else:
        # FIXME: DRY with above
        loc["binaryop"] = set([])
        loc["hascompare"] = []
        loc["hascondition"] = []
        loc["hasconst"] = []
        loc["hasfree"] = []
        loc["hasjabs"] = []
        loc["hasjrel"] = []
        loc["haslocal"] = []
        loc["hasname"] = []
        loc["hasnargs"] = []
        loc["hasstore"] = []
        loc["hasvargs"] = []
        loc["nofollow"] = []
        loc["nullaryop"] = set([])
        loc["opmap"] = {}
        loc["opname"] = [""] * 256
        for op in range(256):
            loc["opname"][op] = "<%r>" % (op,)
        loc["oppop"] = [0] * 256
        loc["oppush"] = [0] * 256
        loc["unaryop"] = set([])


def binary_op(loc, name, opcode, pop=2, push=1):
    loc["binaryop"].add(opcode)
    def_op(loc, name, opcode, pop, push)


def compare_op(loc, name, opcode, pop=2, push=1):
    def_op(loc, name, opcode, pop, push)
    loc["hascompare"].append(opcode)
    loc["binaryop"].add(opcode)


def conditional_op(loc, name, opcode):
    loc["hascompare"].append(opcode)


def const_op(loc, name, opcode, pop=0, push=1):
    def_op(loc, name, opcode, pop, push)
    loc["hasconst"].append(opcode)
    loc["nullaryop"].add(opcode)


def def_op(
    loc,
    op_name,
    opcode,
    pop=-2,
    push=-2,
    fallthrough=True,
):
    loc["opname"][opcode] = op_name
    loc["opmap"][op_name] = opcode
    loc["oppush"][opcode] = push
    loc["oppop"][opcode] = pop
    if not fallthrough:
        loc["nofollow"].append(opcode)


def free_op(loc, name, opcode, pop=0, push=1):
    def_op(loc, name, opcode, pop, push)
    loc["hasfree"].append(opcode)


def jabs_op(
    loc,
    name,
    opcode,
    pop=0,
    push=0,
    conditional=False,
    fallthrough=True,
):
    def_op(loc, name, opcode, pop, push, fallthrough=fallthrough)
    loc["hasjabs"].append(opcode)
    if conditional:
        loc["hascondition"].append(opcode)


def jrel_op(loc, name, opcode, pop=0, push=0, conditional=False, fallthrough=True):
    def_op(loc, name, opcode, pop, push)
    loc["hasjrel"].append(opcode)
    if conditional:
        loc["hascondition"].append(opcode)


def local_op(loc, name, opcode, pop=0, push=1):
    def_op(loc, name, opcode, pop, push)
    loc["haslocal"].append(opcode)
    loc["nullaryop"].add(opcode)


def name_op(loc, op_name, opcode, pop=-2, push=-2):
    def_op(loc, op_name, opcode, pop, push)
    loc["hasname"].append(opcode)
    loc["nullaryop"].add(opcode)


def nargs_op(loc, name, op, pop=-2, push=-2, fallthrough=True):
    def_op(loc, name, op, pop, push, fallthrough=fallthrough)
    loc["hasnargs"].append(op)


def opcode_check(loc):
    """When the version of Python we are running happens
    to have the same opcode set as the opcode we are
    importing, we perform checks to make sure our opcode
    set matches exactly.
    """
    if (PYTHON_VERSION_TRIPLE[:2] == loc["python_version"][:2]) and IS_PYPY == loc[
        "is_pypy"
    ]:
        try:
            import dis

            opmap = fix_opcode_names(dis.opmap)
            # print(set(opmap.items()) - set(loc['opmap'].items()))
            # print(set(loc['opmap'].items()) - set(opmap.items()))

            assert all(item in opmap.items() for item in loc["opmap"].items())
            assert all(item in loc["opmap"].items() for item in opmap.items())
        except Exception:
            pass


def rm_op(loc, name, op):
    """Remove an opcode. This is used when basing a new Python release off
    of another one, and there is an opcode that is in the old release
    that was removed in the new release.
    We are pretty aggressive about removing traces of the op.
    """

    # opname is an array, so we need to keep the position in there.
    loc["opname"][op] = "<%s>" % op

    if op in loc["hascompare"]:
        loc["hascompare"].remove(op)
    if op in loc["hascondition"]:
        loc["hascondition"].remove(op)
    if op in loc["hasconst"]:
        loc["hasconst"].remove(op)
    if op in loc["hasfree"]:
        loc["hasfree"].remove(op)
    if op in loc["hasjabs"]:
        loc["hasjabs"].remove(op)
    if op in loc["hasjrel"]:
        loc["hasjrel"].remove(op)
    if op in loc["haslocal"]:
        loc["haslocal"].remove(op)
    if op in loc["hasname"]:
        loc["hasname"].remove(op)
    if op in loc["hasnargs"]:
        loc["hasnargs"].remove(op)
    if op in loc["hasstore"]:
        loc["hasstore"].remove(op)
    if op in loc["hasvargs"]:
        loc["hasvargs"].remove(op)
    if op in loc["nofollow"]:
        loc["nofollow"].remove(op)

    if loc["opmap"][name] != op:
        print(name, loc["opmap"][name], op)
    assert loc["opmap"][name] == op
    del loc["opmap"][name]


def store_op(loc, name, op, pop=0, push=1, is_type="def"):
    if is_type == "name":
        name_op(loc, name, op, pop, push)
        loc["nullaryop"].remove(op)
    elif is_type == "local":
        local_op(loc, name, op, pop, push)
        loc["nullaryop"].remove(op)
    elif is_type == "free":
        free_op(loc, name, op, pop, push)
    else:
        assert is_type == "def"
        def_op(loc, name, op, pop, push)
    loc["hasstore"].append(op)


def unary_op(loc, name, op, pop=1, push=1):
    loc["unaryop"].add(op)
    def_op(loc, name, op, pop, push)


# This is not in Python. The operand indicates how
# items on the pop from the stack. BUILD_TUPLE_UNPACK
# is line this.
def varargs_op(loc, op_name, op_code, pop=-1, push=1):
    def_op(loc, op_name, op_code, pop, push)
    loc["hasvargs"].append(op_code)


# Some of the convoluted code below reflects some of the
# many Python idiocies over the years.


def finalize_opcodes(loc):
    # Not sure why, but opcode.py address has opcode.EXTENDED_ARG
    # as well as opmap['EXTENDED_ARG']
    loc["EXTENDED_ARG"] = loc["opmap"]["EXTENDED_ARG"]

    # In Python 3.6+ this is 8, but we expect
    # those opcodes to set that
    if "EXTENDED_ARG_SHIFT" not in loc:
        loc["EXTENDED_ARG_SHIFT"] = 16

    loc["ARG_MAX_VALUE"] = (1 << loc["EXTENDED_ARG_SHIFT"]) - 1
    loc["EXTENDED_ARG"] = loc["opmap"]["EXTENDED_ARG"]

    loc["opmap"] = fix_opcode_names(loc["opmap"])

    # Now add in the attributes into the module
    for op in loc["opmap"]:
        loc[op] = loc["opmap"][op]
    loc["JUMP_OPs"] = frozenset(loc["hasjrel"] + loc["hasjabs"])
    loc["NOFOLLOW"] = frozenset(loc["nofollow"])
    loc["operator_set"] = frozenset(
        loc["nullaryop"]
        | loc["unaryop"]
        | loc["binaryop"]
        | set([op for op in loc["hasnargs"] if op not in loc["nofollow"]])
        | set([op for op in loc["hasvargs"] if loc["oppush"][op] == 1])
    )
    opcode_check(loc)
    return


def fix_opcode_names(opmap):
    """
    Python stupidly named some OPCODES with a + which prevents using opcode name
    directly as an attribute, e.g. SLICE+3. So we turn that into SLICE_3, so we
    can then use opcode_23.SLICE_3.  Later Python's fix this.
    """
    return dict([(k.replace("+", "_"), v) for (k, v) in opmap.items()])


def update_pj3(g, loc):
    if loc["version_tuple"] < (3, 11):
        g.update({"PJIF": loc["opmap"]["POP_JUMP_IF_FALSE"]})
        g.update({"PJIT": loc["opmap"]["POP_JUMP_IF_TRUE"]})
    update_sets(loc)


def update_pj2(g, loc):
    g.update({"PJIF": loc["opmap"]["JUMP_IF_FALSE"]})
    g.update({"PJIT": loc["opmap"]["JUMP_IF_TRUE"]})
    update_sets(loc)


def update_sets(loc):
    loc["COMPARE_OPS"] = frozenset(loc["hascompare"])
    loc["CONDITION_OPS"] = frozenset(loc["hascondition"])
    loc["CONST_OPS"] = frozenset(loc["hasconst"])
    loc["FREE_OPS"] = frozenset(loc["hasfree"])
    loc["JREL_OPS"] = frozenset(loc["hasjrel"])
    loc["JABS_OPS"] = frozenset(loc["hasjabs"])

    python_version = loc.get("python_version")
    if python_version and python_version < (3, 11):
        loc["JUMP_UNCONDITONAL"] = frozenset(
            [loc["opmap"]["JUMP_ABSOLUTE"], loc["opmap"]["JUMP_FORWARD"]]
        )
    elif python_version:
        loc["JUMP_UNCONDITONAL"] = frozenset(
            [
                loc["opmap"]["JUMP_FORWARD"],
                loc["opmap"]["JUMP_BACKWARD"],
                loc["opmap"]["JUMP_BACKWARD_NO_INTERRUPT"],
            ]
        )
    else:
        loc["JUMP_UNCONDITONAL"] = frozenset([loc["opmap"]["JUMP_FORWARD"]])
    if PYTHON_VERSION_TRIPLE < (3, 8, 0) and python_version and python_version < (3, 8):
        loc["LOOP_OPS"] = frozenset([loc["opmap"]["SETUP_LOOP"]])
    else:
        loc["LOOP_OPS"] = frozenset()

    loc["LOCAL_OPS"] = frozenset(loc["haslocal"])
    loc["JUMP_OPS"] = (
        loc["JABS_OPS"] | loc["JREL_OPS"] | loc["LOOP_OPS"] | loc["JUMP_UNCONDITONAL"]
    )
    loc["NAME_OPS"] = frozenset(loc["hasname"])
    loc["NARGS_OPS"] = frozenset(loc["hasnargs"])
    loc["VARGS_OPS"] = frozenset(loc["hasvargs"])
    loc["STORE_OPS"] = frozenset(loc["hasstore"])


def dump_opcodes(opmap):
    """Utility for dumping opcodes"""
    op2name = {}
    for k in opmap.keys():
        op2name[opmap[k]] = k
    for i in sorted(op2name.keys()):
        print("%-3s %s" % (str(i), op2name[i]))
