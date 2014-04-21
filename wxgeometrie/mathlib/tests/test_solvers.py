# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from pytest import XFAIL

from sympy import exp, sqrt, Symbol

#from tools.testlib import *
from wxgeometrie.mathlib.solvers import resoudre, positif, ensemble_definition


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
    assert_resoudre(u"x*(sqrt(64-x^2))=32", "{4*sqrt(2)}")
    assert_resoudre('x - 1 + exp(x)>=0', '[0;+oo[')

def test_resoudre_abs():
    assert_resoudre('abs(2*x+3)-4>0', ']-oo;-7/2[U]1/2;+oo[')
    assert_resoudre('exp(abs(2*x+3))>3', ']-oo;-3/2 - ln(3)/2[U]-3/2 + ln(3)/2;+oo[')
    assert_resoudre('3*abs(2*x-7)-2*abs(5*x+2)>0', ']-25/4;17/16[')
    assert_resoudre('3*abs(2*x-7)-2*abs(5*x+2)+5*abs(x+4)-9>0', ']-oo;-4[U]-4;28/11[U]14;+oo[')

def test_resoudre_substitution():
    assert_resoudre('sqrt(x**2+3)-x**2+3>=0', '[-sqrt(6);sqrt(6)]')
    assert_resoudre('sqrt(x+3)+x-5>=0', '[-sqrt(33)/2 + 11/2;+oo[')

def test_resoudre_puissances():
    assert_resoudre('sqrt(x)>4', ']16;+oo[')
    assert_resoudre('x^2.3>4', ']2^(20/23);+oo[')
    assert_resoudre('-3*x^2.3>4', '{}')

def test_sqrt():
    assert_resoudre('x+sqrt(x)>4', ']-sqrt(17)/2 + 9/2;+oo[')
    assert_resoudre('sqrt(x^2-3)<=5', '[-2*sqrt(7);-sqrt(3)]U[sqrt(3);2*sqrt(7)]')
    assert_resoudre('sqrt(x+3)-sqrt(x**2-4)>=0', '[-sqrt(29)/2 + 1/2;-2]U[2;1/2 + sqrt(29)/2]')


def test_resoudre_floats():
    # pass (Geophar 12.08 revision 64f4bb42)
    assert_resoudre(u"0.5*exp(-0.5*x + 0.4)=0.5", "{4/5}")
    # fail (Geophar 12.08 revision 64f4bb42)
    assert_resoudre(u"exp(-0.5*x - 0.4)-1=0", "{-4/5}")

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

def test_positif2():
    x = Symbol("x")
    assert_positif(x - 1 + exp(x), "[0;+oo[")

def test_ensemble_definition():
    x = Symbol("x")
    assert_ens_def((2 - x)/(6 - 5*x + x**2), ']-oo;2[U]2;3[U]3;+oo[')

def test_issue_230():
    # 3 racines réelles pour le polynôme.
    assertEqual(str(resoudre("x^3+7*x^2-5*x-4==0").evalf()),
          '{-7.58937000406433 ; -0.48882774214088 ; 1.07819774620521}')
