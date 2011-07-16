# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from random import random

from sympy import sympify as symp

from tools.testlib import assertAlmostEqual, assertEqual, randint
from wxgeometrie.geolib.tests.geotestlib import rand_pt, rand_cercle

from wxgeometrie.geolib import (Glisseur_arc_cercle, Glisseur_cercle, Glisseur_demidroite,
                                Glisseur_droite, Point, Demidroite, Droite,
                                Glisseur_segment, Point_equidistant, Centre,
                                Centre_cercle_inscrit, Centre_cercle_circonscrit,
                                Orthocentre, Projete_demidroite, Projete_segment,
                                Projete_arc_cercle, Projete_cercle, Segment,
                                Projete_droite, Centre_gravite, Label_point,
                                Point_reflexion, Point_homothetie, Cercle,
                                Point_rotation, Point_translation, Point_final,
                                Arc_points, Arc_cercle, Triangle, Milieu,
                                Barycentre, Mediatrice, Droite_equation,
                                Cercle_equation, Polygone, Rotation, Translation,
                                Vecteur, Vecteur_libre, Representant, Reflexion,
                                Homothetie, NOM,
                                )

def test_Point():
    A = Point(1, 2)
    assert(isinstance(A.etiquette, Label_point))
    assertEqual(A.x, 1)
    assertEqual(A.y, 2)
    assertEqual(type(A.coordonnees),  tuple)
    A.x = 5
    A.y = 7
    assertEqual(A.coordonnees, (5, 7))
    assert(A.style("legende") == NOM)
    # Test du typage dynamique
    d = Droite(rand_pt(), rand_pt())
    B = Point(d)
    assert(isinstance(B, Glisseur_droite))
    c = Cercle(A, 3)
    C = Point(c)
    assert(isinstance(C, Glisseur_cercle))
    d = Demidroite(rand_pt(), rand_pt())
    B = Point(d)
    assert(isinstance(B, Glisseur_demidroite))
    s = Segment(rand_pt(), rand_pt())
    B = Point(s)
    assert(isinstance(B, Glisseur_segment))
    a = Arc_points(Point(), Point(1, 1),  Point(1, 2))
    B = Point(a)
    assert(isinstance(B, Glisseur_arc_cercle))

def test_Point_sympy():
    A = Point('1/2', '2/3')
    assertEqual(A.x, symp('1/2'))
    assertAlmostEqual(A.coordonnees, (1/2, 2/3))


def test_Milieu():
    A = Point(1,2)
    B = Point(2,4)
    I = Milieu(A,B)
    assert(I.x == (A.x+B.x)/2 and I.y == (A.y+B.y)/2)
    assertEqual(type(I.coordonnees),  tuple)
    C = Point('1/3', '1')
    D = Point('1', '1')
    J = Milieu(C, D)
    assert(J.x == symp('2/3'))


def test_Barycentre():
    M = Point(3, 4)
    A = Point(1,2)
    B = Point(2,4)
    I = Milieu(A,B)
    K = Barycentre(M, A, B, (I, -4))
    assertEqual(K.x,  0)
    assertEqual(K.y,  2)
    assert(not Barycentre(M, A, (B, -2)).existe)
    assertEqual(type(K.coordonnees),  tuple)
    # Test keyword 'points_ponderes'
    G = Barycentre(points_ponderes = (M, A, B, (I, -4)))
    assert(K.coordonnees == G.coordonnees)
    assert("point_ponderes" not in G.style())

def test_Point_final():
    A = Point(random(),random())
    C = Point(random(),random())
    u = Vecteur_libre(random(),random())
    v = Vecteur(Point(random(),  random()),  Point(random(),  random()))
    w = Representant(Vecteur(Point(random(),  random()),  Point(random(),  random())),  A)
    F = Point_final(C,  (u, v, w), (-2, 1.5, 4))
    assertEqual(type(F.coordonnees),  tuple)
    assertAlmostEqual(F.x,  C.x -2*u.x+1.5*v.x+4*w.x)
    assertAlmostEqual(F.y,  C.y -2*u.y+1.5*v.y+4*w.y)

def test_Point_translation():
    u = Vecteur_libre(1.56, 2.78)
    v = Vecteur(Point(1.1457, 2.7895), Point(2.458, -8.25))
    A = Point(5.256, -7.231)
    tu = Translation(u)
    tv = Translation(v)
    Au = Point_translation(A, tu)
    Av = Point_translation(A, tv)
    assertAlmostEqual(Au.coordonnees,  (6.816, -4.451))
    assertAlmostEqual(Av.coordonnees, (6.5683, -18.2705))

