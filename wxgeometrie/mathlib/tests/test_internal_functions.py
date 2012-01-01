# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from wxgeometrie.mathlib.internal_functions import poly_factor
from sympy import Symbol, sqrt, S, I as i, expand, Integer

x = Symbol('x')


def assert_factor(poly, *args, **kw):
    def convert(obj):
        if isinstance(obj, int):
            return Integer(obj)
        return obj
    var = kw.get("var", x)
    facteurs = poly_factor(poly,  var)
    poly_args = facteurs.args
    s = set()
    s.update(convert(arg) for arg in poly_args)
    s.update(convert(-arg) for arg in poly_args)
    TEST1 = set(convert(arg) for arg in args).issubset(s)
    if not TEST1:
        print "ERREUR: ", set(args), " n'est pas inclus dans ",  s
        print "Difference: ", set(args).difference(s)
        print [type(obj) for obj in set(args).difference(s)]
    TEST2 = (expand(facteurs) == expand(poly))
    if not TEST2:
        print "ERREUR: ", expand(facteurs), " != ", expand(poly)
    assert(TEST1)
    assert(TEST2)

def test_factor():
    assert_factor(x**2 - 1, x-1, x+1)
    assert_factor(x**2 - 2, x - sqrt(2), x + sqrt(2))
    assert_factor(2*x**2 - 2, 2, x-1, x+1)
    assert_factor(1 + 2*x + 2*x**2 + x**3, x+1, x**2+x+1)
    assert_factor(2*x, 2, x)
    # assert_factor(x**2-i, x+sqrt(2)/2+i*sqrt(2)/2, x-sqrt(2)/2-i*sqrt(2)/2)
    assert_factor(x**2-i, x + (-1)**(S(1)/4), x - (-1)**(S(1)/4))
