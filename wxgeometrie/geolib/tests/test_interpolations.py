# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

#from tools.testlib import assertAlmostEqual
from wxgeometrie.geolib.tests.geotestlib import rand_pt
from wxgeometrie.geolib import Interpolation_lineaire, Translation


def test_Interpolation_lineaire():
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
    assert(len(i1.points) == len(i0.points))
    assert("points" not in i1.style())
    t = Translation((1, -2))
    i2 = t(i1)
    assert i2.points[0].xy == (A.x + 1, A.y - 2)
    assert i2.points[-1].xy == (K.x + 1, K.y - 2)
