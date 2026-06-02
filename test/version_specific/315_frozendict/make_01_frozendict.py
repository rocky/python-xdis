# Generates a frozendict object to test the unmarshal.py implementation for frozen dicts.
#
# Justification: Python 3.15 does not currently statically optimize frozendict() invocations
# because users can name any function `frozendict`. As a result, py_compile can never emit
# TYPE_FROZENDICT, so manually inserting the frozendict object is the only way to test this
# functionality currently.
#
# This must be run in Python 3.15 to correctly generate the pyc file used for testing.

import importlib.util
import marshal
import struct
import time

# Compile a simple dummy script.
source = "print('Testing frozendict cross-version support!')"
code_obj = compile(source, "01_frozendict.py", "exec")

# Create a native 3.15 frozendict. "frozendict" is only
# available starting only with Python 3.15
fd = frozendict({"hello": "cross-version-world"})  # NOQA

# Inject it into the code object's constants
# We use the `.replace()` method (added in Python 3.8) to make a new code obj
new_consts = code_obj.co_consts + (fd,)
new_code_obj = code_obj.replace(co_consts=new_consts)

# Write the .pyc file manually.
magic = importlib.util.MAGIC_NUMBER
bitfield = 0
timestamp = int(time.time())
file_size = len(source)

with open("01_frozendict.pyc", "wb") as f:
    # Write the 16-byte header (Magic, Bitfield, Timestamp, Size).
    f.write(magic)
    f.write(struct.pack("<LLL", bitfield, timestamp, file_size))

    # Dump the injected code object!
    marshal.dump(new_code_obj, f)

print("Generated 01_frozendict.pyc successfully!")
