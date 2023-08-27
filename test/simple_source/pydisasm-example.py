"""An example to show off Python's extended disassembly.
Run: pydisasm -F extended-bytes site-example.pyc
"""
import sys
from sys import version_info

print(sys.version)
print(len(version_info))
major = sys.version_info[0]
power_of_two = major & (major - 1)
if power_of_two in (2, 4):
    print("Is small power of two")
