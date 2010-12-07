# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from geolib.tests.geotestlib import *
from geolib import Interpolation_lineaire


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

