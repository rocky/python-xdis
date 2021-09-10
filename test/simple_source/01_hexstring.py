#!#/usr/bin/env python
# -*- coding: latin-1 -*-
# Bug was in handling Python 2.x strings in Python 3.x which uses
# converst from bytes.
# This program is RUNNABLE!
def f(x):
    return x + "\x7e\x80\x81" + "\x82"

assert f("abc") == "abc~€‚"
