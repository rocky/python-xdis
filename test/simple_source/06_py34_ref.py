# Bug in 3.4+ handling of references.
# Should see:
# Constants:
#    0: '\n'
#    1: 'normal'
#    2: '"""string"""'
#    3: 'string'
#    4: "'string'"
#    5: 'stderr'
#    6: None
#    7: ('\n', 'normal')
#    8: ('"""string"""', 'string')
#    9: ("'string'", 'string')
#   10: ('stderr', 'stderr')
#   11: ('\n', 'normal')
#   12: (('\n', 'normal'), ('"""string"""', 'string'), ("'string'", 'string'), ('stderr', 'stderr'), ('\n', 'normal'))

# Before 3.4 constant 12 does not appear.

textAndTags=(
    ('\n', 'normal'),
    ('"""string"""', 'string'),
    ("'string'", 'string'),
    ('stderr', 'stderr'),
    ('\n', 'normal'))
