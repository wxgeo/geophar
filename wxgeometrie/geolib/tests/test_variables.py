# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

from random import random, randint

import wx_unittest
from wxgeometrie.geolib import Variable, Formule, XMinVar, XMaxVar, YMinVar, YMaxVar, Feuille
from wxgeometrie.mathlib.parsers import mathtext_parser

class TestGeolib(wx_unittest.TestCase):
    # Ce test était surtout utile quand les variables supportaient les opérations mathématiques.
    def test_operations(self):
        for i in range(10):
            a = randint(0,50) - randint(0,50)
            b = randint(0,50) - randint(0,50)
            if i >= 5:
                a += random()
                b += random()
            u = Variable(a)
            v = Variable(b)
            # Test opérations :
            if i < 5:
                self.assertEqual(u.val+v.val, a+b)
                self.assertEqual(u.val-v.val, a-b)
                self.assertEqual(u.val*v.val, a*b)
                if a !=0:
                    self.assertEqual(u.val**v.val, a**b)
                if  b != 0:
                    self.assertEqual(u.val/v.val, a/b)
                    self.assertEqual(u.val//v.val, a//b)
                    self.assertEqual(u.val%v.val, a%b)
            else:
                self.assertAlmostEqual(u.val+v.val, a+b)
                self.assertAlmostEqual(u.val-v.val, a-b)
                self.assertAlmostEqual(u.val*v.val, a*b)
                if a != 0:
                    self.assertAlmostEqual(abs(u.val)**v.val, abs(a)**b)
           # Test assignations :
            u.val += v.val
            a += b
            self.assertEqual(u.val, a)
            u.val *= v.val
            a *= b
            self.assertEqual(u.val, a)

    # Ce test était surtout utile quand les variables supportaient les opérations mathématiques.
    def test_erreurs_mathematiques(self):
        u = Variable(randint(0,50) - randint(0,50)+random())
        def diviser(x,  y):
            return x/y
        self.assertRaises(ZeroDivisionError,  diviser,  u.val,  0)
        def puissance(x,  y):
            return x**y
        self.assertRaises(OverflowError,
                          puissance,  Variable(25.17).val,  10000)

    def test_simple_compose(self):
        self.assertEqual(Variable(5)._type, "simple")
        self.assertEqual(Variable("-5.3")._type, "simple")
        self.assertEqual(Variable("a")._type, "compose")

    def test_parser_matplotlib(self):
        c = Formule._caractere_erreur
        c_math = '$%s$' %c
        self.assertTrue(mathtext_parser(c))
        self.assertTrue(mathtext_parser(c_math))


    def test_XMinVar(self):
        f = Feuille()
        f.fenetre = -1, 1, -2, 2
        f.objets.xm = XMinVar()
        self.assertEqual(f.objets.xm, -1)

    def test_XMaxVar(self):
        f = Feuille()
        f.fenetre = -1, 1, -2, 2
        f.objets.xm = XMaxVar()
        self.assertEqual(f.objets.xm, 1)

    def test_YMinVar(self):
        f = Feuille()
        f.fenetre = -1, 1, -2, 2
        f.objets.ym = YMinVar()
        self.assertEqual(f.objets.ym, -2)

    def test_YMaxVar(self):
        f = Feuille()
        f.fenetre = -1, 1, -2, 2
        f.objets.ym = YMaxVar()
        self.assertEqual(f.objets.ym, 2)
