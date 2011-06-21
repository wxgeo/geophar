# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

import os
import mathlib

from tools.testlib import *
import sympy

# Teste que certains bugs de sympy sont bien ou résolus, ou temporairement patchés



def test_sympy():
    oo = sympy.oo
    x = sympy.Symbol('x', real = True)
    assert -oo < oo
    assert not(-1.5 < -oo)
    assert (1-sympy.exp(x)).is_negative is None
    assert sympy.Matrix([[1, 2], [3, 4]])**sympy.Integer(2) == sympy.Matrix([[7, 10], [15, 22]])
    assertAlmostEqual(sympy.E._evalf(50), math.e)
    assert sympy.solve(1/x, x) == [] # issue 1694
    assert sympy.solve(-(1 + x)/(2 + x)**2 + 1/(2 + x), x) == [] # issue 1694
    assert sympy.limit(1 + 1/x, x, 0, dir='-') == -oo
    assert sympy.limit(1/x**2, x, 0, dir='-') == oo
    assert sympy.sympify(u'45') == 45 # issue 2508

@XFAIL
def test_sympy_1_div_0():
    assert sympy.S.One/S.Zero in (S.NaN, S.ComplexInfinity)

def test_sympy_files():
    sympy_dir = os.path.normpath(os.path.dirname(os.path.abspath(__file__)) + '/../../sympy')
    def tst(path):
        assert os.path.isfile(os.path.join(sympy_dir, path))
    tst('AUTHORS')
    tst('LICENSE')
    tst('README')
