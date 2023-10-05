# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

import math
import numpy
import sympy
from wxgeometrie.mathlib.universal_functions import asin, acos, atan

import wx_unittest

x = sympy.Symbol('x')

class MathlibTest(wx_unittest.TestCase):
    def test_trigo(self):
        # Vérifie que arcsin est correctement implémenté (appel à math, numpy ou
        # sympy suivant le type d'objet).
        self.assertAlmostEqual(asin(.2), math.asin(.2))
        a, b, c = asin([.2, .3, .4])
        d, e, f = numpy.arcsin([.2, .3, .4])
        self.assertAlmostEqual(a, d)
        self.assertAlmostEqual(b, e)
        self.assertAlmostEqual(c, f)
        self.assertEqual(asin(x + 1), sympy.asin(x + 1))
        # Vérifie que arccos est correctement implémenté (appel à math, numpy ou
        # sympy suivant le type d'objet).
        self.assertAlmostEqual(acos(.2), math.acos(.2))
        a, b, c = acos([.2, .3, .4])
        d, e, f = numpy.arccos([.2, .3, .4])
        self.assertAlmostEqual(a, d)
        self.assertAlmostEqual(b, e)
        self.assertAlmostEqual(c, f)
        self.assertEqual(acos(x + 1), sympy.acos(x + 1))
        # Vérifie que arctan est correctement implémenté (appel à math, numpy ou
        # sympy suivant le type d'objet).
        self.assertAlmostEqual(atan(.2), math.atan(.2))
        a, b, c = atan([.2, .3, .4])
        d, e, f = numpy.arctan([.2, .3, .4])
        self.assertAlmostEqual(a, d)
        self.assertAlmostEqual(b, e)
        self.assertAlmostEqual(c, f)
        self.assertEqual(atan(x + 1), sympy.atan(x + 1))
