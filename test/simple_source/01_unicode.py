# Bug from Python 3.5 heapq.py
# Unicode cidilla to ASCII messed up.

# Should see:
#   Constants:
#      0: 'François Pinard'
# for Python 3.0+ nad
#   Constants:
#      0: 'Francois Pinard'
# for Python < 3.0

__about__ = """François Pinard"""
