# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

from wxgeometrie.mathlib.custom_objects import Decim
from sympy import Symbol, Rational, S

import tools.unittest

x = Symbol('x')

class MathlibTest(tools.unittest.TestCase):

    def test_Decim(self):
        expr = S.One*Decim('0.3')
        self.assertIsInstance(expr,  Decim), type(expr)
        expr = Decim('0.3')*x
        self.assertIsInstance(expr.args[0],  Decim), type(expr.args[0])
        self.assertEqual(repr(Decim(1, 2)*x + Decim(1, 5)), '0.5*x + 0.2')
        self.assertEqual(repr(Decim(1, 2)*Rational(1, 5)), '0.1')
