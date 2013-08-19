# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

import math
import numpy
import sympy
from tools.testlib import assertAlmostEqual, assertEqual
from wxgeometrie.mathlib.universal_functions import asin, acos, atan

x = sympy.Symbol('x')

def test_trigo():
    # Vérifie que arcsin est correctement implémenté (appel à math, numpy ou
    # sympy suivant le type d'objet).
    assertAlmostEqual(asin(.2), math.asin(.2))
    a, b, c = asin([.2, .3, .4])
    d, e, f = numpy.arcsin([.2, .3, .4])
    assertAlmostEqual(a, d)
    assertAlmostEqual(b, e)
    assertAlmostEqual(c, f)
    assertEqual(asin(x + 1), sympy.asin(x + 1))
    # Vérifie que arccos est correctement implémenté (appel à math, numpy ou
    # sympy suivant le type d'objet).
    assertAlmostEqual(acos(.2), math.acos(.2))
    a, b, c = acos([.2, .3, .4])
    d, e, f = numpy.arccos([.2, .3, .4])
    assertAlmostEqual(a, d)
    assertAlmostEqual(b, e)
    assertAlmostEqual(c, f)
    assertEqual(acos(x + 1), sympy.acos(x + 1))
    # Vérifie que arctan est correctement implémenté (appel à math, numpy ou
    # sympy suivant le type d'objet).
    assertAlmostEqual(atan(.2), math.atan(.2))
    a, b, c = atan([.2, .3, .4])
    d, e, f = numpy.arctan([.2, .3, .4])
    assertAlmostEqual(a, d)
    assertAlmostEqual(b, e)
    assertAlmostEqual(c, f)
    assertEqual(atan(x + 1), sympy.atan(x + 1))
