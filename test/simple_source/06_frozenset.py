# Bug from Python 3.3 _markupbase.py cross compilation
# error in unmarshaling a frozenset
import sys
if sys.argv[0] in {"attlist", "linktype", "link", "element"}:
    print("Yep")
