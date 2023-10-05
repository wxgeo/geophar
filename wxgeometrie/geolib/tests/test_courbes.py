# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

from wxgeometrie.geolib import (
    Point, Fonction, Interpolation_polynomiale_par_morceaux,
    Glisseur_courbe, Interpolation_lineaire, Courbe
)

import tools.unittest

class GeolibTest(tools.unittest.TestCase):

    def test_Courbe(self):
        f = Fonction('1/(x+3)')
        c1 = Courbe(f)
        self.assertIsInstance(c1, Courbe)
        A = Point(0, 0)
        B = Point(-1, 2)
        C = Point(4, 3)
        D = Point(-3, 1)
        E = Point(4, 5)
        c2 = Courbe(A, B, C, D, E)
        try:
            import scipy
            self.assertIsInstance(c2, Interpolation_polynomiale_par_morceaux)
        except ImportError:
            self.assertIsInstance(c2, Interpolation_lineaire)