def test_Point_rotation():
    A = Point(1, -4)
    r = Rotation(Point(-2, 7.56), 4.25)
    B = Point_rotation(A, r)
    assertAlmostEqual(r(A).coordonnees, B.coordonnees)
    assertAlmostEqual(B.coordonnees,  (-13.684339450863803, 10.031803308717693))
    A = Point('1',  '0')
    r = Rotation(('0', '0'), 'pi/4')
    B = Point_rotation(A, r)
    C = Point('sqrt(2)/2', 'sqrt(2)/2')
    assert(C.x == B.x and C.y == B.y)

def test_Point_homothetie():
    A = Point(1, -2)
    h = Homothetie(A, -3)
    M = Point(2, 7)
    assertAlmostEqual(Point_homothetie(M, h).coordonnees, (-2, -29))
#    assert(Point_homothetie(A, h) is A)   -> méthode __new__ ?

def test_Point_reflexion():
    d = Droite_equation(1, 6, -2)
    r = Reflexion(d)
    M = Point(random()+randint(50)-randint(50), random()+randint(50)-randint(50))
    m = Mediatrice(M,  Point_reflexion(M, r))
    assertAlmostEqual(d.equation_reduite,  m.equation_reduite)

def test_Projete_droite():
    d = Droite_equation(1.25, -7.12, 2.15)
    A = Point(1.52, 2.14)
    M = Projete_droite(A, d)
    assert(M in d)
    assert(Droite(A, M)._perpendiculaire(d))

def test_Projete_cercle():
    c = Cercle_equation(1, -2, -20)
    assert(c.existe)
    A = Point(randint(50) - randint(50) + random(), randint(50) - randint(50) + random())
    P = Projete_cercle(A, c)
    assert(P.existe)
    assert(P in c)
    assert(P in Demidroite(c.centre, A))
    A.coordonnees = c.centre.coordonnees
    assert(not P.existe)

def test_Projete_arc_cercle():
    O = Point(23.15, -12.75)
    A = Point(-12.5, 7.14)
    B = Point(7.15, 8.64)
    a = Arc_cercle(O, A, B)
    M = rand_pt()
    P = Projete_arc_cercle(M, a)
    assert(P in a)
    M.coordonnees = a.centre.coordonnees
    assert(not P.existe)
    M.coordonnees = -17.826266675199999, 11.760911186
    assert(type(P.coordonnees) is tuple)
    assertAlmostEqual(A.coordonnees, P.coordonnees)
    assertEqual(A, P)

def test_Projete_segment():
    s = Segment(rand_pt(), rand_pt())
    M = rand_pt()
    assert(Projete_segment(M, s) in s)
    A = Point(0, 1)
    B = Point(2, 1)
    s = Segment(A, B)
    M = Point(1, 7.15)
    P = Projete_segment(M, s)
    assertAlmostEqual(Milieu(A, B).coordonnees, P.coordonnees)
    M.x = .5
    assertAlmostEqual(Barycentre((A, 3), (B, 1)).coordonnees, P.coordonnees)
    M.x = -1
    assertAlmostEqual(A.coordonnees, P.coordonnees)
    M.x = 3
    assertAlmostEqual(B.coordonnees, P.coordonnees)


def test_Projete_demidroite():
    d = Demidroite(rand_pt(), rand_pt())
    M = rand_pt()
    assert(Projete_demidroite(M, d) in d)
    A = Point(0, 1)
    B = Point(2, 1)
    s = Demidroite(A, B)
    M = Point(1, 7.15)
    P = Projete_demidroite(M, s)
    assertAlmostEqual(Milieu(A, B).coordonnees, P.coordonnees)
    M.x = .5
    assertAlmostEqual(Barycentre((A, 3), (B, 1)).coordonnees, P.coordonnees)
    M.x = -1
    assertAlmostEqual(A.coordonnees, P.coordonnees)
    M.x = 3
    assertAlmostEqual(Barycentre((A, -1), (B, 3)).coordonnees, P.coordonnees)


def test_Centre_gravite():
    A = rand_pt()
    B = rand_pt()
    C = rand_pt()
    I = Milieu(B, C)
    J = Milieu(A, C)
    K = Milieu(A, B)
    G = Centre_gravite(Triangle(A, B, C))
    assertAlmostEqual(Segment(A, G).longueur, 2*Segment(I, G).longueur)
    assertAlmostEqual(Segment(B, G).longueur, 2*Segment(J, G).longueur)
    assertAlmostEqual(Segment(C, G).longueur, 2*Segment(K, G).longueur)

def test_Orthocentre():
    A, B, C = rand_pt(), rand_pt(), rand_pt()
    p = Polygone(A, B, C)
    H = Orthocentre(p)
    assert(Droite(A, H).perpendiculaire(Droite(B, C)))
    assert(Droite(B, H).perpendiculaire(Droite(A, C)))
    assert(Droite(C, H).perpendiculaire(Droite(B, A)))

