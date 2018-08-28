# -*- coding: utf-8 -*-

from wxgeometrie.mathlib.custom_objects import Decim
from sympy import Symbol, Rational, S

from tools.testlib import assertEqual

x = Symbol('x')


def test_Decim():
    expr = S.One*Decim('0.3')
    assert isinstance(expr,  Decim), type(expr)
    expr = Decim('0.3')*x
    assert isinstance(expr.args[0],  Decim), type(expr.args[0])
    assertEqual(repr(Decim(1, 2)*x + Decim(1, 5)), '0.5*x + 0.2')
    assertEqual(repr(Decim(1, 2)*Rational(1, 5)), '0.1')
