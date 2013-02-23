# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from wxgeometrie.mathlib.custom_objects import Decim
from sympy import Symbol, Rational

x = Symbol('x')


def test_Decim():
    assert repr(Decim(1, 2)*x + Decim(1, 5)) == '0.5*x + 0.2'
    assert repr(Decim(1, 2)*Rational(1, 5)) == '0.1'