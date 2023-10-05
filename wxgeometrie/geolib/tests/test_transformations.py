# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

from random import random, randint
from math import pi

import wx_unittest
from wxgeometrie.geolib import (
    Point, Droite, Droite_equation, Reflexion, Rotation, Translation,
    Homothetie, Symetrie_centrale, Milieu, Mediatrice, Vecteur_libre
)

class TestGelolib(wx_unittest.TestCase):

    def test_Rotation(self):
        A = Point(1.523, 45.35211)
        r = Rotation(A, pi/4)
        M = Point(1.4452,  -1.2545)
        self.assertAlmostEqual(r(M).coordonnees, (34.423837071540447, 12.341247113306926))
        self.assertAlmostEqual(r(A).coordonnees, A.coordonnees)
        d = Droite(A, M)
        d1 = Droite(A, r(M))
        self.assertAlmostEqual(r(d).equation_reduite, d1.equation_reduite)
        self.assertIs(r(A), A)


    def test_Translation(self):
        v = Vecteur_libre(random()+randint(0,50)-randint(0,50), random()+randint(0,50)-randint(0,50))
        t = Translation(v)
        M = Point(random()+randint(0,50)-randint(0,50), random()+randint(0,50)-randint(0,50))
        self.assertAlmostEqual(M.x + v.x, t(M).x)
        self.assertAlmostEqual(M.y + v.y, t(M).y)


    def test_Reflexion(self):
        d = Droite_equation(1, 6, -2)
        r = Reflexion(d)
        M = Point(random()+randint(0,50)-randint(0,50), random()+randint(0,50)-randint(0,50))
        m = Mediatrice(M,  r(M))
        self.assertAlmostEqual(d.equation_reduite[0],  m.equation_reduite[0])
        self.assertAlmostEqual(d.equation_reduite[1],  m.equation_reduite[1])
        self.assertIs(r(d), d)

    def test_Homothetie(self):
        A = Point(1, -2)
        h = Homothetie(A, -3)
        M = Point(2, 7)
        self.assertAlmostEqual(h(M).coordonnees, (-2, -29))
        self.assertIs(h(A), A)


    def test_Symetrie_centrale(self):
        M = Point(random()+randint(0,50)-randint(0,50), random()+randint(0,50)-randint(0,50))
        A = Point(random()+randint(0,50)-randint(0,50), random()+randint(0,50)-randint(0,50))
        s = Symetrie_centrale(A)
        self.assertAlmostEqual(Milieu(M, s(M)).coordonnees[0], A.coordonnees[0])
        self.assertAlmostEqual(Milieu(M, s(M)).coordonnees[1], A.coordonnees[1])
        self.assertIs(s(A), A)
