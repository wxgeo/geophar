# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from pytest import XFAIL

#from tools.testlib import assertAlmostEqual
from wxgeometrie.geolib.tests.geotestlib import rand_pt
from wxgeometrie.geolib import NOM

def test_Label_point():
    A = rand_pt()
    B = rand_pt()
    A.label("Position de l'hirondelle d'Afrique.")
    B.label(u"Position de l'hirondelle européenne.")
    assert(A.label() == "Position de l'hirondelle d'Afrique.")
    assert(B.label() == u"Position de l'hirondelle européenne.")
    A.style(legende = NOM)
    assert(A.label() == "")

@XFAIL
def test_Label_segment():
    raise NotImplementedError

@XFAIL
def test_Label_droite():
    raise NotImplementedError

@XFAIL
def test_Label_demidroite():
    raise NotImplementedError

@XFAIL
def test_Label_cercle():
    raise NotImplementedError

@XFAIL
def test_Label_arc_cercle():
    raise NotImplementedError

@XFAIL
def test_Label_polygone():
    raise NotImplementedError

@XFAIL
def test_Label_angle():
    raise NotImplementedError
