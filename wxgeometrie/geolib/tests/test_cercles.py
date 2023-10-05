# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

from math import sqrt, sin, cos
from random import random

import tools.unittest, unittest

from wxgeometrie.geolib import (
    Cercle_points, Cercle_diametre, Cercle_rayon, Demicercle,
    Arc_oriente, Arc_points, Label_arc_cercle, Disque,
    Label_cercle, Rayon, Point, Cercle, Milieu, Segment,
    Mediatrice, Arc_cercle, Cercle_equation,
)

class GeolibTest(tools.unittest.TestCase):
    def test_Arc_cercle(self):
        A = Point(-1.2561, 45.236)
        B = Point(251.2561, 41.256)
        O = Point(-42.25, 2.351)
        a = Arc_cercle(O, A, B)
        self.assertIsInstance(a.etiquette, Label_arc_cercle)
        self.assertIn(A, a)
        self.assertNotIn(B, a)
        self.assertNotIn(O, a)


    def test_Arc_points(self):
        A = Point(-1.2561, 45.236)
        B = Point(251.2561, 41.256)
        C = Point(-42.25, 2.351)
        a = Arc_points(A, B, C)
        self.assertIn(A, a)
        self.assertIn(B, a)
        self.assertIn(C, a)
        self.assertAlmostEqual(a.longueur, 1208.25931027)
        self.assertAlmostEqual(
            a.centre.coordonnees, (122.51970100911581, -114.11725498641933))

    def test_Arc_oriente(self):
        A = Point(-1.2561, 45.236)
        B = Point(251.2561, 41.256)
        C = Point(-42.25, 2.351)
        a = Arc_oriente(A, B, C)
        self.assertIn(A, a)
        self.assertIn(B, a)
        self.assertIn(C, a)
        self.assertAlmostEqual(a.longueur, 1208.25931027)
        self.assertAlmostEqual(
            a.centre.coordonnees, (122.51970100911581, -114.11725498641933))
        self.assertEqual(a.sens, "indirect")

    def test_Demicercle(self):
        A = Point(-1.2561, 45.236)
        B = Point(251.2561, 41.256)
        c = Demicercle(A, B)
        self.assertAlmostEqual(Milieu(A, B).coordonnees, c.centre.coordonnees)
        self.assertAlmostEqual(c.diametre, Segment(A, B).longueur)
        self.assertAlmostEqual(c.rayon, Segment(A, B).longueur/2)

    def test_Cercle_rayon(self):
        A = Point(-2.586, 7.541)
        c_1 = Cercle_rayon(A, -1)
        c0 = Cercle_rayon(A, 0)
        c2 = Cercle_rayon(A, 2)
        self.assertIsInstance(c_1.etiquette, Label_cercle)
        self.assertFalse(c_1.existe)
        self.assertTrue(c0.existe)
        self.assertTrue(c2.existe)
        self.assertAlmostEqual(A.coordonnees, c0.centre.coordonnees)
        self.assertNotIn(A, c_1)
        self.assertIn(A, c0)
        self.assertNotIn(A, c2)
        self.assertEqual(c_1.rayon,  -1)
        self.assertEqual(c0.rayon,  0)
        self.assertEqual(c2.rayon,  2)
        k = random()
        B = Point(A.x + 2*sin(k),  A.y + 2*cos(k))
        self.assertIn(B, c2)

    @unittest.expectedFailure
    def test_cercle_defini_par_equation(self):
        c = Cercle("x^2+y^2-2x+y-3=0")
        self.assertAlmostEqual(c.centre.xy, (1, -.5))
        self.assertAlmostEqual(c.rayon, sqrt(4.25))

    def test_Cercle(self):
        A = Point(2.78841, -5.25)
        O = Point(27.8841, -0.525)
        c = Cercle(O, A)
        self.assertIs(c.centre, O)
        self.assertIs(c.point, A)
        self.assertAlmostEqual(c.rayon, 25.5366262763)
       # Test du typage dynamique
        c = Cercle(Point(1, 1), 1)
        self.assertIn(Point(1, 2), c)
        c = Cercle(Point(1, 1), Point(0, 2), Point(-1, 1))
        self.assertIn(Point(0, 0), c)
        self.assertAlmostEqual(c.centre.coordonnees, (0, 1))

    def test_Cercle_diametre(self):
        A = Point(2.78841, -5.25)
        B = Point(27.8841, -0.525)
        c = Cercle_diametre(A, B)
        c1 = Cercle(A, B)
        self.assertAlmostEqual(c.diametre, c1.rayon)
        self.assertAlmostEqual(c.diametre, Segment(A, B).longueur)
        self.assertAlmostEqual(c.centre.coordonnees, Milieu(A, B).coordonnees)

    def test_Cercle_points(self):
        A = Point(2.78841, -5.25)
        B = Point(27.8841, -0.525)
        C = Point(-42.25, 2.351)
        c = Cercle_points(A, B, C)
        self.assertIn(c.centre, Mediatrice(Segment(A, B)))
        self.assertIn(c.centre, Mediatrice(Segment(A, C)))


    def test_Cercle_equation(self):
        c = Cercle_equation()
        self.assertAlmostEqual(c.centre.coordonnees, (0, 0))
        self.assertEqual(c.rayon, 1)
        c.a = -2
        c.b = 4
        c.c = -4
        self.assertAlmostEqual(c.centre.coordonnees, (1, -2))
        self.assertEqual(c.rayon, 3)
        self.assertTrue(c.existe)
        c.c = 6
        self.assertFalse(c.existe)


    def test_Disque(self):
        A = Point(2.78841, -5.25)
        B = Point(27.8841, -0.525)
        C = Point(-42.25, 2.351)
        c = Cercle_points(A, B, C)
        d = Disque(c)
        self.assertAlmostEqual(d.centre.coordonnees, c.centre.coordonnees)
        self.assertAlmostEqual(d.rayon, c.rayon)
        self.assertIn(A, d)
        self.assertIn(B, d)
        self.assertIn(C, d)
        self.assertIn(d.centre, d)
        self.assertNotIn(Point(-500, -500), d)

    def test_equation_formatee(self):
        self.assertEqual(
            Cercle((10, 0), (1, 5)).equation_formatee,
            'x\xb2 + y\xb2 - 20 x - 6 = 0')

    def test_Rayon(self):
        c = Cercle((1, 1), (4, 5))
        r = Rayon(c)
        self.assertAlmostEqual(r.val, 5)
        c.point.x = 1
        self.assertAlmostEqual(r.val, 4)
