# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

import wx_unittest
from wxgeometrie.geolib.tests.geotestlib import rand_dte, rand_pt
from wxgeometrie.geolib import (
    Intersection_droite_cercle, Intersection_cercles,
    Point, Droite,
    Intersection_droites, Parallele, Feuille, Cercle,
    Mediatrice, Segment,
)

class GeolibTest(wx_unittest.TestCase):
    def test_Intersection_droites(self):
        d1 = rand_dte()
        d2 = rand_dte()
        A = Intersection_droites(d1, d2)
        if not d1.parallele(d2):
            self.assertTrue(A in d1 and A in d2)
        d3 = Parallele(d1, rand_pt())
        self.assertFalse(Intersection_droites(d1, d3).existe)
        D = Point(-14.201335283549275, 1.5093204196583834)
        U = Point(-14.201335283549273, 17.644024286752096)
        d = Droite(U, D)
        s = Segment(U, D)
        V = Point(1.933368583544437, 7.5065025053891166)
        W = Point(7.1347038670937115, 8.3895493390615954)
        d2 = Droite(W, V)
        M1 = Intersection_droites(s, d2)
        M2 = Intersection_droites(d, d2)
        self.assertTrue(M1.existe)
        self.assertTrue(M2.existe)

    def test_Intersection_droite_cercle(self):
        A = Point(-3.075, 2.0)
        B = Point(0.0, 1.625)
        c1 = Cercle(A, B)
        C = Point(-0.375, 4.425)
        D = Point(3.25, 0.125)
        d1 = Droite(C, D)
        self.assertFalse(Intersection_droite_cercle(d1, c1).existe)
        C(-5.675, 4.95)
        I = Intersection_droite_cercle(d1, c1, True)
        self.assertTrue(I.egal((-4.87791007862, 4.51908023858)))
        J = Intersection_droite_cercle(d1, c1, False)
        self.assertTrue(J.egal((0.0201000262814, 1.87113640036)))



    def test_Intersection_cercles(self):
        A = Point(-4.4375, 1.95833333333)
        B = Point(-2.10416666667, 0.875)
        c1 = Cercle(A, B)
        C = Point(2.1875, 1.35416666667)
        c2 = Cercle(C,B)
        D = Intersection_cercles(c2, c1, False)
        self.assertTrue(D.egale((-1.9466976004889973, 2.6017297602107377)))
        self.assertTrue(Intersection_cercles(c2, c1, True).egale(B))
        self.assertTrue( Droite(A, C).confondu(Mediatrice(B, D)))

    def test_intersection_et_feuille(self):
        """On teste que par défaut, le deuxième d'intersection soit différent du premier."""
        f = Feuille()
        f.objets._ = Point(-5.11060948081, 0.144469525959)
        f.objets._ = Point(-3.97291196388, 0.794582392777)
        f.objets._ = Cercle(f.objets.M1, f.objets.M2)
        f.objets._ = Point(-3.26862302483, -1.10158013544)
        f.objets._ = Point(-5.79683972912, 2.41986455982)
        f.objets._ = Droite(f.objets.M3, f.objets.M4)
        f.objets._ = Intersection_droite_cercle(f.objets.d1, f.objets.c1, True)
        f.objets._ = Intersection_droite_cercle(f.objets.d1, f.objets.c1)
        # On vérifie qu'on a bien obtenu le 2e point d'intersection (et non deux fois de suite le même)
        self.assertFalse(f.objets.M6.premier_point)

    def test_intersections_non_deplacables(self):
        d1 = rand_dte()
        d2 = rand_dte()
        A = Intersection_droites(d1, d2)
        self.assertFalse(A._modifiable)
        self.assertFalse(A._deplacable)
