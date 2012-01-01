# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from pytest import XFAIL

from tools.testlib import assertAlmostEqual
from wxgeometrie.geolib import Fonction, Feuille

_VAL0 = -5.156557933


@XFAIL
def test_Fonction():
    u"Test sans feuille."
    g = Fonction('2x+7')
    assert g(17) == 41
    # La fonction n'est compilée que s'il y a une feuille.
    # -> à tester lorsque chaque objet aura un feuille par défaut.


def test_base():
    f = Feuille()
    H = f.objets.H = Fonction("2*t**3+5", variable = 't')
    assertAlmostEqual(H(_VAL0), 2*_VAL0**3+5)


def test_reecriture():
    f = Feuille()
    H = f.objets.H = Fonction("2x^2+3x(1+x)", 'R')
    def h(x):
        return 2*x**2+3*x*(1+x)
    assertAlmostEqual(H(17), h(17))
    assertAlmostEqual(H(_VAL0), h(_VAL0))


def test_variables():
    f = Feuille()
    o = f.objets
    a = o.a = 3
    b = o.b = 5
    g = o.g = Fonction("a*x+b")
    assertAlmostEqual(g(4), a*4+b)
    assertAlmostEqual(g(_VAL0), a*_VAL0+b)

def test_intervalle():
    f = Feuille()
    o = f.objets
    g = o.g = Fonction('x^2+2x+1', ']0;5')
    assert g.style('extremites_cachees') == ([5],)
    assert g.ensemble == ']0;5['
