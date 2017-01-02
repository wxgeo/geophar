# -*- coding: utf-8 -*-

import re
from math import cos, pi, e, sqrt

from pytest import XFAIL

from tools.testlib import assertAlmostEqual, assertRaises, assertEqual
from wxgeometrie.geolib.tests.geotestlib import rand_pt
from wxgeometrie.geolib import (Triangle_rectangle, DescripteurFeuille, Point, Segment,
                    Vecteur, Fonction, Variable, Feuille, Angle, contexte, Arc_cercle,
                    Texte, Droite, Carre, Triangle, Polygone, Cercle, Parallelogramme,
                    Droite_equation, Cercle_equation, Courbe, Formule,
                    Representant
                    )
from wxgeometrie.geolib.routines import nice_display
from wxgeometrie.geolib.feuille import parse_equation, is_equation


def test_abreviations():
    f = Feuille(titre = "Feuille de travail n°1")
    o = f.objets

    assert("Point" in o)
    assert("Variable" in o)
    assert("Texte" in o)
    assert("point" in o)
    assert("variable" in o)
    assert("texte" in o)

    o.txt = ["salut"]
    assert(isinstance(o.txt, Texte))
    assert(o.txt.texte == "salut")
    o.s = ["Hé, ça marche !"]
    assert(isinstance(o.s, Texte))
    assert(o.s.texte == "Hé, ça marche !")

    o.A = (1, 2)
    o.k = 7
    assert(isinstance(o.A, Point))
    assert(isinstance(o.k, int))
    o.h = 'A.x'
    o.A.x = 15
    assert(o.h == 15)
    o.h = "A.x-10"
    assert(o.h == 5)
    assert(o.h - 3 == 2)
    o.h = pi/3
    assertAlmostEqual(cos(o.h), 1/2)
    o.B = (-1, 3)
    o.u = o.A>o.B
    assert(isinstance(o.u, Vecteur))
    assert(o.u.coordonnees == (o.B.x - o.A.x, o.B.y - o.A.y))
    o.C = 2-3j
    assert(isinstance(o.C, Point))
    assert(o.C.z == 2-3j)
    o.C.x = "A.x"
    #print 'o.C.x.val:', o.C.x.val, type(o.C.x.val)
    assert(isinstance(o.C.x.val, (float, int)))
    assert(o.C.x == o.A.x)
    o.A.coordonnees = -11, 3
    assert(o.C.coordonnees[0] == -11)
    o.B.x = "A.x + 1"
    assert(isinstance(o.B.x.val, (float, int)))
    assert(o.B.x == o.A.x + 1)
    o.A.coordonnees = 30, -5
    assert(o.B.coordonnees[0] == 31)
    o.A(-3.6, 0.4)
    assert(o.C.coordonnees[0] ==-3.6)
    # 'o.EFG = Triangle' doit être accepté comme alias de 'o.EFG = Triangle()'
    o.EFG = Triangle
    assert(isinstance(o.EFG, Triangle))

def test_nommage_automatique():
    f = Feuille()
    M1 = f.objets._ = Point()
    assert("M1" in f.objets)
    M2 = f.objets._ = Point(1, 3)
    assert("M2" in f.objets)
    f.objets._ = Droite(M1, M2)
    assert("d1" in f.objets)
    f.objets._ = Cercle(M1, M2)
    assert("c1" in f.objets)
    f.objets._ = Segment(M1, M2)
    assert("s1" in f.objets)

def test_noms_aleatoires():
    f = Feuille()
    f.executer('A1=(1,2)')
    f.executer('A2=(1,0)')
    M = Point()
    s = Segment()
    g = Fonction('2x+7')
    assert f.nom_aleatoire(M) == 'M1'
    assert f.nom_aleatoire(s) == 's1'
    assert f.nom_aleatoire(g) == 'f1'
    assert f.nom_aleatoire(M, prefixe='A') == 'A3'
    # f0, f1, etc. sont réservés aux fonctions
    nom = f.nom_aleatoire(M, prefixe='f')
    assert re.match('[A-Za-z]{8}[0-9]+$', nom)

def test_prime():
    # Cf. issue 129
    f = Feuille()
    f.executer('F = Fonction("2x+7")')
    assertRaises(NameError, f.executer, "F'' = (1, 4)")
    f.executer("G''' = (-3, 6)")
    assertRaises(NameError, f.executer, 'G = Fonction("3x+2")')
    assertRaises(NameError, f.executer, '''H' = Fonction("2x-4")''')
    assertRaises(NameError, f.executer, "f1' = (1, 2)")

