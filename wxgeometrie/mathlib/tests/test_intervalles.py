# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

import mathlib

from tools.testlib import *

import mathlib
import mathlib.intervalles as intervalles
from mathlib.intervalles import Intervalle
import sympy



def assert_intervalle_preformater(x, y):
    y_ = intervalles.preformatage_ensemble(x)
    if y_ != y:
        print "/!\\ Formule: ", x
        print "ERREUR: ",  y_, " != ", y
    assert(y_ == y)

def test_preformater():
    assert_intervalle_preformater("R", "]-oo;+oo[")
    assert_intervalle_preformater("R+", "[0;+oo[")
    assert_intervalle_preformater("R*", "]-oo;+oo[-{0}")
    assert_intervalle_preformater("R-U{3}", "]-oo;0]+{3}")
    assert_intervalle_preformater("R-{3}", "]-oo;+oo[-{3}")
    assert_intervalle_preformater("R-{3}", "]-oo;+oo[-{3}")
    assert_intervalle_preformater("[0,1]U]1,2]", "[0;1]+]1;2]")

def test_intervalle():
    assert(str(Intervalle(8) + Intervalle(9)) == '[8;+oo[')
    assert(str(Intervalle("{0}")) == '{0}')

def test_evalf():
    i = intervalles.conversion_chaine_ensemble(']-oo;-2]U[1/4;1/2[')
    assert(str(i.evalf()) == ']-oo;-2.0]U[0.25;0.5[')
    i = Intervalle(-sympy.sqrt(2), sympy.pi)
    assert(str(i.evalf()) == '[-1.41421356237310;3.14159265358979]')
    assert(str(i.evalf(n = 3)) == '[-1.41;3.14]')
