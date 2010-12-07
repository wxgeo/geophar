# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from geolib.tests.geotestlib import *

import geolib
from geolib import (Angle_oriente, Angle_vectoriel, Angle_libre,
                                Secteur_angulaire, univ, Label_angle,
                                )

def test_Secteur_angulaire():
    u = Vecteur_libre(5.458, -2.546)
    v = Vecteur_libre(-5.75, 12.6)
    P = Point(2.54, -5.68)
    a = Secteur_angulaire(P, u, v)
    assert(isinstance(a.etiquette, Label_angle))
    assertAlmostEqual(a.val, 2.43538435941)
    assertAlmostEqual(a.degre, 139.537245287)

def test_Angle_oriente():
    A = Point(250.54, 612.78)
    B = Point(115.54, 168.24)
    C = Point(412.78, -254.23)
    a = Angle_oriente(A, B, C)
    assertAlmostEqual(a.rad, -2.2336365048)

def test_Angle():
    A = Point(250.54, 612.78)
    B = Point(115.54, 168.24)
    C = Point(412.78, -254.23)
    a = Angle(A, B, C)
    assertAlmostEqual(a.rad, +2.2336365048)

def test_Angle_libre():
    x = random()
    a = Angle_libre(x)
    assertAlmostEqual(a.deg, x*180/math.pi)
    assertAlmostEqual(a.grad, x*200/math.pi)
    assertAlmostEqual(a.rad, x)
    assertAlmostEqual(a.val, x)
    assertAlmostEqual(math.sin(a.val), math.sin(x))
    assertAlmostEqual(math.cos(a.val), math.cos(x))
    assertAlmostEqual(math.tan(a.val), math.tan(x))
    y = x*180/math.pi
    a = Angle_libre(y, u"°")
    assertAlmostEqual(a.deg, y)
    assertAlmostEqual(a.grad, x*200/math.pi)
    assertAlmostEqual(a.rad, x)
    assertNotAlmostEqual(a.val, a.deg)
    sin = univ.sin
    cos = univ.cos
    tan = univ.tan
    assertAlmostEqual(sin(a), math.sin(x))
    assertAlmostEqual(cos(a), math.cos(x))
    assertAlmostEqual(tan(a), math.tan(x))
    a.unite = "g"
    assertNotAlmostEqual(a.val, a.grad)
    b = Angle_libre(u"45°")
    assertAlmostEqual(b.rad, math.pi/4)
##        print "%% FEUILLE %%"
##        f = geolib.Feuille()
##        print f, type(f)
##        p = Point(40, 20)
##        print p,  type(p), id(p)
##        f.objets.A = p
##        print f.objets.A, type(f.objets.A), id(f.objets.A)
##        v = Variable("A.x+5")
##        print v, type(v)
##        f.objets.k = v
##        f.objets.c = Angle_libre(f.objets.k, "d")
##        assertAlmostEqual(b.rad, c.rad)
    f = geolib.Feuille()
    f.objets.A = geolib.Point(40, 20)
    f.objets.k = geolib.Variable("A.x+5")
    f.objets.c = geolib.Angle_libre(f.objets.k, "d")
    f.objets.d = geolib.Angle_libre("A.x+5", "d")
    assert(f.objets.c.rad is not None)
    assertAlmostEqual(b.rad, f.objets.c.rad)
    assertAlmostEqual(f.objets.d.rad, f.objets.c.rad)


def test_Angle_vectoriel():
    u = Vecteur_libre(5.458, -2.546)
    v = Vecteur_libre(-5.75, 12.6)
    a = Angle_vectoriel(u, v)
    assertAlmostEqual(a.val, 2.43538435941)