# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

import re
from math import cos, pi, e, sqrt

from pytest import XFAIL

from tools.testlib import assertAlmostEqual, assertRaises, assertEqual
from wxgeometrie.geolib.tests.geotestlib import rand_pt
from wxgeometrie.geolib import (Triangle_rectangle, DescripteurFeuille, Point, Segment,
                    Vecteur, Fonction, Variable, Feuille, Angle, contexte, Arc_cercle,
                    Texte, Droite, Carre, Triangle, Polygone, Cercle, Parallelogramme,
                    NOM, Droite_equation, Cercle_equation, Courbe, FORMULE, Formule
                    )
from wxgeometrie.geolib.routines import nice_display
from wxgeometrie.geolib.feuille import parse_equation, is_equation


def test_issue_186():
    f = Feuille()
    f.executer("c=Cercle")
    assertRaises(NameError, f.executer, "C_'=_")
    assert(f.objets.has_key("c"))

def test_issue_176():
    f = Feuille()
    A = f.objets.A = Point()
    B = f.objets.B = Point()
    f.objets.s = Segment(A, B)
    del f.objets.A, f.objets.B, f.objets.s
    assert set(('A', 'B', 's')).isdisjoint(f.objets.noms)

def test_issue_227():
    pass

def test_issue_252():
    # Test de la conversion intelligente des virgules en points
    # dans l'interpréteur de commandes de geolib.

    # 1er cas : conserver les virgules
    # Par exemple, 'A=(1,2)' signifie 'A=(1, 2)'
    f = Feuille()
    f.executer("A=(1,5)")
    f.executer("B = (-2,3)")
    assert f.objets.A.xy == (1, 5)
    assert f.objets.B.xy == (-2, 3)

    # 2e cas : transformer les virgules en point (séparateur décimal)
    # Par exemple, 'g(1,3)' signifie 'g(1.3)'
    f.executer('g = Fonction("2x+3")')
    f.executer("a = g(5,3)")
    assertAlmostEqual(f.objets.a, 13.6)
    f.executer("=Point(1,5 ; g(1,5))")
    assertAlmostEqual(f.objets.M1.xy, (1.5, 6.))

    f.executer('g2 = Fonction("3x+1")')
    f.executer("a = g2(-1,2)")
    assertAlmostEqual(f.objets.a, -2.6)
    f.executer("=Point(-1,5 ; g2(-1,5))")
    assertAlmostEqual(f.objets.M2.xy, (-1.5, -3.5))