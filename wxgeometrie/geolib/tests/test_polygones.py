# -*- coding: iso-8859-1 -*-
from __future__ import division, absolute_import # 1/2 == .5 (par defaut, 1/2 == 0)

from math import pi, sin, cos
from random import random

from tools.testlib import assertAlmostEqual, assertEqual, randint
from wxgeometrie.geolib.tests.geotestlib import rand_pt
from wxgeometrie.geolib import (Point, Polygone, Milieu, Label_polygone, Barycentre,
                                Droite, Triangle, Angle, Vecteur,
                                Quadrilatere, Pentagone, Hexagone, Heptagone,
                                Octogone, Segment, Parallelogramme,
                                Triangle_isocele, Triangle_equilateral, Rectangle,
                                Carre, Polygone_regulier, Carre_centre,
                                Triangle_equilateral_centre, Polygone_regulier_centre,
                                Losange, Mediatrice, Triangle_isocele_rectangle,
                                Triangle_rectangle,
                                )

# def test_Cote():
#     pass # À ÉCRIRE
#
# def test_Sommet():
#     pass # À ÉCRIRE

def test_Polygone():
    # cas général : polygone à 11 côtés :
    A = rand_pt()
    B = rand_pt()
    C = rand_pt()
    D = rand_pt()
    E = rand_pt()
    F = rand_pt()
    G = rand_pt()
    H = rand_pt()
    I = rand_pt()
    J = rand_pt()
    K = rand_pt()
    p = p0 = Polygone(A, B, C, D, E, F, G, H, I, J, K)
    assert(isinstance(p.etiquette, Label_polygone))
    assert(p.sommets[0] == A and p.sommets[10] == K)
    assert(Milieu(B, C) in p.cotes[1])
    assertAlmostEqual(p.centre.coordonnees, Barycentre(A, B, C, D, E, F, G, H, I, J, K).coordonnees)
    # cas particuliers :
    t = Polygone(A, B, C)
    O = t.centre_cercle_circonscrit
    assertAlmostEqual(Segment(O, A).longueur, Segment(O, C).longueur)
    assert(Droite(t.orthocentre, C).perpendiculaire(Droite(A, B)))
    assert(t.__class__ is Triangle)
    p = Polygone(A, B, C,  D)
    assert(p.__class__ is Quadrilatere)
    p = Polygone(A, B, C,  D, E)
    assert(p.__class__ is Pentagone)
    p = Polygone(A, B, C,  D, E, F)
    assert(p.__class__ is Hexagone)
    p = Polygone(A, B, C,  D, E, F, G)
    assert(p.__class__ is Heptagone)
    p = Polygone(A, B, C,  D, E, F, G, H)
    assert(p.__class__ is Octogone)
    assert(p._hierarchie < p.sommets[0]._hierarchie < p.sommets[1]._hierarchie < p.sommets[7]._hierarchie < p._hierarchie + 1)
    # Test keyword 'points'
    p = Polygone(points = (A, B, C, D, E, F, G, H, I, J, K))
    assert(p.centre.coordonnees == p0.centre.coordonnees)
    assert("points" not in p.style())
    # Syntaxe spéciale : Polygone créé sans arguments, ou avec un entier comme argument.
    p = Polygone()
    p = Polygone(2)
    assert(isinstance(p, Segment))
    p = Polygone(3)
    assert(isinstance(p, Triangle))
    p = Polygone(n = 5)
    assert(isinstance(p, Pentagone))
    p = Polygone(n = 12)
    assert(len(p.points) == 12)
    p = Polygone(23)
    assert(len(p.points) == 23)
    assert(len(str(p.points)) < 30000)


def test_Triangle():
    A = rand_pt()
    B = rand_pt()
    C = rand_pt()
    t = Triangle(A, B, C)
    O = t.centre_cercle_circonscrit
    assertAlmostEqual(Segment(O, A).longueur, Segment(O, C).longueur)

def test_Quadrilatere():
    A = rand_pt()
    B = rand_pt()
    C = rand_pt()
    D = rand_pt()
    p = Quadrilatere(A, B, C, D)
    assertAlmostEqual(p.centre.coordonnees, Barycentre(A, B, C, D).coordonnees)

def test_Pentagone():
    A = rand_pt()
    B = rand_pt()
    C = rand_pt()
    D = rand_pt()
    E = rand_pt()
    p = Pentagone(A, B, C, D, E)
    assertAlmostEqual(p.centre.coordonnees, Barycentre(A, B, C, D, E).coordonnees)

def test_Hexagone():
    A = rand_pt()
    B = rand_pt()
    C = rand_pt()
    D = rand_pt()
    E = rand_pt()
    F = rand_pt()
    p = Hexagone(A, B, C, D, E, F)
    assertAlmostEqual(p.centre.coordonnees, Barycentre(A, B, C, D, E, F).coordonnees)

def test_Heptagone():
    A = rand_pt()
    B = rand_pt()
    C = rand_pt()
    D = rand_pt()
    E = rand_pt()
    F = rand_pt()
    G = rand_pt()
    p = Heptagone(A, B, C, D, E, F, G)
    assertAlmostEqual(p.centre.coordonnees, Barycentre(A, B, C, D, E, F, G).coordonnees)

def test_Octogone():
    A = rand_pt()
    B = rand_pt()
    C = rand_pt()
    D = rand_pt()
    E = rand_pt()
    F = rand_pt()
    G = rand_pt()
    H = rand_pt()
    p = Octogone(A, B, C, D, E, F, G, H)
    assertAlmostEqual(p.centre.coordonnees, Barycentre(A, B, C, D, E, F, G, H).coordonnees)