def test_Centre_cercle_circonscrit():
    A, B, C = rand_pt(), rand_pt(), rand_pt()
    p = Polygone(A, B, C)
    O= Centre_cercle_circonscrit(p)
    assert(O == Point_equidistant(A, B, C))

def test_Centre_cercle_inscrit():
    A, B, C = rand_pt(), rand_pt(), rand_pt()
    p = Polygone(A, B, C)
    I = Centre_cercle_inscrit(p)
    P = Projete_segment(I, Segment(B, C))
    Q = Projete_segment(I, Segment(A, C))
    R = Projete_segment(I, Segment(A, B))
    c = Cercle(I, P)
    assert(P in c and Q in c and R in c)

def test_Centre():
    c = rand_cercle()
    O = Centre(c)
    M = Glisseur_cercle(c)
    assertAlmostEqual(Segment(O, M).longueur, c.rayon)

def test_Point_equidistant():
    A = rand_pt()
    B = rand_pt()
    C = rand_pt()
    P = Point_equidistant(A, B, C)
    assertAlmostEqual(Segment(A, P).longueur, Segment(B, P).longueur)
    assertAlmostEqual(Segment(A, P).longueur, Segment(C, P).longueur)
    assert(P in Mediatrice(A, B))

def test_Glisseur_droite():
    A = rand_pt()
    B = rand_pt()
    d = Droite(A, B)
    M = Glisseur_droite(d)
    assert(M in d)
    M.k = 0
    assertEqual(M.k, 0)
    assertAlmostEqual(M.coordonnees, A.coordonnees)
    P = Point(*M.coordonnees)
    M.k = 1
    assertEqual(M.k, 1)
    assertAlmostEqual(M.coordonnees, B.coordonnees)
    M.k = 2
    assertEqual(M.k, 2)
    M.k = -1
    assertEqual(M.k, -1)
    Q = Point(*M.coordonnees)
    assertAlmostEqual(Droite(P, Q).equation_reduite, d.equation_reduite)
    M.k = 1.7
    M(*M.coordonnees)
    assertAlmostEqual(M.k, 1.7)


def test_Glisseur_segment():
    A = rand_pt()
    B = rand_pt()
    s = Segment(A, B)
    M = Glisseur_segment(s)
    assert(M in s)
    M.k = 0
    assertEqual(M.k, 0)
    assertAlmostEqual(M.coordonnees, A.coordonnees)
    P = Point(*M.coordonnees)
    M.k = 1
    assertEqual(M.k, 1)
    assertAlmostEqual(M.coordonnees, B.coordonnees)
    M.k = 2
    assertEqual(M.k, 1) # 0<=k<=1 pour un segment
    assert(M in s)
    M.k = -1
    assertEqual(M.k, 0) # 0<=k<=1 pour un segment
    assert(M in s)
    M.k = 1
    Q = Point(*M.coordonnees)
    assertAlmostEqual(Droite(P, Q).equation_reduite, s.equation_reduite)
    M.k = 1.7
    M(*M.coordonnees)
    assertAlmostEqual(M.k, 1)

def test_Glisseur_demidroite():
    A = rand_pt()
    B = rand_pt()
    d = Demidroite(A, B)
    M = Glisseur_demidroite(d)
    assert(M in d)
    M.k = 0
    assertEqual(M.k, 0)
    assertAlmostEqual(M.coordonnees, A.coordonnees)
    P = Point(*M.coordonnees)
    M.k = 1
    assertEqual(M.k, 1)
    assertAlmostEqual(M.coordonnees, B.coordonnees)
    M.k = 2
    assertEqual(M.k, 2)
    M.k = -1
    assertEqual(M.k, 0) # k>=0 pour une demi-droite
    M.k = 1
    Q = Point(*M.coordonnees)
    assertAlmostEqual(Droite(P, Q).equation_reduite, d.equation_reduite)
    M.k = 1.7
    M(*M.coordonnees)
    assertAlmostEqual(M.k, 1.7)

def test_Glisseur_cercle():
    c = rand_cercle()
    M = Glisseur_cercle(c)
    assert(M in c)
    O = c.centre
    M.coordonnees = O.coordonnees
    # il faudrait compléter un peu

def test_Glisseur_arc_cercle():
    A = rand_pt()
    B = rand_pt()
    C = rand_pt()
    a = Arc_cercle(A, B, C)
    M = Glisseur_arc_cercle(a)
    assert(M in a)
    O = a.centre
    M.coordonnees = O.coordonnees
    # il faudrait compléter un peu
