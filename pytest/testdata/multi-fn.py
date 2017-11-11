#!/usr/bin/env python
# a = lambda x: x + 1
# b = lambda y: y + 2
def bar():
    def baz():
        return 3
    return baz()
def baz():
    def bar():
        return 4
    return bar()
# print(a(0))
# print(b(0))
print(bar())
print(baz())