def test_Parallelogramme():
    A = rand_pt()
    B = rand_pt()
    C = rand_pt()
    p = Parallelogramme(A, B, C)
    D = p.sommets[3]
    assertEqual(Vecteur(A, B), Vecteur(D, C))

def test_Rectangle():
    A = rand_pt()
    B = rand_pt()
    r = Rectangle(A, B)
    M, N, O, P = r.sommets
    diagonale1 = Segment(M, O)
    diagonale2 = Segment(N, P)
    assertAlmostEqual(diagonale1.longueur, diagonale2.longueur)
    cote = Droite(M, N)
    cote_oppose = Droite(O, P)
    assert(cote.parallele(cote_oppose))

def test_Losange():
    A = rand_pt()
    B = rand_pt()
    l = Losange(A, B)
    M, N, O, P = l.sommets
    diagonale1 = Droite(M, O)
    diagonale2 = Droite(N, P)
    assert(diagonale1.perpendiculaire(diagonale2))
    cote = Droite(M, N)
    cote_oppose = Droite(O, P)
    assert(cote.parallele(cote_oppose))

def test_Polygone_regulier_centre():
    O = rand_pt()
    M = rand_pt()
    p = Polygone_regulier_centre(O, M, 15)
    assert(len(p.cotes) == 15)
    assert(p.centre is O)
    for Mi in p.sommets:
        assertAlmostEqual(Segment(O, Mi).longueur, Segment(O, M).longueur)
    for i in xrange(10):
        coeffs = tuple(random() for i in xrange(15))
        G = Barycentre(*zip(p.sommets, coeffs))
        assert(G in p)
        G.points_ponderes[randint(11)].coefficient = -5
        assert(G not in p)
    # cas particuliers :
    p = Polygone_regulier_centre(O, M, 3)
    assert(isinstance(p,  Triangle))
    p = Polygone_regulier_centre(O, M, 4)
    assert(isinstance(p,  Quadrilatere))
    assert(len(str(p.points)) < 30000)

def test_Triangle_equilateral_centre():
    O = rand_pt()
    M = rand_pt()
    p = Triangle_equilateral_centre(O, M)
    assert(p.centre.existe and p.centre is O)
    assert(p.centre_cercle_circonscrit.existe)
    assert(p.centre_cercle_inscrit.existe)
    assert(p.orthocentre.existe)
    assert(p.orthocentre == p.centre == p.centre_cercle_circonscrit == p.centre_cercle_inscrit)

def test_Triangle_isocele_rectangle():
    t = Triangle_isocele_rectangle((0, 0), (1, 1))
    assertAlmostEqual(t.point3.xy, (0, 1))
    assertAlmostEqual(t.aire, .5)

def test_Carre_centre():
    O = rand_pt()
    M = rand_pt()
    p = Carre_centre(O, M)
    assert(p.centre.existe and p.centre is O)
    assert(len(p.cotes) == 4)
    assertAlmostEqual(p.aire,  p.cotes[0].longueur**2)

def test_Polygone_regulier():
    O = rand_pt()
    M = rand_pt()
    p = Polygone_regulier(O, M, 15)
    assert(len(p.cotes) == 15)
    assert(p.centre in Mediatrice(O, M))
    for i in xrange(15):
        assertAlmostEqual(Segment(p.sommets[i%15], p.sommets[(i+1)%15]).longueur, Segment(p.sommets[(i+2)%15], p.sommets[(i+3)%15]).longueur)
    p = Polygone_regulier(O, M, 3)
    assert(isinstance(p,  Triangle))
    p = Polygone_regulier(O, M, 4)
    assert(isinstance(p,  Quadrilatere))
    # Test de régression :
    # la taille de str(p.points) croissait exponentiellement.
    assert(len(str(p.points)) < 30000)


def test_Triangle_equilateral():
    O = rand_pt()
    M = rand_pt()
    p = Triangle_equilateral(O, M)
    assert(p.centre.existe)
    assert(p.centre_cercle_circonscrit.existe)
    assert(p.centre_cercle_inscrit.existe)
    assert(p.orthocentre.existe)
    assert(p.orthocentre == p.centre == p.centre_cercle_circonscrit == p.centre_cercle_inscrit)

def test_Carre():
    O = rand_pt()
    M = rand_pt()
    p = Carre(O, M)
    A, B, C, D = p.sommets
    assert(p.centre == Milieu(A, C) == Milieu(B, D))
    assert(A == O and B == M)
    assert(len(p.cotes) == 4)
    assertAlmostEqual(p.aire,  p.cotes[0].longueur**2)
    # Test redéfinition d'un sommet
    c = Carre((3, 2), (7, 2))
    M = Point(0, 2)
    c.point1 = M
    assert(c.point1 is M)
    assert(c.regulier)
    assertAlmostEqual(c.aire, 49)
    assertAlmostEqual(c.point4.coordonnees, (0, 9))

def test_Triangle_isocele():
    A = rand_pt()
    B = rand_pt()
    tri = Triangle_isocele(A, B, 2*pi/13)
    C = tri.point3
    a = Angle(B, A, C)
    assertAlmostEqual(a.radian, 2*pi/13)
    assertAlmostEqual(Segment(A, B).longueur, Segment(A, C).longueur)
    t1 = Triangle_isocele((0, 0), (1, 1), u'90°')
    assertAlmostEqual(t1.point3.xy, (-1, 1))
    t2 = Triangle_isocele((0, 0), (2, 0), pi/3)
    assertAlmostEqual(t2.point3.xy, (2*cos(pi/3), 2*sin(pi/3)))

def test_Triangle_rectangle():
    t = Triangle_rectangle(rand_pt(), rand_pt(), pi/7)
    a = Angle(t.point1, t.point3, t.point2)
    assertAlmostEqual(a.degre, 90)
