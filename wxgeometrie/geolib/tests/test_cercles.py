# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from math import sqrt, sin, cos
from random import random

from pytest import XFAIL

from tools.testlib import assertAlmostEqual, assertEqual
from wxgeometrie.geolib import (Cercle_points, Cercle_diametre, Cercle_rayon, Demicercle,
                                Arc_oriente, Arc_points, Label_arc_cercle, Disque,
                                Label_cercle, Rayon, Point, Cercle, Milieu, Segment,
                                Mediatrice, Arc_cercle, Cercle_equation,
                                )

def test_Arc_cercle():
    A = Point(-1.2561, 45.236)
    B = Point(251.2561, 41.256)
    O = Point(-42.25, 2.351)
    a = Arc_cercle(O, A, B)
    assert(isinstance(a.etiquette, Label_arc_cercle))
    assert(A in a)
    assert(B not in a)
    assert(O not in a)


def test_Arc_points():
    A = Point(-1.2561, 45.236)
    B = Point(251.2561, 41.256)
    C = Point(-42.25, 2.351)
    a = Arc_points(A, B, C)
    assert(A in a)
    assert(B in a)
    assert(C in a)
    assertAlmostEqual(a.longueur, 1208.25931027)
    assertAlmostEqual(a.centre.coordonnees, (122.51970100911581, -114.11725498641933))

def test_Arc_oriente():
    A = Point(-1.2561, 45.236)
    B = Point(251.2561, 41.256)
    C = Point(-42.25, 2.351)
    a = Arc_oriente(A, B, C)
    assert(A in a)
    assert(B in a)
    assert(C in a)
    assertAlmostEqual(a.longueur, 1208.25931027)
    assertAlmostEqual(a.centre.coordonnees, (122.51970100911581, -114.11725498641933))
    assert(a.sens == "indirect")

def test_Demicercle():
    A = Point(-1.2561, 45.236)
    B = Point(251.2561, 41.256)
    c = Demicercle(A, B)
    assertAlmostEqual(Milieu(A, B).coordonnees, c.centre.coordonnees)
    assertAlmostEqual(c.diametre, Segment(A, B).longueur)
    assertAlmostEqual(c.rayon, Segment(A, B).longueur/2)

def test_Cercle_rayon():
    A = Point(-2.586, 7.541)
    c_1 = Cercle_rayon(A, -1)
    c0 = Cercle_rayon(A, 0)
    c2 = Cercle_rayon(A, 2)
    assert(isinstance(c_1.etiquette, Label_cercle))
    assert(not c_1.existe)
    assert(c0.existe)
    assert(c2.existe)
    assertAlmostEqual(A.coordonnees, c0.centre.coordonnees)
    assert(A not in c_1)
    assert(A in c0)
    assert(A not in c2)
    assertEqual(c_1.rayon,  -1)
    assertEqual(c0.rayon,  0)
    assertEqual(c2.rayon,  2)
    k = random()
    B = Point(A.x + 2*sin(k),  A.y + 2*cos(k))
    assert(B in c2)

@XFAIL
def test_cercle_defini_par_equation():
    c = Cercle("x^2+y^2-2x+y-3=0")
    assertAlmostEqual(c.centre.xy, (1, -.5))
    assertAlmostEqual(c.rayon, sqrt(4.25))

def test_Cercle():
    A = Point(2.78841, -5.25)
    O = Point(27.8841, -0.525)
    c = Cercle(O, A)
    assert(c.centre is O)
    assert(c.point is A)
    assertAlmostEqual(c.rayon, 25.5366262763)
   # Test du typage dynamique
    c = Cercle(Point(1, 1), 1)
    assert(Point(1, 2) in c)
    c = Cercle(Point(1, 1), Point(0, 2), Point(-1, 1))
    assert(Point(0, 0) in c)
    assertAlmostEqual(c.centre.coordonnees, (0, 1))

def test_Cercle_diametre():
    A = Point(2.78841, -5.25)
    B = Point(27.8841, -0.525)
    c = Cercle_diametre(A, B)
    c1 = Cercle(A, B)
    assertAlmostEqual(c.diametre, c1.rayon)
    assertAlmostEqual(c.diametre, Segment(A, B).longueur)
    assertAlmostEqual(c.centre.coordonnees, Milieu(A, B).coordonnees)

def test_Cercle_points():
    A = Point(2.78841, -5.25)
    B = Point(27.8841, -0.525)
    C = Point(-42.25, 2.351)
    c = Cercle_points(A, B, C)
    assert(c.centre in Mediatrice(Segment(A, B)))
    assert(c.centre in Mediatrice(Segment(A, C)))


def test_Cercle_equation():
    c = Cercle_equation()
    assertAlmostEqual(c.centre.coordonnees, (0, 0))
    assert(c.rayon == 1)
    c.a = -2
    c.b = 4
    c.c = -4
    assertAlmostEqual(c.centre.coordonnees, (1, -2))
    assert(c.rayon == 3)
    assert(c.existe)
    c.c = 6
    assert(not c.existe)


def test_Disque():
    A = Point(2.78841, -5.25)
    B = Point(27.8841, -0.525)
    C = Point(-42.25, 2.351)
    c = Cercle_points(A, B, C)
    d = Disque(c)
    assertAlmostEqual(d.centre.coordonnees, c.centre.coordonnees)
    assertAlmostEqual(d.rayon, c.rayon)
    assert(A in d)
    assert(B in d)
    assert(C in d)
    assert(d.centre in d)
    assert(Point(-500, -500) not in d)

def test_equation_formatee():
    assert Cercle((10, 0), (1, 5)).equation_formatee == u'x\xb2 + y\xb2 - 20 x - 6 = 0'

def test_Rayon():
    c = Cercle((1, 1), (4, 5))
    r = Rayon(c)
    assertAlmostEqual(r.val, 5)
    c.point.x = 1
    assertAlmostEqual(r.val, 4)
