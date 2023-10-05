# -*- coding: utf-8 -*-

import os, math,sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../../.."))
sys.path.insert(0, TOPDIR)

from sympy import (Symbol, exp, solve, limit, S, E, Matrix, Integer, oo,
                    sympify, Float, sqrt,
                    )

import tools.unittest, unittest

def isDebian():
    issueFile = os.path.join('/etc','issue')
    return os.path.isfile(issueFile) and "Debian" in open(issueFile).read()

# Teste que certains bugs de sympy sont bien ou résolus, ou temporairement patchés

class MathlibTest(tools.unittest.TestCase):

    def test_sympy(self):
        x = Symbol('x', real=True)
        self.assertTrue(-oo < oo)
        self.assertFalse(-1.5 < -oo)
        self.assertIsNone((1 - exp(x)).is_negative)
        self.assertEqual(Matrix([[1, 2], [3, 4]])**Integer(2),
                         Matrix([[7, 10], [15, 22]]))
        self.assertAlmostEqual(E._evalf(50), math.e)
        self.assertEqual( solve(1/x, x), []) # issue 1694
        self.assertEqual(solve(-(1 + x)/(2 + x)**2 + 1/(2 + x), x),
                         []) # issue 1694
        self.assertEqual(limit(1 + 1/x, x, 0, dir='-'), -oo)
        self.assertEqual(limit(1/x**2, x, 0, dir='-'), oo)
        self.assertEqual(sympify('45'), 45) # issue 2508

    @unittest.expectedFailure
    def test_issue10391(self):
        # issue 10391 (FS#319)
        x = Symbol('x', real=True)
        self.assertEqual(solve((2*x + 8)*exp(-6*x), x), [-4])

    def test_sympy_solving_with_floats(self):
        x = Symbol('x', real=True)

        sols = solve(exp(-Float('0.5')*x + Float('0.4')) - 1)
        self.assertEqual(len(sols), 1)
        sol = sols[0]
        self.assertAlmostEqual(sol, Float('0.8'))

        sols = solve(exp(-Float('0.5')*x - Float('0.4')) - 1)
        self.assertEqual(len(sols), 1)
        sol = sols[0]
        self.assertAlmostEqual(sol, Float('-0.8'))

        sols = solve(exp(-Float('0.5', 10)*x + Float('0.4', 10)) - 1)
        self.assertEqual(len(sols), 1)
        sol = sols[0]
        self.assertAlmostEqual(sol, Float('0.8'))

    def test_sympy_1_div_0(self):
        self.assertIs(S.One/S.Zero, S.ComplexInfinity)

    @unittest.skipIf(isDebian(),
                     "Debian Geophar packages do not embed sympy")
    def test_sympy_files(self):
        sympy_dir = os.path.normpath(os.path.dirname(os.path.abspath(__file__)) + '/../../sympy')
        def tst(path):
            result = os.path.isfile(os.path.join(sympy_dir, path))
            if not result:
                print(os.path.join(sympy_dir, path), "is not an existing file")
            self.assertTrue(result)
        tst('AUTHORS')
        tst('LICENSE')
        tst('README.rst')



    def test_solve_reals(self):
        x = Symbol('x', real=True)
        self.assertEqual(solve(sqrt(x)), [0])

    def test_set(self):
        self.assertEqual(S(2), 2)
        self.assertEqual({S(2)}, {2})
