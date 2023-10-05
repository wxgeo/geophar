# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

from sympy import exp, sqrt, Symbol

from wxgeometrie.mathlib.solvers import resoudre, positif, ensemble_definition

import wx_unittest

def _red(s):
    return '\033[0;31m' + s + '\033[0m'

class MathlibTest(wx_unittest.TestCase):
    def test_resoudre(self):
        self.assert_resoudre("2*x=0", "{0}")
        self.assert_resoudre("2*x>0", "]0;+oo[")
        self.assert_resoudre("(x>4 et x<7) ou (x/2-1>=3)", "]4;7[U[8;+oo[")
        self.assert_resoudre("(2)*x>0", "]0;+oo[")
        self.assert_resoudre("2*x+3>5*x-4 et 3*x+1>=4*x-4", ']-oo;7/3[')
        self.assert_resoudre("2*x+3*y=4 et 4*x-2*y=1", ["{x: 11/16, y: 7/8}", "{y: 7/8, x: 11/16}"])
        self.assert_resoudre("ln(x)<ln(-2*x+1)", "]0;1/3[")
        self.assert_resoudre("exp(x^2)-x^2-1>=0", "]-oo;+oo[")
        self.assert_resoudre("x*(sqrt(64-x^2))=32", "{4*sqrt(2)}")
        self.assert_resoudre('x - 1 + exp(x)>=0', '[0;+oo[')

    def test_resoudre_abs(self):
        self.assert_resoudre('abs(2*x+3)-4>0', ']-oo;-7/2[U]1/2;+oo[')
        self.assert_resoudre('exp(abs(2*x+3))>3', ']-oo;-3/2 - ln(3)/2[U]-3/2 + ln(3)/2;+oo[')
        self.assert_resoudre('3*abs(2*x-7)-2*abs(5*x+2)>0', ']-25/4;17/16[')
        self.assert_resoudre('3*abs(2*x-7)-2*abs(5*x+2)+5*abs(x+4)-9>0', ']-oo;-4[U]-4;28/11[U]14;+oo[')

    def test_resoudre_substitution(self):
        self.assert_resoudre('sqrt(x**2+3)-x**2+3>=0', '[-sqrt(6);sqrt(6)]')
        self.assert_resoudre('sqrt(x+3)+x-5>=0', '[11/2 - sqrt(33)/2;+oo[')

    def test_resoudre_puissances(self):
        self.assert_resoudre('sqrt(x)>4', ']16;+oo[')
        self.assert_resoudre('x^2.3>4', ']2^(20/23);+oo[')
        self.assert_resoudre('-3*x^2.3>4', ['{}', 'Ø'])

    def test_sqrt(self):
        self.assert_resoudre('x+sqrt(x)>4', ']9/2 - sqrt(17)/2;+oo[')
        self.assert_resoudre('sqrt(x^2-3)<=5', '[-2*sqrt(7);-sqrt(3)]U[sqrt(3);2*sqrt(7)]')
        self.assert_resoudre('sqrt(x+3)-sqrt(x**2-4)>=0', '[1/2 - sqrt(29)/2;-2]U[2;1/2 + sqrt(29)/2]')

    def test_trigo(self):
        self.assert_resoudre('sin(x)<=1/2', '[0;pi/6]U[5*pi/6;2*pi]')
        self.assert_resoudre('sin(2*x)<1/2', '[0;pi/12[U]5*pi/12;pi]')

    def test_resoudre_floats(self):
        # pass (Geophar 12.08 revision 64f4bb42)
        self.assert_resoudre("0.5*exp(-0.5*x + 0.4)=0.5", "{4/5}")
        # fail (Geophar 12.08 revision 64f4bb42)
        self.assert_resoudre("exp(-0.5*x - 0.4)-1=0", "{-4/5}")

    def test_positif(self):
        x = Symbol("x")
        self.assert_positif(x**7, "[0;+oo[")
        self.assert_positif((x + 1)**5, "[-1;+oo[")
        self.assert_positif(sqrt(x + 1), "[-1;+oo[")
        self.assert_positif((x + 1)**6, "]-oo;+oo[")
        self.assert_positif(-x**2 - x, "[-1;0]")
        self.assert_positif(sqrt(5), "]-oo;+oo[")
        self.assert_positif((x - 1)/(x + 1), ']-oo;-1[U[1;+oo[')
        self.assert_positif(x*exp(3) - 1, '[exp(-3);+oo[')

    def test_positif2(self):
        x = Symbol("x")
        self.assert_positif(x - 1 + exp(x), "[0;+oo[")

    def test_ensemble_definition(self):
        x = Symbol("x")
        self.assert_ens_def((2 - x)/(6 - 5*x + x**2), ']-oo;2[U]2;3[U]3;+oo[')

    def test_issue_230(self):
        # 3 racines réelles pour le polynôme.
        self.assertEqual(str(resoudre("x^3+7*x^2-5*x-4==0").evalf()),
              '{-7.58937000406433 ; -0.48882774214088 ; 1.07819774620521}')

    def test_issue_306(self):
        x = Symbol("x")
        self.assert_positif(x + sqrt(x**2 - 5), '[sqrt(5);+oo[')
        self.assert_positif(x - sqrt(x**2 - 5), '[sqrt(5);+oo[')

    def test_poly3(self):
        sols = resoudre('5 + 1500/x**2 - 2*(1500*x + 100)/x**3=0', ensemble='R')
        # 3 solutions
        self.assertEqual(len(sols.intervalles), 3)
