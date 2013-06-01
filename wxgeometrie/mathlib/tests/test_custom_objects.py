# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from wxgeometrie.mathlib.custom_objects import Decim
from sympy import Symbol, Rational

from tools.testlib import assertEqual

x = Symbol('x')


def test_Decim():
    assertEqual(repr(Decim(1, 2)*x + Decim(1, 5)), '0.5*x + 0.2')
    assertEqual(repr(Decim(1, 2)*Rational(1, 5)), '0.1')