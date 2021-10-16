6.0.0 2021-10-15
=================

Reworked for Python 3.10.

We had been internally using floating point numbers for version testing.
Clearl this doesn't work to distinguish 3.1 from 3.10.
(This was a flaw known about for a while and we'd been avoiding).

* Add 3.10 opcodes.
* Add 3.9 and 3.10 testing.
* Some tolerance for running from 3.11
* Update magic numbers
* Expanding testing to include pyston and PyPy 3.7
* Improve distribution packaging, e.g. Python 3 wheels should no longer be attmpted on Python 2.x

5.0.13 2021-09-24
=================

Added knowledge of Python versions 3.6.15 and 3.7.12.

However the main motivation was to impove packaging to handle administration
of the 3 different branches or dialects of Python 2.4-2.7, 3.1-3.2, 3.3-3.5, and 3.6+

Restrict wheel packaging for Python 3 only.

Use the wheel for only the 3.x and newer version of Python.
Use eggs for 2.x versions (and others as well).


5.0.12 2021-09-11
=================

* Add Python version 3.9.7
* Document unmarshal better
* Correct stack information for `IMPORT_NAME`
* Fix bug in code type handling where bytes were showing up as strings
* More type annotations in master branch. Create more older variations without annotations

5.0.11 2021-07-05
================

* Add Python versions 3.9.6, 3.7.11, 3.8.11, and 3.6.14
* Format Python various files using black. (Not completely done yet though)

5.0.10 2021-06-16
================

- Note Python versions 3.8.10 and 3.9.5
- Incorrect variable name in marshal dump (used in writing `.pyc` files). PR #75

5.0.9 2021-04-16
================

In general, better Python 3.9 support.

- Improve 3.9 `IS_OP` and `CONTAINS_OP` operand formatting
- Correct disassembly of 3.9 bytecode from other bytecode
- Accept 3.9.3 and 3.9.4 as a valid 3.9 version
- Accept 3.8.9 as a valid 3.8 version

5.0.8 2021-03-13
================

- PR #73 from mitre:
  Allow an alternate opmap - adds the capability to disassemble python bytecode that has
  been frozen with a custom opcode mapping. This is particularly useful for disassembling
  malware that uses custom opcode mappings in an attempt to hinder disassembly with standard
  tools. The updates in this pull request are used by pydecipher, a tool to unfreeze and deobfuscate frozen python code.

- Add Python versions 3.8.8 and 3.9.2

5.0.7 2021-01-10
================

* Add Python 3.8.7

5.0.6 2020-12-16
================

* Add Python 3.9.1

5.0.5 2020-10-27
================

* Add support for Python2.7 on Ubuntu 20.04
* Bump versions for Python 3.8.6 and 3.5.10
* Release instructions moved to wiki
* `VERSION` -> `__version__` because Python prefers it that way

5.0.4 2020-08-30
================

* Add python versions 3.6.12, 3.7.9
* extended arg disassembly handling for `LOAD_ATTR` and `STORE_ATTR`

5.0.3 2020-07-28
================

* Add versions 3.8.5, 3.7.8, and 3.6.11
* Clarify changes to 3.8 `ROT_FOUR`
* Update 3.9 magics and opcodes

5.0.2 2020-07-25
================

* Add Python 3.8.4 as a 3.8 release
* pydisasm.py Python 3.3 tolerance
* Make pydoc's version reporting show xdis's version

5.0.1 2020-06-28
================

Two small improvements that are useful in the forthcoming [trepan3k](https://pypi.org/project/trepan3k) release:

* interpret `RAISE_VARARGS`'s `argc` parameter. Some other formatting was extended too
* `check_object_path()` is more lenient in the path name (it doesn't have to end in `.py` anymore), but it is
   more stringent about what constitutes Python source (it compiles the text to determine validity)
* In the above `is_python_source()` and `is_bytecode_extension()` are used. They are also exported.


5.0.0 2020-06-27
================

Disassembly format and options have simplified and improved.

I had this "Aha!" moment working on the cross-version interpreter x-python. It can show a better disassembly because it has materialized stack entries.
So for example when a `COMPARE_OP` instruction is run it can show what operands are getting compared.

It was then that I realized that this is also true much of the time statically. For example you'll often find a `LOAD_CONST` instruction before a `RETURN_VALUE` and when you do can show exactly what is getting returned. Although cute, the place where something like this is most appreciated and needed is in calling functions such as via `CALL_FUNCTION`. The situation here is that the name of the function is on the stack and it can be several instructions back depending on the number of parameters. However in a large number of cases, by tracking use of stack effects (added in a previous release), we can often location the `LOAD_CONST` of that function name.

Note though that we don't attempt work across basic blocks to track down information. Nor do we even attempt recreate expression trees. We don't track across call which has a parameter return value which is the return from another call. Still, I find this all very useful.

This is not shown by default though. Instead we use a mode called "classic". To get this, in `pydisasm` use the `--format extended` or `--format extended-bytes`.

And that brings up a second change in formatting. Before, we had separate flags and command-line options for whether to show just the header, and whether to include bytecode ops in the output. Now there is just a single parameter called `asm_format`, and choice option `--format` (short option `-F`).

As a result this release is incompatible with prior releases, hence the version bump.

A slight change was made in "classic" output. Before we had shown the index into some code table, like `co_consts` or `co_varnames`. That no longer appears. If you want that information select either the `bytes` or `extended-bytes` formats.

A bug was fixed in all offsets in the recently-added `xdis.lineoffsets` module.


4.7.0 2020-06-12 Fleetwood66
============================

Routines for extracting line and offset information from code objects was added.

Specifically in module `xdis.lineoffsets`:
	* classes:	`LineOffsetInfo`, `LineOffsets`, and `LineOffsetsCompact`
	* functions: `lineoffsets_in_file()`, `lineoffsets_in_module()`

This is need to better support debugging which is done via module
pyficache.

In the future, I intend to make use of this to disambiguate which offset to break at when there are several for a line.  Or to indicate better which function or module the line is located in when reporting lines.

For example in:

```python
  z = lambda x, y: x + y
```

there two offsets associated with that line. The first is to the assignment of `z` while the second is to the addition expression inside the lambda.

In other news, a long-standing bug was fixed to handle bytestring constants in 3.x. We had been erroneously converting bytestrings into 3.x. However when decompiling 1.x or 2.x bytecode from 3.x we still need to convert bytestrings into strings.

Also, operand formatting in assembly for `BUILD_UNMAP_WITH_CALL` has been improved, and
we note how the operand encoding has changed between 3.5. and 3.6.

Disassembly now properly marks offsets where the line number that doesn't change from the previous entry.

4.6.1 2020-05-30 Lady Elaine
============================

The main purpose of this release is to support x-python better.

* Fix a bad bug in handling byte constants in 3.x. How could this go so long fixed?
* More custom formatting across more opcodes
   * `CALL_FUNCTION`, `CALL_FUNCTION_KW`, `CALL_FUNCTION_VAR`, etc
   * `MAKE_FUNCTION`
   * `LOAD_CONST` in some cases
* Go over magics numbers, yet again
* Update *See also* links

4.6.0 2020-05-18 Décadi 30th Floréal - Shepherd's Crook
=======================================================

The major impetus for this release is expanding the Python in Python interpreter [x-python](https://pypi.org/project/x-python/)
(A new release of that will go out after this.)

* 3.8.3 added as a valid 3.8 release
* command program `pydisasm` disassembles more Python source files now
* Add better argument formatting on `CALL_FUNCTION` and `MAKE_FUNCTION`
* bytecode.py now has `distb`
* opcode modules now have variable `python_implementation` which is either "CPython" or "PyPY"
* Reformat a number of files using blacken, and lint using flymake
* Update `__init__.py` exports based on what is used in projects `uncompyle6`, `decompyle3`, `trepan3k`,
  `xasm` and `x-python`
* Remove duplicate `findlinestarts()` code. Remove testing on the Python version and simplify
  this where possible.
* get_opcode_module allows either a float and string datatype for the version, and coverts
  the bytecode datatype when needed
* Fix a bugs in marshal and unmarshal

See the commit history or ChangeLog file for a full list of changes


4.5.1 2020-04-26 stack_effects redux
====================================

* Fix bug in marshal for 3.8+ (include posonlyargcount)
* Go over stack effects from 2.5 to 3.4 using and idea from Maynard
* Expand stack-effect testing

4.5.0 2020-04-20 stack_effects
==============================

* `stack_effects()` checked against Python 3.4+ is now in place.
* Added `stack_effects()` function to `std.py` since this is part of the API
* `cross_xdis.py` file/module now has `dis.py` functions split off from `bytecode.py`
* `Instructions` class is in its own module too.
* Python 2.7.18 added into magics.

Incompatibility with earlier versions:

Note: as a result of the reorganization, exported functions from
bytecode are now in cross_dis.  However functions are exported from
the top-level so use that and there will be no disruption in the
future. For example `from xdis import iscode, instruction_size,
code_info`.

4.4.0 2020-04-20 modern-pitch A
===============================

Incompatibility: `load_module()` and `load_module_from_file_object()` now return a couple more parameters: is_pypy, and the sip_hash value when that is available. The timestamp and file_size returned on these functions is now None when they aren't available. Previously timestamp had been 0.

* --asm option fixes
* Show sip hash in 3.7+ when that is used
* Handle PEP 552 bytecode-file variations more properly
* Detect more intermediate Python versions in `load_code_from_file_object()`
* 3.8+ posonlyargcount in assembly...  rename Kw-only field to Keyword-only
* Add 3.5 canonic bytecode version Marshal `dumps()`
* convert from byte() to str() in dumps() when needed in 3.x
* to_native() convert to bytes from string when needed in 3.x.
* clean up loading code by using float version values rather than magic values

4.3.2 2020-04-16 portable code type
===================================

Fix a few more bugs caused by the recent portability refactoring

* back off line-number table decompression for Python < 3.0 for now. This breaks decomplation.
* bytecode fix for cell_names now that code types are more stringent.


4.3.1 2020-04-16
===================================

Fix bug in handling Python 3.8 bytecode.

Sadly, I inadvertently wasn't testing 3.8 bytecode before. That's now fixed too.

Release revoked - use 4.3.2

4.3.0 2020-04-16
===================================

Release revoked - use 4.3.2

Portable Code Type
------------------

A portable version of types.CodeType was rewritten, to make it

* easier to use
* and catch more errors
* more complete in tracking Python `types.CodeType` changes
* simpler in implementation by using type inheretence
* more general

Previously getting bytecode read from a bytecode file or from a code object requiring knowing a lot about the Python version of the code type and of the currently running interpreter. That is gone now.

Use `codeType2Portable()` to turn a native `types.CodeType` or a structure read in from a bytecode file into a portable code type. The portable code type allows fields to be mutated, and is more flexible in the kinds of datatypes it allows.

For example lists of thing like `co_consts`, or `varnames` can be Python lists as well as tuples. The line number table is stored as a dictionary mapping of address to bytecode offset rather than as a compressed structure. Bytecode can either be a string (which is advantageous if you are running Python before 3.x) or a sequence of bytes which is the datatype of a code object for 3.x.

However when you need a `type.CodeType` that can be can be `eval()`'d by the Python interpreter you are running, use the `to_native()` method on the portable code type returned. It will compress and encode the line number table, and turn lists into tuples and convert other datatypes to the right type as needed.

If you have a *complete* `types.Codetype` structure for a particular Python version whether, it is the one the current Python interpreter is using or not, use the `to_portable()` function and it will figure out based on the version parameter supplied (or use the current Python interpreter version if none supplieed), which particlar portable code type is the right one.

If on the other hand, you have a number of code-type fields which may be incomplete, but still want to work with something that has code-type characteristics while not worring about which fields are required an their exact proper datatypes, use the `CodeTypeUnion` structure.

Internally, we use OO inheretence to reduce the amount of duplicate code. The `load_code_internal()` function from `unmarshal.py` is now a lot shorter and cleaner as a result of this reorganization.

### New Portable Code Methods, Modules and Classes

* Python 3.8-ish `replace()` method has been added to the portable code types
* Portable code type classes `Code13`, `Code15` have been added to more precisely distinguish Python 1.3 and 1.5 code types. The other portable code classes are `Code2`, `Code3`, and `Code38`.
* the to_native() conversts a portable code type into a native code type
* the `decode_lineno_tab()` method on portable code types from Python 1.5 on decompresses the Python encode line number table into a dictionary mapping offset to line number.


Incompatibility
---------------

The module `xdis.code` has been remamed to `xdis.codetype` and with that the function `iscode()` moved as well. In previous versions to use `iscode()` you might import it from `xdis.code`; now simply import it from `xdis`. In general function that had been imported from a module under `xdis` can now be imported simply from `xdis`.

The classes `Compat3Code` and function `code2compat()` and `code3compat()` have been removed. `Compat2Code` is still around for dropbox 2.5, but that is deprecated and will be removed when I can figure out how to remove it from dropbox 2.5.

Other Changes
-------------

CI testing for older testing has been fixed now that 2.7 is even more deprecated.

4.2.3 2020-03-16 post ides-of-march
===================================
s
* Add Python versions: 3.7.7, 3.8.2, and 3.9.0alpha1,
* Create a set for "STORE" instructions
* facilitate code type freezing (PR #57)
* Warn about cross-decompilation problems for byte types

4.2.2 2019-12-24 christmas + hannukah
=====================================

* Add Python versions: 3.6.10, 3.7.6. 3.8.1,
* Update 3.9-dev to 3.9.0alpha2
* Add interpolation of FUNCTION_CALL_{KW,EX} argument for 3.7-3.9
* Better output of complex type values


4.2.1 2019-12-16
=================

Correct and clean up compiler flags. Add 3.5+ `ITERABLE_COROUTINE` and
3.6+ `ASYNC_GENERATOR`.

Clean up PYPY 3.6 flags and opcodes Many thanks again to Arman
Rigo. Split PYPY specfic compiler-specific flags into its own thing.

4.2.0 2019-12-10 gecko gecko
============================

- Add preliminary 3.9(dev) support
- Handle 3.8-3.9 bytecode from 3.7ish

4.1.3 2019-11-17 JNC
====================

- Add magics for 3.5.8 and 3.5.9
- Python 3.0 tolerance
- Fix for unmarshaling Python 3.8 `str` from 3.2
- Pypy 3.3, 3.5, 3.6, and 3.6.9 magic numbers and support

4.1.2 2019-10-29 pre Halloween redux
====================================
- Python 3.8.0 magic changed
- More Pypy 3.6 tolerance
- Fixed DeprecationWarning; thanks to laike9m

4.1.1 2019-10-29 pre Halloween
==============================

- Fix unmarshaling 3.4+ object_ref bugs.
  A big thanks to Armin Rigo of the PyPy team.
- Add Pypy 3.6+ disassembly, e.g. pypy3.6-7.1.0 and pypy3.6-7.1.1
- Add Python 3.7.5, 2.7.16, 2.7.17rc1, and 2.7.15candidate1 as a valid releases
- convert unmarshal `if` .. `elif` code to a dictionary lookup with function entries
- Handle newer Python importlib - thanks to laike9m

4.1.0 2019-10-12 Stony Brook Ride
=================================

- Add early bytecodes: 1.0, 1.1, 1.2, and 1.6. Going off of pycdc bytecode since this is the only bytecode for these versions I know of
- Fix bug in Python 3.x decompiling 2.x that contains strings with non-ascii characters
- More generally, better handling of non-ascii Python 2 strings in both input and output in Python 3
- pypy 3.6-7.1.0 tolerance

4.0.4 2019-10-02
================

- Add most-recent 3.8 magic number
- Remove some 3.8 invalid escape warnings

4.0.3 2019-7-24  Mueller day
============================

- Support 3.8.0beta2; Code38 type with `posonlyargcount` field
- Add Python versions 3.4.10, 3.7.4 and 3.6.9
- `script` no longer works to install pydisasm; `entry_points` still works
- Add pypy 3.6 opcode formatting for `MAKE_FUNCTION` and `EXTENDED_ARG`
- Add `format_CALL_function` and use it or pypy36
- Start using "blacken" to reformat Python files

4.0.2 2019-6-12  Fleetwood at 65
================================

- To unicode strings in Python 2.x Try to convert to ascii, but if that doesn't work, leave as unicode. (x0ret)
- `BUILD_TUPLE_UNPACK_WITH_CALL` is a vararg


===============
4.0.1 2019-4-30
===============

- Add magics.IS_PYPY3 and correct `is_pypy()`
- disassemble PyPY3 versions correctly

4.0.0 2019-4-09
===============

- Expand is_jump_target to True, 'loop', False. This is the reason for the version bump
- Remove deprecated opcodes_pypyDD.py files. Use opcode_DDpypy instead.
- Fix bug in setting jump offset in wordcode (3.6+) relative jumps.
- Note that this works now in Python 3.8 (dev)
- Add 3.6{,.1}pypy version
- Dry opcodes 3.6 - 3.8

3.9.1 2019-3-28
===================

- Go over list of available Python 	versions
- 3.8.0alpha3 tolerance

3.9.0 2019-3-23
===================

- Correct instruction field `inst_size` in instructions that were build from `EXTENDED_OP` instructions
- Add `has_extended_arg` field in instruction


3.8.9 2018-10-20
====================

- Add magic for 3.6.8, 3.7.2
- Dropbox-hacked bytecode fixes, and some typos (jwilk@jwilk.net)
- Go over stack effects for vararg ops
- Fix CI for pypy
- Work around wheel munging

3.8.8 2018-10-20
=====================
- Add magic for 3.6.7, 3.7.1

3.8.7 2018-07-19
=====================

- Add magic for 3.6.5

3.8.6 2018-07-03 Independence-1
=======================================

- Remove stray print that got into op_imports

3.8.5 2018-07-02 Pre Independence
==========================================

- Add Python 3.7.0 magic and adjustments for its bytecode file reading
- Note Python 3.6.6 version

3.8.4 2018-06-12 When I'm 64
====================================

- Add Python 1.3 opcodes

3.8.3 2018-06-04 MF
=========================

- Fix Python 1.4 opcodes
- Fix misleading error message when failing to open a file
  (courtesy of jeffenstein)

3.8.2 2018-05-18 Paper Tiger
===================================

- Add 2.7.15rc1/candidate1
- Add Python 1.4 opcodes

3.8.1 2018-04-16
====================

- Correct classification of CALL_METHOD
- Add 3.6.5 and 3.7.0beta{2,3}
- Start supporting 3.7

3.8.0 2018-04-04
=====================

- Track 3.7 magic numbers, and interim releases
- a number of varargs opcodes introduced in 3.5 were not marked as such

3.7.0  2018-03-7
====================

License is GPL2.0 only now

- Make it work on bigendian machines
- Add canonic versions up to 3.4.8 and 3.5.5

3.6.11  2018-02-9 pycon2018.co
======================================

- Add version 3.5.5 to canonic_versions

3.6.10 2018-02-3
=====================


- Handle pypy in str2float
- Accomodate broken or incomplete "import platform"
- Pin Hypothesis to 3.0.0 - it has been broken after 3.0.0

3.6.9 2018-01-21
=====================

- Correct improper 3.4.4 setting

3.6.8 2018-01-21
=====================

- Add 3.4.4
- Fix a small bug in load.py
- improve unpack_opargs_wordcode

3.6.7 2018-01-21
=====================

- Add 3.7.0alpha3
- Fix bug in disassembly of 3.6+ from 2.x

3.6.6 2018-01-19
=====================

- Fix a bug in py_str2float for handling 3-place version number
- pydisasm: handle --version properly and invalid files better
- test_pyenvlib.py: can now test >= 3.5.0 (if not Pypy)

3.6.5 2018-01-18
=====================

- Go over 3.5 and 3.6 magics
- test_pyenvlib.py pick up acceptable python versions from
  xdis.magics rather than hardcode it in.

3.6.4 2018-01-08 Samish

- Update magics for 3.3.7, 3.6.4, 3.5.3, and 3.5.4

3.6.3 2017-12-09 Dr. Gecko
=====================

- Add pydisasm --header/--no-header
  option --header shows just the module-level header information
- Add magic.magicint2version
  In this dictionary, the key is an magic integer, e.g. 62211,
  and the value is its canonic versions string, e.g. '2.7'

3.6.2 2017-12-02

- Add canonic 3.2, 3.2a2, in op_imports
- Handle {-,}nan and {-,}inf in bytecode print attributes

3.6.1 2017-11-10
=====================

- Improve --asm option: disambiguate code objects with the same co_name
- Update canonic versions 3.6.3, 3.5.4, etc.
- "std" API now uses get_opcode_module rather than get_opcode()
- Add function extended_arg_val and use it in unpack_opargs_bytecode()
- str2version(): canonicalize version before float
- str2float(): We now at least detect inter-python version magic changes and
  can return something like 3.54 for 3.5.4  This assumes there never will be a 3.51

3.6.0 2017-09-25
=====================

- StdApi now uses std functions and constants from the
  correctly generated opc rather than the standard dis module (moagstar)
- Improve accuracy of opcode stack effects; classify opcodes more correctly
- Regularize opcode names: pypy is at the end now
- Correct writing Python3 bytecode from Python2 and Python2 bytecode from Python 3
- Add function to load from file object
- Add EXTENDED_ARG_SHIFT the number of bit positions EXTENDED_ARGS shifts
  This varies depending on where we are with respect to Python 3.6; similarly
  add ARG_MAX_VALUE, the maixumim integer value an operand field can have before
  needing EXTENDED_ARGS
- add unpack_opargs_bytecode which is similar to unpack_opargs_wordcode of 3.6
  This probably fixes a long-standing but little-noticed bug in Python 2.x disassembly
- cross version compatability bug fixed in code2num()
- Mark NOFOLOW opcodes (RETURN, RAISE)
- Mark conditional opcodes (POP_JUMP_IF...)
- Add len() and getitem() to code types code types to mimic Python3 behavior
- More tests; add appveyor CI testing

3.5.5 2017-08-31
=====================

- Add 3.7 opcodes
- Add optional file parameter on load_file
- add functions code_has_star_arg and code_has_star_star_arg (from uncompyle6)

3.5.4 2017-08-15
=====================

- Add internal switch in findlabels() to show multiple offsets for a
  given line.  This is turned on in pydisasm --xasm mode. Otherwise it
  is off. Sme  programs make use of findlinstart's somewhat misleading
  behavior

- Add methods for selecting from sys.version_info to the right opcode
  module, or canonic Python string or floating-point number.

- Add a notion of a canonic Python version.

- Add magic values for pyston and Jython.

- Some pyston tolerance. More is needed though.


3.5.3 2017-08-12
=====================

Showing all line number bolixes uncompyle6 and the trepan debuggers,
so nuke that for now.

However we show the full deal in pydisasm for asm format.  Here it is imporant since we recreate the line number table based on information
given in the instructions.  We could and probably should allow showing all of the line number in the default format as well.  Underneath there is a parameter to control that.

* Add pypy 3.5.3 magic number


3.5.2 2017-08-09
=====================

- magic to opcode for all known versions we handle
- simpiler import access to opcodes modules
- magic lookup for Python 3.3 is probably more correct more often

3.5.1 2017-07-14
=====================

Overall: Better xasm support, pydisasm improvements

- Was picking up wrong findlabels and findlinestarts in Python 3.5
- Add ARG_MAX_VALUE: the largest operand value before needing EXTENDED_ARG
- Allow lnotab as a dict before code freeze
- pydisasm: don't show Freevars more than once. Do show varnames,
  the combined positional + local vars
- change cmp_op values so they don't have an embedded space
  this helps xasm tokenization of COMPARE_OP's operand
- --asm option fixes
- a frozenset is more appropriate for opcode sets

3.5.0 2017-07-08
=====================

Overall: Support for bytecode assembler (xasm), Better 3.4-3.6 support

- Add --xasm option to pydisasm. This will output a disassembly
  suitable for an assembler, specifically xasm.
- Add magic lookup for 3.4.[0..6] 3.5.[0..2] and 3.6.[0..1]
- Add magic lookup for base versions, e.g. 2.7 or 3.4
- Trap ill-formed python bytecode bettern
- Show timestamp in pydisasm output as it is stored
- Add "optype" field to Instructions. Derived from the has_xxx lists
- Marshaling for Python2 and Python3 code when using cross-version
  is aware that the format for the other type is different.
- Add opcode sets corresponding to the the opcode has_xxx lists.
- Document Code2 and Code3 a little better
- add Code2Compat and Code3Compat to make cross-version Code creation
  easier
- add Code2/Code3 freeze() routine which convert from from a
  programmer-friendly code object to one compacted and ready for
  marshalling or use.
- Correct Python 3.6+ findlinestarts() and findlabels() methods
- Fix _unpack_opargs_wordcode in 3.6
- DRY opcodes more
- Add marshal types that have appeared since Python 3.4 and
  start to implement. More work is needed here.


3.4.0 2017-06-25
=====================

- Add functions in xdis.bytecode:
  has_argument()_, next_offset(), and op_size() functions to
- work with fixed (3.6+) and variable-length (pre 3.6) instructions
- Add magic for pypy3.5

3.3.1 2017-05-18 - Lewis
=====================

Python 3.6 bugs/features
- Fix bug in handling operand of opcode after EXTENDED_ARG
- A general mechanism to handle formatting of instruction operands and use
  that on Python 3.6+ opcode MAKE_FUNCTION FORMAT_VALUE
- Add missing SETUP_ASYNC_WITH opcode
- Test 3.6 on Travis CI
- compile() return value, "code" no longer has a len. Use "code.co_code"

3.3.0 2017-03-18
=====================

- Start supporting Python 3.x dis API functions
  This is largely due to Daniel Bradburn (moagstar)
- Expanded tests, bug fixes, and bug fixes for various versions of Python
  This is largely due to Kirill Spitsyn

3.2.4 2016-12-16
=====================

- add magic for 3.6rc
- Fix Python 3.6 disaseembly of CALL_FUNCTION_EX
- Make magic string values unique
- Note we can now handle Python 2.4 and 2.5

3.2.3 2016-11-6
=====================

- Correct Python 3.0 bytecodes
- Go over other opcodes and add stack manipulation entries.  For
  example, for LIST_APPEND.

3.2.2 2016-11-02
=====================

- Distrbute COPYING.txt
- Correct pypy 3.2 bytecode
- Start adding stack use on opcodes for Python 3.x

- add stack use for Python 2 and Python3 opcodes (incomplete)

3.2.1 2016-10-30
=====================

- Tag pypy 2.6 and 2.7 LOOKUP_METHOD properly
  (bug introduced in 3.2.0. Thanks to alexwlchan of the hypothesis team.)
- Clarification of EXTENDED_ARG in 3.0 and 3.1
- disassemble output size indicates bytes explicitly

3.2.0 2016-10-25
=====================

- Python 3.1 EXTENDED_ARG opcode bug fix
- Python 3.0 opcode fixes
- DRY opcode files
- start noting stack-modification attributes on opcodes and
  use for Python 2.4-2.7
- Remove hasAgumentExtended. It's not used.
- Update Python 3.6 opcodes
- Add magic number for Python 3.6.0b2
- On disassembly Python 3.6 no longer knows what's up in CALL_FUNCTION
- Add Python 2.1 and 3.1 bytecode tests
- Add list2bytecode() and write_bytecode_file() -
  First steps in handling bytecode assembly
- Change licence to GPL 2.0

3.1.0 2016-10-15
=====================

- expose findlabels, and findlinestarts,
- add offset2line routine to give line number for a given offset
- clean up requirements.txt and setup.py

3.0.2 2016-10-09
=====================

- Fix Python 1.5 disassembly bugs
- Add Python 1.3 and 1.4 magics

3.0.1 2016-10-09
=====================

- botched classification of FOR_LOOP in Python 1.5

3.0.0 2016-10-09
=====================

- load_module returns source-code size now.
  This is incompatible with previous (2.x) versions

- add parameter in load_module to omit parsing code,
  just other info (source-code-size, timestamp, magic, etc)

- Disassemble 1.5 bytecodes and test

- fix some Python 1.5 and 2.0 bytecode bugs

2.3.2 2016-10-06
=====================

- Start adding Python 1.5 and 2.0, and 2.1 opcodes
- Disassemble dropbox 2.5
- correct pydisasm name in --help

2.3.1 2016-09-11
=====================

- Add Dropbox magic numbers.
  Decode dropbox's 2.5 bytecode via code (on Python 2.x)
  from https://github.com/rumpeltux/dropboxdec

2.2.3 2016-08-29
=====================

- Fix Python 3.1 opcode bugs

2.2.2 2016-08-26
=====================

- Add Python 3.6 opcodes since 3.6.0.a1
- magics.versions has more detailed version information, e.g. 62121 is 2.5c1
- Add format conversion type (!r, !s, !a) in 3.6 FORMAT_VALUE attribute
- We no longer support Python 3.6.0a1 but only 3.6.0a3
- Update opcode history

2.2.1 2016-08-14
=====================

- Fix 3.6 arg parsing in wordcode
- PyPy 2.7 LOAD_ATTR wasn't marked as a name op
- add python_version attribute to opc
- Doc corrections

2.2.0 2016-08-05
=====================

- Add Python 2.2 bytecodes
- Show Python magic number in disassembly output
- Show compile flags in hex and in proper bit order

2.1.0 2016-07-26
=====================

- better opcode classification hasvargs for non-function calls, e.g. BUILD
- Support 3.6 wordcode

2.0.3 2016-07-26
=====================

- Small instruction print change

2.0.2 2016-07-25
=====================

- Fix some PyPy op classification bugs

2.0.1 2016-07-24
=====================

- PyPy bug fixes. (More probably to come.)
  * pypy 3.x opcodes need to be their own thing
  * classify LOOKUP_METHOD and CALL_METHOD
    (probably will need to classify others too)
  * some PyPy testing tolerance

2.0.0 2016-07-24
=====================

- Support PyPy 2.x and 3.x
  * load() now returns whether we've loaded PyPy. This is an incompatible change
  * added is_pypy(magic_int)

- Support Python 3.6

- Remove uncompyle6's JA and JF: Use standard JUMP_ABSOLUTE and
  JUMP_FORWARD.

- Instructions store whether they have an argument

1.1.7 2016-07-09
=====================

- Fix bug in 2.4 complex type unmarshalling

1.1.6 2016-07-08
=====================

- Fix More Python 2.4 bugs

1.1.5 2016-07-08
=====================

- Add Python 2.4 jrel, jabs sets

1.1.4 2016-07-07
=====================

-  Correct bad python 3.3 magic number

1.1.3 2016-06-27
=====================

- Bug - Python < 2.7 JUMP_IF_{TRUE,FALSE} are
  relative jumps, not absolute

1.1.2 2016-06-24
=====================

- Bug - Python 2.4-2.6 LIST_APPEND doesn't take an extended arg

1.1.1 2016-06-3
=====================

- opcode 2.3 fixes

1.1.0 2016-05-31 Mom
=====================

- Expose needed opcode values and bug fixes
- drop support for running on Python 2.5

1.0.5 2016-05-29
=====================

For Python 2.3-2.5 add pseudo opcodes PJIF PJIT JA
This simplifies code in cross-version tools like uncompyle6

1.0.4 2016-05-28
=====================

Small omissions found by uncompyle6

- export findlinestarts
- correct pydisassemble.py imports
- add 2.4, 2.5 hasArgumentExtended
- add hasjrel, and hasjabs
- Add JUMP_OPs and JPIF, JPIT, JA, JF

1.0.1-1.0.3 2016-05-27
=====================

Minor fixes

- small bugs and make more usable in uncompyle6

1.0.0 2016-05-26 First release
=====================

- Reduce redundancy in opcodes
- Use 3.5.1 disassembly format
- Start to roll in PYPY marshal routines
- support PYPY and be able to run under
  Python 2.5 - 3.5 with opcodes going back to 2.3

See uncompyle6 for past releases/history