def test_nommage_intelligent():
    f = Feuille()
    o = f.objets

    o.AB = Segment()
    assert(o.AB.point1.nom == "A")
    assert(o.AB.point2.nom == "B")
    del o.AB
    del o.B

    o.AB = Segment(o.A)
    assert(o.AB.point2.nom == "B")

    o.D = Point()
    o.CD = Segment(point2 = o.D)
    assert(o.CD.point1.nom == "C")

    o.clear()

    # o.clear() ne doit pas supprimer les mots clefs
    assert 'erreur' in o

    o.EFG = Triangle()
    assert(o.EFG.point1.nom == "E")
    assert(o.EFG.point2.nom == "F")
    assert(o.EFG.point3.nom == "G")

    o.MNP = Triangle_rectangle()
    assert(o.MNP.point1.nom == "M")
    assert(o.MNP.point2.nom == "N")
    assert(o.MNP.sommets[2].nom == "P")
    assert(o.P.mode_affichage == 'nom')


    o.ABCD = Carre()
    assert(o.ABCD.point1.nom == "A")
    assert(o.ABCD.point2.nom == "B")
    assert(o.ABCD.sommets[2].nom == "C")
    assert(o.ABCD.sommets[3].nom == "D")


def test_nommage_intelligent_lent():
    #FIXME: accélérer la création du polygone.
    f = Feuille()
    s = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    p = f.objets[s] = Polygone(26)
    assert(list(pt.nom for pt in p.points) == list(s))


def test_nommage_intelligent_vecteur_et_representant():
    f = Feuille()
    o = f.objets
    o.AB = Vecteur()
    assert(o.AB.point1.nom == "A")
    assert(o.AB.point2.nom == "B")
    o.CD = Representant(o.AB)
    assert(o.CD.origine.nom == "C")
    assert(o.CD.extremite.nom == "D")


def test_acces_objets():
    f = Feuille()
    o = f.objets
    o.A = (1, 2)
    assert(o["A"] is o.A)
    o.A_prime = (7, -1.5)
    assert(o["A`"] is o.A_prime)
    exec("b=Vecteur_libre()", o)
    assert("b" in o)
    exec("del b", o)
    assert("b" not in keys)


def test_noms_latex():
    f = Feuille()
    f.objets.A = Point()
    assert(f.objets.A.nom == "A")
    assert(f.objets.A.nom_latex == "$A$")
    f.objets.B1 = Point()
    assert(f.objets.B1.nom == "B1")
    assert(f.objets.B1.nom_latex == "$B_{1}$")
    f.objets.C17 = Point()
    assert(f.objets.C17.nom == "C17")
    assert(f.objets.C17.nom_latex == "$C_{17}$")
    f.objets.objet5 = Point()
    assert(f.objets.objet5.nom == "objet5")
    assert(f.objets.objet5.nom_latex == "$objet_{5}$")
    f.objets.Delta = Point()
    assert(f.objets.Delta.nom == "Delta")
    assert(f.objets.Delta.nom_latex == "$\\Delta$")
    f.objets.delta = Point()
    assert(f.objets.delta.nom == "delta")
    assert(f.objets.delta.nom_latex == "$\\delta$")
    f.objets.phi15 = Point()
    assert(f.objets.phi15.nom == "phi15")
    assert(f.objets.phi15.nom_latex == "$\\phi_{15}$")
    f.objets.A_prime_prime = Point()
    assert(f.objets.A_prime_prime.nom == "A_prime_prime")
    assert(f.objets.A_prime_prime.nom_latex == "$A''$")
    f.objets["A'B'"] = Point()
    assert(f.objets.A_primeB_prime.nom == "A_primeB_prime")
    assert(f.objets.A_primeB_prime.nom_latex == "$A'B'$")
    f.objets.A_prime71 = Point()
    assert(f.objets.A_prime71.nom == "A_prime71")
    assert(f.objets.A_prime71.nom_latex == "$A'_{71}$")
    f.objets.A17B22 = Point()
    assert(f.objets.A17B22.nom == "A17B22")
    assert(f.objets.A17B22.nom_latex == "$A_{17}B_{22}$")

    f.objets.C_prime = Cercle()
    assert(f.objets.C_prime.nom_latex == "$\\mathscr{C}'$")
    f.objets.u = Vecteur()
    assert(f.objets.u.nom_latex == "$\\vec u$")
    f.objets.u_prime = Vecteur()
    assert(f.objets.u_prime.nom_latex == "$\\overrightarrow{u'}$")

def test_info():
    f = Feuille()
    o = f.objets
    with contexte(decimales = 2):
        A = o.A = Point(5, 7)
        assert(A.info == "Point A de coordonnées (5 ; 7)")
        B = o.B = Point(6.5, 9.3)
        assert(B.info == "Point B de coordonnées (6,5 ; 9,3)")
        s = o.s = Segment(A, B)
        assert(s.info == "Segment s de longueur 2,75")
        c = o.c = Cercle(s)
        assert(c.info == "Cercle c de rayon 1,37")
        d = o.d = Droite(A, B)
        assert(d.info == "Droite d d'équation -2,3 x + 1,5 y + 1 = 0")
        C = o.C = Point(-1.5, 2.7)
        a = o.a = Arc_cercle(A, B, C)
        assert(a.info == 'Arc a de longueur 7,5')
        alpha = o.alpha = Angle(A, B, C)
        assertEqual(alpha.info, 'Angle alpha de valeur 0,3 rad')
    with contexte(decimales = 3):
        assert(a.info == 'Arc a de longueur 7,505')


