# -*- coding: iso-8859-1 -*-

from random import random, randint as _randint
from os.path import split, realpath, abspath
import sys

from wxgeometrie.param import tolerance as EPSILON

_module_path = split(realpath(sys._getframe().f_code.co_filename))[0]
ROOTDIR = abspath(_module_path + '/..') # /.../nom_du_projet/
WXGEODIR = ROOTDIR + '/wxgeometrie'

def randint(a, b = None):
    if b is None:
        b = a
        a = 0
    return _randint(a, b)

def rand():
    return randint(50) - randint(50) + random()

def assertAlmostEqual(x, y):
    if type(x) == type(y) and isinstance(x, (tuple, list)):
        for x_elt, y_elt in zip(x, y):
            assertAlmostEqual(x_elt, y_elt)
    else:
        TEST = abs(y - x) < EPSILON
        if not TEST:
            print('''
--------------
 *** FAIL ***
-> Output:
%s
-> Expected:
%s
--------------
''' %(repr(x), repr(y)))
            assert TEST

def assertNotAlmostEqual(x, y):
    # TODO: define test for tuple
    TEST = abs(y - x) > EPSILON
    if not TEST:
        print(x,  "==",  y)
    assert TEST

def _yellow(s):
    return '\033[0;33m' + s + '\033[0m'

def assertEqual(x, y, additionnal_msg=None, _raise=True):
    if x != y:
        rx = repr(x)
        ry = repr(y)
        if isinstance(x, str) and isinstance(y, str):
            for i in range(min(len(rx), len(ry))):
                if rx[i] != ry[i]:
                    break
            ry = ry[:i] + _yellow(ry[i:])

        print('''
--------------
 *** FAIL ***
-> Output:
%s
-> Expected:
%s
--------------''' %(rx, ry))
        if additionnal_msg is not None:
            print(additionnal_msg)
        if _raise:
            assert False
        return False
    return True

assertEq = assertEqual

def assertEqualAny(result, list_of_acceptable_results, _raise=True):
    l = list_of_acceptable_results
    if all((result != r) for r in l):
        msg = ('Other accepted results: %s' % l[1:] if len(l) > 1 else None)
        return assertEqual(result, l[0], additionnal_msg=msg, _raise=_raise)
    return True

def assertRaises(error, f, *args, **kw):
    try:
        f(*args, **kw)
    except Exception as e:
        assert type(e) == error
    else:
        raise AssertionError('%s should be raised.' %type(e).__name__)
