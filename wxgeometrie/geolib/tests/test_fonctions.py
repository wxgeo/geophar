# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

import wx_unittest, unittest
from wxgeometrie.geolib import Fonction, Feuille

_VAL0 = -5.156557933

class GeolibTest(wx_unittest.TestCase):

    @unittest.expectedFailure
    def test_Fonction(self):
        "Test sans feuille."
        g = Fonction('2x+7')
        self.assertEqual(g(17), 41)
        # La fonction n'est compilée que s'il y a une feuille.
        # -> à tester lorsque chaque objet aura un feuille par défaut.


    def test_base(self):
        f = Feuille()
        H = f.objets.H = Fonction("2*t**3+5", variable = 't')
        self.assertAlmostEqual(H(_VAL0), 2*_VAL0**3+5)


    def test_reecriture(self):
        f = Feuille()
        H = f.objets.H = Fonction("2x^2+3x(1+x)", 'R')
        def h(x):
            return 2*x**2+3*x*(1+x)
        self.assertAlmostEqual(H(17), h(17))
        self.assertAlmostEqual(H(_VAL0), h(_VAL0))


    def test_variables(self):
        f = Feuille()
        o = f.objets
        a = o.a = 3
        b = o.b = 5
        g = o.g = Fonction("a*x+b")
        self.assertAlmostEqual(g(4), a*4+b)
        self.assertAlmostEqual(g(_VAL0), a*_VAL0+b)

    def test_intervalle(self):
        f = Feuille()
        o = f.objets
        g = o.g = Fonction('x^2+2x+1', ']0;5')
        self.assertEqual(g.style('extremites_cachees')[0][0].val, 5) # ([Variable(5)],)
        self.assertEqual(g.ensemble, ']0;5[')

