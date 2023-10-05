# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

import tools.unittest
from random import random
from math import sqrt

from wxgeometrie.geolib import (
    Point, Vecteur_unitaire, Vecteur, Vecteur_libre,
    Representant, Label_vecteur, Somme_vecteurs,
    Extremite
)

class TestGeolib(tools.unittest.TestCase):

    def setUp(self):
        pass

    def test_Vecteur(self):
        A=Point(1,2)
        B=Point(2,4)
        v=Vecteur(A, B)
        self.assertIsInstance(v.etiquette, Label_vecteur)
        self.assertEqual(v.x, 1)
        self.assertEqual(v.y, 2)
        self.assertEqual(v.norme,  sqrt(5))
        self.assertEqual(type(v.coordonnees),  tuple)
        # Test du typage dynamique :
        self.assertIsInstance(Vecteur(1, 3), Vecteur_libre)
        self.assertEqual(Vecteur(1, 3).coordonnees, (1, 3))

    def test_Vecteur_libre(self):
        u = Vecteur_libre(1, -2)
        u.y = -3
        self.assertEqual(u.norme,  sqrt(10))
        self.assertEqual(type(u.coordonnees),  tuple)

    def test_Representant(self):
        A=Point(1,2)
        B=Point(2,4)
        v=Vecteur(A, B)
        w = Representant(v,  B)
        self.assertEqual(w.x, v.x)
        self.assertEqual(w.y, v.y)
        self.assertEqual(w.z, v.z)
        self.assertEqual(w.origine, v.point2)
        self.assertEqual(type(w.coordonnees),  tuple)
        self.assertAlmostEqual(w.extremite.coordonnees, (3, 6))
        self.assertTrue(w._hierarchie < w.extremite._hierarchie < w._hierarchie + 1)

    def test_Vecteur_unitaire(self):
        u = Vecteur_unitaire(Vecteur_libre(random(), random()))
        self.assertAlmostEqual(u.norme,  1)
        self.assertEqual(type(u.coordonnees),  tuple)

    def test_Somme_vecteurs(self):
        A=Point(1,2)
        B=Point(2,4)
        v=Vecteur(A, B)
        w=Vecteur_libre(-4, 5)
        u=Representant(v, Point(1, 2))
        vec = 2*u+1*v
        vec -= 5*w
        self.assertEqual(tuple(vec.coordonnees), (23, -19))
        self.assertEqual(type(vec.coordonnees),  tuple)
        self.assertEqual(vec.coordonnees,
                         Somme_vecteurs((u, v, w), (2, 1, -5)).coordonnees)

    def test_Extremite(self):
        v=Vecteur_libre(-4.2, -6.7)
        w = Representant(v)
        A = w.origine
        B = w.extremite
        self.assertAlmostEqual(B.x - A.x, v.x)
        self.assertAlmostEqual(B.y - A.y, v.y)
        C = Extremite(w, couleur = 'purple')
        self.assertIs(C, B)
        self.assertEqual(C.style('couleur'), 'purple')

if __name__ == '__main__':
    unittest.main()
