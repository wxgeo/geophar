# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

#from tools.testlib import assertAlmostEqual
from wxgeometrie.geolib.tests.geotestlib import rand_pt
from wxgeometrie.geolib import (Point, Interpolation_polynomiale_par_morceaux,
                                Glisseur_courbe_interpolation, Interpolation_lineaire,
                                Translation,)


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


def test_Interpolation_polynomiale_par_morceaux():
    A = Point(-5.9897435897435898, -1.1319690410599499)
    B = Point(-3.6911010558069393, 2.3942017578381218)
    C = Point(-0.50558069381598791, -1.0768726223271674)
    D = Point(2.6437405731523356, 1.1545323363505182)
    inter = Interpolation_polynomiale_par_morceaux(A, B, C, D)
    M = Glisseur_courbe_interpolation(inter, M)
