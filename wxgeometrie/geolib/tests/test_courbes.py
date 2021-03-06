# -*- coding: utf-8 -*-

from pytest import XFAIL

from wxgeometrie.geolib import Point, Fonction, Interpolation_polynomiale_par_morceaux, \
                                Glisseur_courbe, Interpolation_lineaire, Courbe


def test_Courbe():
    f = Fonction('1/(x+3)')
    c1 = Courbe(f)
    assert isinstance(c1, Courbe)
    A = Point(0, 0)
    B = Point(-1, 2)
    C = Point(4, 3)
    D = Point(-3, 1)
    E = Point(4, 5)
    c2 = Courbe(A, B, C, D, E)
    try:
        import scipy
        assert isinstance(c2, Interpolation_polynomiale_par_morceaux), type(c2)
    except ImportError:
        assert isinstance(c2, Interpolation_lineaire)

