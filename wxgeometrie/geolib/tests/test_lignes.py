# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from math import sqrt
from random import random

from tools.testlib import assertAlmostEqual, assertEqual, assertRaises, randint
from wxgeometrie.geolib.tests.geotestlib import rand_pt
from wxgeometrie.geolib import (Tangente, Perpendiculaire, Parallele, Mediatrice,
                                Droite_vectorielle, Point, Cercle, Droite,
                                Bissectrice, Label_droite, Label_demidroite,
                                Label_segment, Droite_equation, Milieu, Segment,
                                Barycentre, Vecteur_libre, RIEN, Demidroite, DemiPlan,
                                )


def test_Segment():
    A = Point(4.5,  7.3)
    B = Point(4,  2.1)
    s = Segment(A,  B)
    assert(isinstance(s.etiquette, Label_segment))
    assertAlmostEqual(s.longueur, sqrt((B.x - A.x)**2 + (B.y - A.y)**2))
    I = Milieu(s.point1,  s.point2)
    assertEqual(I.coordonnees,  ((A.x+B.x)/2, (A.y+B.y)/2))
    M = Barycentre((A,  1),  (B,  -2))
    N = Barycentre((A,  -2),  (B,  1))
    assert(I in s)
    assert(M not in s)
    assert(N not in s)
    assert(s.style("legende") == RIEN)

def test_Demidroite():
    A = Point(4.5,  7.3)
    B = Point(4,  2.1)
    s = Demidroite(A,  B)
    assert(isinstance(s.etiquette, Label_demidroite))
    assertRaises(AttributeError,  getattr,  s, "longueur")
    I = Milieu(s.origine,  s.point)
    assertEqual(I.coordonnees,  ((A.x+B.x)/2, (A.y+B.y)/2))
    M = Barycentre((A,  1),  (B,  -2))
    N = Barycentre((A,  -2),  (B,  1))
    assert(I in s)
    assert(M in s)
    assert(N not in s)
    assert(s.style("legende") == RIEN)

def test_Droite():
    A = Point(4.5,  7.3)
    B = Point(4,  2.1)
    d = Droite(A,  B)
    assert(isinstance(d.etiquette, Label_droite))
    assertRaises(AttributeError,  getattr,  d, "longueur")
    I = Milieu(d.point1,  d.point2)
    assertEqual(I.coordonnees,  ((A.x+B.x)/2, (A.y+B.y)/2))
    M = Barycentre((A,  1),  (B,  -2))
    N = Barycentre((A,  -2),  (B,  1))
    assert(I in d)
    assert(M in d)
    assert(N in d)
    assert(isinstance(d.equation,  tuple))
    assert(d.style("legende") == RIEN)
    # Test du typage dynamique
    d = Droite("y=x+1")
    assert(Point(0, 1) in d)
    d = Droite(Point(1, 2), Vecteur_libre(1, 1))
    assert(Point(1, 2) in d)
    assert(Point(2, 3) in d)
    d2 = Droite("y=-x+1")
    assert(Point(0, 1) in d2)
    assert(Point(1, 0) in d2)



def test_Droite_vectorielle():
    v = Vecteur_libre(1,  7)
    A = Point(-2, 3)
    d = Droite_vectorielle(A,  v)
    assert(d.vecteur is v and d.point is A)
    assertAlmostEqual(v.y/v.x,  -d.equation[0]/d.equation[1])
    B = rand_pt()
    d1 = Droite_vectorielle(B, v)
    assert(d.parallele(d1))

def test_Parallele():
    d0 = Droite_equation(2,  1,  7)
    A = Point(-2, 3)
    d = Parallele(d0,  A)
    assert(d.parallele(d0))
    assert(d.droite is d0 and d.point is A)
    assertAlmostEqual(d0.equation[:1],  d.equation[:1])

