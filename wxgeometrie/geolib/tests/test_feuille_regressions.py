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
