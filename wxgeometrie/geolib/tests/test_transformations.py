# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from random import random
from math import pi

from tools.testlib import assertAlmostEqual, randint
from wxgeometrie.geolib import (Point, Droite, Droite_equation, Reflexion, Rotation, Translation,
                                Homothetie, Symetrie_centrale, Milieu, Mediatrice, Vecteur_libre
                                )


def test_Rotation():
    A = Point(1.523, 45.35211)
    r = Rotation(A, pi/4)
    M = Point(1.4452,  -1.2545)
    assertAlmostEqual(r(M).coordonnees, (34.423837071540447, 12.341247113306926))
    assertAlmostEqual(r(A).coordonnees, A.coordonnees)
    d = Droite(A, M)
    d1 = Droite(A, r(M))
    assertAlmostEqual(r(d).equation_reduite, d1.equation_reduite)
    assert(r(A) is A)


def test_Translation():
    v = Vecteur_libre(random()+randint(50)-randint(50), random()+randint(50)-randint(50))
    t = Translation(v)
    M = Point(random()+randint(50)-randint(50), random()+randint(50)-randint(50))
    assertAlmostEqual(M.x + v.x, t(M).x)
    assertAlmostEqual(M.y + v.y, t(M).y)


def test_Reflexion():
    d = Droite_equation(1, 6, -2)
    r = Reflexion(d)
    M = Point(random()+randint(50)-randint(50), random()+randint(50)-randint(50))
    m = Mediatrice(M,  r(M))
    assertAlmostEqual(d.equation_reduite,  m.equation_reduite)
    assert(r(d) is d)

def test_Homothetie():
    A = Point(1, -2)
    h = Homothetie(A, -3)
    M = Point(2, 7)
    assertAlmostEqual(h(M).coordonnees, (-2, -29))
    assert(h(A) is A)


def test_Symetrie_centrale():
    M = Point(random()+randint(50)-randint(50), random()+randint(50)-randint(50))
    A = Point(random()+randint(50)-randint(50), random()+randint(50)-randint(50))
    s = Symetrie_centrale(A)
    assertAlmostEqual(Milieu(M, s(M)).coordonnees, A.coordonnees)
    assert(s(A) is A)
