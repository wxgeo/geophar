# -*- coding: utf-8 -*-

from random import random

from tools.testlib import assertAlmostEqual, assertEqual, randint, assertRaises
from wxgeometrie.geolib import Variable, Formule, XMinVar, XMaxVar, YMinVar, YMaxVar, Feuille
from wxgeometrie.mathlib.parsers import mathtext_parser


# Ce test était surtout utile quand les variables supportaient les opérations mathématiques.
def test_operations():
    for i in range(10):
        a = randint(50) - randint(50)
        b = randint(50) - randint(50)
        if i >= 5:
            a += random()
            b += random()
        u = Variable(a)
        v = Variable(b)
        # Test opérations :
        if i < 5:
            assertEqual(u.val+v.val, a+b)
            assertEqual(u.val-v.val, a-b)
            assertEqual(u.val*v.val, a*b)
            if a !=0:
                assertEqual(u.val**v.val, a**b)
            if  b != 0:
                assertEqual(u.val/v.val, a/b)
                assertEqual(u.val//v.val, a//b)
                assertEqual(u.val%v.val, a%b)
        else:
            assertAlmostEqual(u.val+v.val, a+b)
            assertAlmostEqual(u.val-v.val, a-b)
            assertAlmostEqual(u.val*v.val, a*b)
            if a != 0:
                assertAlmostEqual(abs(u.val)**v.val, abs(a)**b)
       # Test assignations :
        u.val += v.val
        a += b
        assertEqual(u.val, a)
        u.val *= v.val
        a *= b
        assertEqual(u.val, a)

# Ce test était surtout utile quand les variables supportaient les opérations mathématiques.
def test_erreurs_mathematiques():
    u = Variable(randint(50) - randint(50)+random())
    def diviser(x,  y):
        return x/y
    assertRaises(ZeroDivisionError,  diviser,  u.val,  0)
    def puissance(x,  y):
        return x**y
    assertRaises(OverflowError,  puissance,  Variable(25.17).val,  10000)

def test_simple_compose():
    assert(Variable(5)._type == "simple")
    assert(Variable("-5.3")._type == "simple")
    assert(Variable("a")._type == "compose")

def test_parser_matplotlib():
    c = Formule._caractere_erreur
    c_math = '$%s$' %c
    assert(mathtext_parser(c))
    assert(mathtext_parser(c_math))


def test_XMinVar():
    f = Feuille()
    f.fenetre = -1, 1, -2, 2
    f.objets.xm = XMinVar()
    assert f.objets.xm == -1

def test_XMaxVar():
    f = Feuille()
    f.fenetre = -1, 1, -2, 2
    f.objets.xm = XMaxVar()
    assert f.objets.xm == 1

def test_YMinVar():
    f = Feuille()
    f.fenetre = -1, 1, -2, 2
    f.objets.ym = YMinVar()
    assert f.objets.ym == -2

def test_YMaxVar():
    f = Feuille()
    f.fenetre = -1, 1, -2, 2
    f.objets.ym = YMaxVar()
    assert f.objets.ym == 2
