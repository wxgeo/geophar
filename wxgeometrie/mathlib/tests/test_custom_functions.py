# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from pytest import XFAIL

from sympy import exp, sqrt, Symbol

#from tools.testlib import *
from wxgeometrie.mathlib.custom_functions import resoudre, positif, ensemble_definition


#VERBOSE = False


def assertEqual(x, y):
    if x != y:
        print "ERREUR:", repr(x), "!=", repr(y)
    assert(x == y)

def assert_resoudre(x, y):
    assertEqual(str(resoudre(x)), y)

def assert_positif(x, y):
    assertEqual(unicode(positif(x)), y)

def assert_ens_def(x, y):
    assertEqual(unicode(ensemble_definition(x)), y)

def test_resoudre():
    assert_resoudre("2*x=0", "{0}")
    assert_resoudre("2*x>0", u"]0;+oo[")
    assert_resoudre("(x>4 et x<7) ou (x/2-1>=3)", u"]4;7[U[8;+oo[")
    assert_resoudre("(2)*x>0", u"]0;+oo[")
    assert_resoudre("2*x+3>5*x-4 et 3*x+1>=4*x-4", u']-oo;7/3[')
    assert_resoudre("2*x+3*y=4 et 4*x-2*y=1", u"{x: 11/16, y: 7/8}")
    assert_resoudre("ln(x)<ln(-2*x+1)", "]0;1/3[")
    assert_resoudre("exp(x^2)-x^2-1>=0", "]-oo;+oo[")


def test_positif():
    x = Symbol("x")
    assert_positif(x**7, "[0;+oo[")
    assert_positif((x + 1)**5, "[-1;+oo[")
    assert_positif(sqrt(x + 1), "[-1;+oo[")
    assert_positif((x + 1)**6, "]-oo;+oo[")
    assert_positif(-x**2 - x, "[-1;0]")
    assert_positif(sqrt(5), "]-oo;+oo[")
    assert_positif((x - 1)/(x + 1), ']-oo;-1[U[1;+oo[')
    assert_positif(x*exp(3) - 1, '[exp(-3);+oo[')

@XFAIL
def test_positif2():
    x = Symbol("x")
    assert_positif(x - 1 + exp(x), "[0;+oo[")

def test_ensemble_definition():
    x = Symbol("x")
    assert_ens_def((2 - x)/(6 - 5*x + x**2), ']-oo;2[U]2;3[U]3;+oo[')
