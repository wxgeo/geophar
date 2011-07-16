# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from random import random

from tools.testlib import assertAlmostEqual, assertEqual, randint, assertRaises
from wxgeometrie.geolib import Variable, Formule
from wxgeometrie.pylib import mathtext_parser


def test_operations():
    for i in xrange(10):
        a = randint(50) - randint(50)
        b = randint(50) - randint(50)
        if i >= 5:
            a += random()
            b += random()
        u = Variable(a)
        v = Variable(b)
        # Test opérations :
        if i < 5:
            assertEqual(u+v, a+b)
            assertEqual(u-v, a-b)
            assertEqual(u*v, a*b)
            if a !=0:
                assertEqual(u**v, a**b)
            if  b != 0:
                assertEqual(u/v, a/b)
                assertEqual(u//v, a//b)
                assertEqual(u%v, a%b)
        else:
            assertAlmostEqual(u+v, a+b)
            assertAlmostEqual(u-v, a-b)
            assertAlmostEqual(u*v, a*b)
            if a != 0:
                assertAlmostEqual(abs(u)**v, abs(a)**b)
       # Test assignations :
        u += v
        a += b
        assertEqual(u, a)
        u *= v
        a *= b
        assertEqual(u, a)

def test_erreurs_mathematiques():
    u = Variable(randint(50) - randint(50)+random())
    def diviser(x,  y):
        return x/y
    assertRaises(ZeroDivisionError,  diviser,  u,  0)
    def puissance(x,  y):
        return x**y
    assertRaises(OverflowError,  puissance,  Variable(25.17),  10000)

def test_simple_compose():
    assert(Variable(5)._type == "simple")
    assert(Variable("-5.3")._type == "simple")
    assert(Variable("a")._type == "compose")

def test_parser_matplotlib():
    c = Formule._caractere_erreur
    c_math = '$%s$' %c
    assert(mathtext_parser(c))
    assert(mathtext_parser(c_math))
