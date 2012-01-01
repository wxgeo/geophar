# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

#from tools.testlib import assertAlmostEqual
from wxgeometrie.geolib.tests.geotestlib import rand_dte, rand_pt
from wxgeometrie.geolib import (Intersection_droite_cercle, Intersection_cercles,
                                Point, Droite,
                                Intersection_droites, Parallele, Feuille, Cercle,
                                Mediatrice, Segment,
                                )

def test_Intersection_droites():
    d1 = rand_dte()
    d2 = rand_dte()
    A = Intersection_droites(d1, d2)
    if not d1.parallele(d2):
        assert(A in d1 and A in d2)
    d3 = Parallele(d1, rand_pt())
    assert(not Intersection_droites(d1, d3).existe)
    D = Point(-14.201335283549275, 1.5093204196583834)
    U = Point(-14.201335283549273, 17.644024286752096)
    d = Droite(U, D)
    s = Segment(U, D)
    V = Point(1.933368583544437, 7.5065025053891166)
    W = Point(7.1347038670937115, 8.3895493390615954)
    d2 = Droite(W, V)
    M1 = Intersection_droites(s, d2)
    M2 = Intersection_droites(d, d2)
    assert(M1.existe)
    assert(M2.existe)

def test_Intersection_droite_cercle():
    A = Point(-3.075, 2.0, legende=2)
    B = Point(0.0, 1.625, legende=2)
    c1 = Cercle(A, B)
    C = Point(-0.375, 4.425, legende=2)
    D = Point(3.25, 0.125, legende=2)
    d1 = Droite(C, D)
    assert(not Intersection_droite_cercle(d1, c1).existe)
    C(-5.675, 4.95)
    I = Intersection_droite_cercle(d1, c1, True)
    assert(I == (-4.87791007862, 4.51908023858))
    J = Intersection_droite_cercle(d1, c1, False)
    assert(J == (0.0201000262814, 1.87113640036))



def test_Intersection_cercles():
    A = Point(-4.4375, 1.95833333333, legende=2)
    B = Point(-2.10416666667, 0.875, legende=2)
    c1 = Cercle(A, B)
    C = Point(2.1875, 1.35416666667, legende=2)
    c2 = Cercle(C,B)
    D = Intersection_cercles(c2, c1, False, legende=2)
    assert(D == (-1.9466976004889973, 2.6017297602107377))
    assert(Intersection_cercles(c2, c1, True, legende=2) == B)
    assert(Droite(A, C) == Mediatrice(B, D))

def test_intersection_et_feuille():
    u"""On teste que par défaut, le deuxième d'intersection soit différent du premier."""
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
    assert(f.objets.M6.premier_point == False)
