# -*- coding: utf-8 -*-

import re
from math import cos, pi, e, sqrt

from pytest import XFAIL

from tools.testlib import assertAlmostEqual, assertRaises, assertEqual
from wxgeometrie.geolib.tests.geotestlib import rand_pt
from wxgeometrie.geolib import (Triangle_rectangle, DescripteurFeuille, Point, Segment,
                    Vecteur, Fonction, Variable, Feuille, Angle, contexte, Arc_cercle,
                    Texte, Droite, Carre, Triangle, Polygone, Cercle, Parallelogramme,
                    Droite_equation, Cercle_equation, Courbe, Formule
                    )
from wxgeometrie.geolib.routines import nice_display
from wxgeometrie.geolib.feuille import parse_equation, is_equation


def test_issue_186():
    f = Feuille()
    f.executer("c=Cercle")
    assertRaises(NameError, f.executer, "C_'=_")
    assert("c" in f.objets)

def test_issue_176():
    f = Feuille()
    A = f.objets.A = Point()
    B = f.objets.B = Point()
    f.objets.s = Segment(A, B)
    del f.objets.A, f.objets.B, f.objets.s
    assert set(('A', 'B', 's')).isdisjoint(f.objets.noms)


def test_issue_227():
    f = Feuille()
    f.executer('F = (1;0)')
    f.executer('O = (0;0)')
    f.executer('ABCDEF = Polygone_regulier_centre(n=6,centre=O,sommet=F)')
    try:
        f.executer('ABCDEF = Polygone_regulier_centre(n=6,centre=O,sommet=F)')
    except NameError:
        pass
    f.executer('S5.renommer("A", afficher_nom=True)')
    f.executer('S4.renommer("B", afficher_nom=True)')
    f.executer('S3.renommer("C", afficher_nom=True)')
    f.executer('S2.renommer("D", afficher_nom=True)')
    f.executer('S1.renommer("E", afficher_nom=True)')
    assert 'S1' not in f.objets
    assert 'S2' not in f.objets
    assert 'S3' not in f.objets
    assert 'S4' not in f.objets
    assert 'S5' not in f.objets
    f.executer('O = (-1;0)')
    f.historique.annuler()
    f.historique.refaire()


def test_issue_227_bis():
    f = Feuille()
    f.executer('F = (1;0)')
    f.executer('O = (0;0)')
    f.executer('ABCDEF = Polygone_regulier_centre(n=6,centre=O,sommet=F)')
    f.executer('S5.renommer("A", afficher_nom=True)')
    f.executer('A.renommer("B", afficher_nom=True)')
    assert 'S5' not in f.objets
    assert 'A' not in f.objets

def test_issue_252():
    # Test de la conversion intelligente des virgules en points
    # dans l'interpréteur de commandes de geolib.

    # 1er cas : conserver les virgules
    # Par exemple, 'A=(1,2)' signifie 'A=(1, 2)'
    f = Feuille()
    f.executer("A=(1,5)")
    f.executer("B = (-2,3)")
    assert f.objets.A.xy == (1, 5)
    assert f.objets.B.xy == (-2, 3)

    # 2e cas : transformer les virgules en point (séparateur décimal)
    # Par exemple, 'g(1,3)' signifie 'g(1.3)'
    f.executer('g = Fonction("2x+3")')
    f.executer("a = g(5,3)")
    assertAlmostEqual(f.objets.a, 13.6)
    f.executer("=Point(1,5 ; g(1,5))")
    assertAlmostEqual(f.objets.M1.xy, (1.5, 6.))

    f.executer('g2 = Fonction("3x+1")')
    f.executer("a = g2(-1,2)")
    assertAlmostEqual(f.objets.a, -2.6)
    f.executer("=Point(-1,5 ; g2(-1,5))")
    assertAlmostEqual(f.objets.M2.xy, (-1.5, -3.5))

def test_issue_250():
    # «'» transformé en «_prime»
    f = Feuille()
    f.executer("txt=`prix unitaire en milliers d'euros`")
    assert f.objets.txt.texte == "prix unitaire en milliers d'euros"