# def test_Droite_rotation():
#     r = Rotation(Point(1.45, -2.59), math.pi/3)
#     C = Point(1.458, -5.255)
#     D = Point(3.478, -2.14788)
#     d = Droite(C, D)
#     # Dans ce qui suit, d1, d2 et d3 doivent correspondre à la même droite.
#     d1 = Droite_rotation(d,  r)
#     d2 = Droite(r(C), r(D))
#     d3 = r(d)
#     a, b, c = d1.equation
#     assertAlmostEqual(d1.equation_reduite, d2.equation_reduite)
#     assertAlmostEqual(d1.equation_reduite, d3.equation_reduite)
#     assertAlmostEqual(d1.equation_reduite, (-a/b, -c/b))
#     d = Droite_rotation(Droite_equation(1, -1, 1),  Rotation(Point(0, 0), math.pi/2))
#     a, b, c = d.equation
#     assertAlmostEqual(b/a,  1)
#     assertAlmostEqual(c/a,  1)


def test_Mediatrice():
    A = Point(4.5,  7.3)
    B = Point(-4.147,  2.1)
    s = Segment(A,  B)
    d0 = Mediatrice(s)
    d1 = Mediatrice(A,  B)
    I = Milieu(A,  B)
    assert(I in d0)
    assert(I in d1)
    a,  b,  c = s.equation
    a0,  b0,  c0 = d0.equation
    assertAlmostEqual(a*a0 + b*b0,  0)
    assertAlmostEqual(d0.equation,  d1.equation)

def test_Perpendiculaire():
    d = Droite_equation(-1, 2, 0)
    M = Point()
    d0 = Perpendiculaire(d,  M)
    a,  b,  c = d.equation
    a0,  b0,  c0 = d0.equation
    assert(d.perpendiculaire(d0))
    assertAlmostEqual(a*a0 + b*b0,  0)
    assert(M in d0)

def test_Droite_equation():
    a = randint(50) - randint(50) + 0.1 # afin que a ne soit pas nul
    b = randint(50) - randint(50) + random()
    c = randint(50) - randint(50) + random()
    d, e, f = Droite_equation(a, b, c).equation
    assertAlmostEqual((e/d, f/d),  (b/a, c/a))
    assertEqual(Droite_equation(a, 0, 0).equation[1:],  (0, 0))
    assertEqual((Droite_equation(0, a, 0).equation[0], Droite_equation(0, a, 0).equation[2]),  (0, 0))
    assert(not Droite_equation(0, 0, 0).existe)
    d = Droite_equation("y=-5/2x-3/2")
    assert(Point(0, -1.5) in d)
    assert(Point(-1, 1) in d)
    d = Droite_equation("x=2*10**2")
    assert(Point(200, -1000) in d)
    assert(Point(100, -1000) not in d)
    d = Droite_equation("2*x+2*y=1")
    assert(Point(0.5, 0) in d)
    assert(Point(1, -0.5) in d)
    d = Droite_equation("x+y=1")
    assert(Point(0, 1) in d)
    assert(Point(1, 0) in d)
    d = Droite_equation("x+2y=-2")
    assert(Point(0, -1) in d)
    assert(Point(-2, 0) in d)

def test_Bissectrice():
    A = Point(1, -5)
    B = Point(1.5, -5.3)
    C = Point(3, -4)
    d = Bissectrice(A,  B,  C)
    a, b, c = d.equation
    d,  e = (0.0870545184921, -1.03861105199)
    assertAlmostEqual(b/a, d)
    assertAlmostEqual(c/a, e)

def test_Tangente():
    A = Point(4.75, -2.56887)
    O = Point(2.56874, -85.2541)
    M = Point(7.854, -552.444)
    c = Cercle(O, A)
    d = Tangente(c, A)
    assert(A in d)
    assert(M not in d)
    d1 = Tangente(c, M)
    assert(M in d1)
    assert(A not in d1)
    assert(not  Tangente(c, O).existe)

def test_equation_formatee():
    assert Droite('y=x').equation_formatee == '-x + y = 0'

def test_DemiPlan():
    d = Droite('y=-x+1')
    P1 = DemiPlan(d, Point(0, 0), True)
    P2 = DemiPlan(d, Point(0, 0), False)
    assert Point(0, 0) in P1
    assert Point(1, 0) in P1
    assert Point(0, 0) in P2
    assert Point(1, 0) not in P2
