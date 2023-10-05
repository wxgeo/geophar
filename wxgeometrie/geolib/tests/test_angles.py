# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

from random import random
import math

from wxgeometrie.geolib import (
    Feuille, Angle_oriente, Angle_vectoriel, Angle_libre,
    Secteur_angulaire, Label_angle, Vecteur_libre,
    Point, Angle, Variable, contexte,
)
from wxgeometrie.mathlib.universal_functions import sin as u_sin, cos as u_cos, tan as u_tan

import wx_unittest

class GeolibTest(wx_unittest.TestCase):

    def test_Secteur_angulaire(self):
        u = Vecteur_libre(5.458, -2.546)
        v = Vecteur_libre(-5.75, 12.6)
        P = Point(2.54, -5.68)
        a = Secteur_angulaire(P, u, v)
        self.assertIsInstance(a.etiquette, Label_angle)
        self.assertAlmostEqual(a.val, 2.43538435941)
        self.assertAlmostEqual(a.degre, 139.537245287)

    def test_Angle_oriente(self):
        A = Point(250.54, 612.78)
        B = Point(115.54, 168.24)
        C = Point(412.78, -254.23)
        a = Angle_oriente(A, B, C)
        self.assertAlmostEqual(a.rad, -2.2336365048)

    def test_Angle(self):
        A = Point(250.54, 612.78)
        B = Point(115.54, 168.24)
        C = Point(412.78, -254.23)
        a = Angle(A, B, C)
        self.assertAlmostEqual(a.rad, +2.2336365048)

    def test_Angle_libre(self):
        x = random()
        a = Angle_libre(x)
        self.assertAlmostEqual(a.deg, x*180/math.pi)
        self.assertAlmostEqual(a.grad, x*200/math.pi)
        self.assertAlmostEqual(a.rad, x)
        self.assertAlmostEqual(a.val, x)
        self.assertAlmostEqual(math.sin(a.val), math.sin(x))
        self.assertAlmostEqual(math.cos(a.val), math.cos(x))
        self.assertAlmostEqual(math.tan(a.val), math.tan(x))
        y = x*180/math.pi
        a = Angle_libre(y, "°")
        self.assertAlmostEqual(a.deg, y)
        self.assertAlmostEqual(a.grad, x*200/math.pi)
        self.assertAlmostEqual(a.rad, x)
        self.assertNotAlmostEqual(a.val, a.deg)
        self.assertAlmostEqual(u_sin(a.val), math.sin(x))
        self.assertAlmostEqual(u_cos(a.val), math.cos(x))
        self.assertAlmostEqual(u_tan(a.val), math.tan(x))
        a.style(unite="g")
        self.assertNotAlmostEqual(a.val, a.grad)
        b = Angle_libre("45°")
        self.assertAlmostEqual(b.rad, math.pi/4)
        f = Feuille()
        f.objets.A = Point(40, 20)
        f.objets.k = Variable("A.x+5")
        f.objets.c = Angle_libre(f.objets.k, "d")
        f.objets.d = Angle_libre("A.x+5", "d")
        self.assertIsNotNone(f.objets.c.rad)
        self.assertAlmostEqual(b.rad, f.objets.c.rad)
        self.assertAlmostEqual(f.objets.d.rad, f.objets.c.rad)

    def test_Angle_vectoriel(self):
        u = Vecteur_libre(5.458, -2.546)
        v = Vecteur_libre(-5.75, 12.6)
        a = Angle_vectoriel(u, v)
        self.assertAlmostEqual(a.val, 2.43538435941)

    def test_contexte_degre(self):
        with contexte(unite_angle='d'):
            a = Angle_libre('pi rad')
            self.assertAlmostEqual(a.deg, 180)
            a = Angle_libre('100 grad')
            self.assertAlmostEqual(a.deg, 90)
            b = Angle_libre(30)
            self.assertAlmostEqual(b.rad, math.pi/6)
            # En interne, tout doit être stocké en radians
            self.assertEqual(float(b.val), float(b.rad))
            # On doit avoir eval(repr(b)) == b
            self.assertAlmostEqual(eval(repr(b)).deg, 30)

    def test_info(self):
        a = Angle_libre("30°")
        self.assertEqual(str(a.deg), '30')
        with contexte(unite_angle='d'):
            self.assertEqual(a.info, 'Angle de valeur 30°')
        with contexte(unite_angle='r'):
            self.assertEqual(a.info, 'Angle de valeur pi/6 rad')
        with contexte(unite_angle='g'):
            self.assertEqual(a.info, 'Angle de valeur 100/3 grad')
