# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from random import random
from math import sqrt

from tools.testlib import assertAlmostEqual, assertEqual
from wxgeometrie.geolib import Point, Vecteur_unitaire, Vecteur, Vecteur_libre, Representant, Label_vecteur, Somme_vecteurs


def setUp():
    pass

def test_Vecteur():
    A=Point(1,2)
    B=Point(2,4)
    v=Vecteur(A, B)
    assert(isinstance(v.etiquette, Label_vecteur))
    assert(v.x == 1 and v.y == 2)
    assertEqual(v.norme,  sqrt(5))
    assertEqual(type(v.coordonnees),  tuple)
    # Test du typage dynamique :
    assert(isinstance(Vecteur(1, 3), Vecteur_libre))
    assert(Vecteur(1, 3).coordonnees == (1, 3))



def test_Vecteur_libre():
    u = Vecteur_libre(1, -2)
    u.y = -3
    assertEqual(u.norme,  sqrt(10))
    assertEqual(type(u.coordonnees),  tuple)


def test_Representant():
    A=Point(1,2)
    B=Point(2,4)
    v=Vecteur(A, B)
    w = Representant(v,  B)
    assert(w.x == v.x and w.y == v.y and w.z == v.z)
    assert(w.origine == v.point2)
    assertEqual(type(w.coordonnees),  tuple)
    assertAlmostEqual(w.extremite.coordonnees, (3, 6))
    assert(w._hierarchie < w.extremite._hierarchie < w._hierarchie + 1)

def test_Vecteur_unitaire():
    u = Vecteur_unitaire(Vecteur_libre(random(), random()))
    assertAlmostEqual(u.norme,  1)
    assertEqual(type(u.coordonnees),  tuple)

def test_Somme_vecteurs():
    A=Point(1,2)
    B=Point(2,4)
    v=Vecteur(A, B)
    w=Vecteur_libre(-4, 5)
    u=Representant(v, Point(1, 2))
    vec = 2*u+1*v
    vec -= 5*w
    assert(tuple(vec.coordonnees) == (23, -19))
    assertEqual(type(vec.coordonnees),  tuple)
    assertEqual(vec.coordonnees,  Somme_vecteurs((u, v, w), (2, 1, -5)).coordonnees)
