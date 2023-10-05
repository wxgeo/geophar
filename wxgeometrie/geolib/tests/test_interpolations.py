# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

import tools.unittest, unittest

from wxgeometrie.geolib.tests.geotestlib import rand_pt
from wxgeometrie.geolib import (Point, Interpolation_polynomiale_par_morceaux,
                                Glisseur_courbe, Interpolation_lineaire,
                                Translation,)

class GeolibTest(tools.unittest.TestCase):
    def test_Interpolation_lineaire(self):
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
        i0 = Interpolation_lineaire(A, B, C, D, E, F, G, H, I, J, K)
        # Test keyword "points"
        i1 = Interpolation_lineaire(points = (A, B, C, D, E, F, G, H, I, J, K))
        self.assertEqual(len(i1.points), len(i0.points))
        self.assertNotIn("points", i1.style())
        t = Translation((1, -2))
        i2 = t(i1)
        self.assertEqual(i2.points[0].xy, (A.x + 1, A.y - 2))
        self.assertEqual(i2.points[-1].xy, (K.x + 1, K.y - 2))


    @unittest.expectedFailure
    def test_Interpolation_quadratique(self):
        raise NotImplementedError


    @unittest.expectedFailure
    def test_Interpolation_cubique(self):
        raise NotImplementedError


    def test_Interpolation_polynomiale_par_morceaux(self):
        A = Point(-5.9897435897435898, -1.1319690410599499)
        B = Point(-3.6911010558069393, 2.3942017578381218)
        C = Point(-0.50558069381598791, -1.0768726223271674)
        D = Point(2.6437405731523356, 1.1545323363505182)
        inter = Interpolation_polynomiale_par_morceaux(A, B, C, D)
        M = Glisseur_courbe(inter, 2)
        self.assertEqual(M.xy[0], 2)
        P = Point(inter)
        self.assertEqual(P.y, inter.fonction(float(P.x)))
        # Sous forme de liste
        inter2 = Interpolation_polynomiale_par_morceaux([A, B, C, D])
        M = Point(inter, -7)
        self.assertTrue(M.x == min(A.x, B.x, C.x, D.x) == inter2.xmin)

