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



def test_sauvegarde():
    f1 = Feuille(titre="Ma feuille")
    o = f1.objets
    o.A = (1, 2)
    o.B = (-1, 3)
    o.k = 7
    o.s = Segment(o.A, o.B)
    sauvegarde = f1.sauvegarder()
    f2 = Feuille(titre="Nouvelle feuille")
    f2.charger(sauvegarde)
    assertEqual(f2.objets.noms, set(['A', 'B', 'k', 's', 'dpy', 'dpx',
                                     'xmax', 'xmin', 'ymin', 'ymax']))

def test_rattachement_objets():
    A=Point()
#    assert(A.x == 0 and A.y == 0)
    x0, y0 = A.xy
    assert(isinstance(Point.feuille, DescripteurFeuille))
    assert(A.feuille is None)
    f = Feuille()
    f.objets.A = A
    assert(A.feuille is f)
    assert(A.x != x0 and A.y != y0)
    xmin, xmax, ymin, ymax = f.fenetre
    assert(xmin <= A.x <= xmax and ymin <= A.y <= ymax)


def test_executer():
    f = Feuille()
    o = f.objets
    f.executer("A = (1, 2)")
    f.executer("A.x += 1")
    assert(o.A.x == 2)
    f.executer("A' = 3, 4")
    f.executer("s = [A A']")
    f.executer("I = Milieu(s)")
    assertAlmostEqual(o.I.xy, (2.5, 3))
    f.executer("del")
    assert("I" not in o.noms)
    assert("A_prime" in o.noms)
    f.executer("del")
    f.executer("del")
    assert("A_prime" not in o.noms)
    f.executer("= (1, 2)")
    assert(o.M1.coordonnees == (1, 2))
    f.executer("txt0 = `Bonjour !`")
    f.executer(r"txt1 = `$P\`ere et m\`ere ont un accent grave.$`")
    f.executer("chaine_vide = ``")
    assert(o.txt0.texte == "Bonjour !")
    assert(o.txt1.texte == r"$P\`ere et m\`ere ont un accent grave.$")
    assert(o.chaine_vide.texte == "")
    f.executer("M = (5, 7)")
    f.executer("C = _")
    assert(o.C.x == 5)
    f.executer("=((i,sqrt(i)) for i in (3, 4, 5, 6))")
    assert(o.M2.xy == (3, sqrt(3)))
    assert(o.M3.xy == (4, sqrt(4)))
    assert(o.M4.xy == (5, sqrt(5)))
    assert(o.M5.xy == (6, sqrt(6)))
    f.executer("B= -1;7")
    ##f.executer("u=A>B")
    ##assert o.u.xy == (o.B.x - o.A.x, o.B.y - o.A.y)
    f.executer("K=(-1.3,2.5)")
    assert o.K.xy == (-1.3, 2.5)
    f.executer("K=(1,2)")
    assert o.K.xy == (1, 2)
    f.executer("u = A->B")
    assert o.u.xy == (o.B.x - o.A.x, o.B.y - o.A.y)
    f.executer("v = A->B + M3 -> M4")
    assertAlmostEqual(o.v.x, o.B.x - o.A.x + o.M4.x - o.M3.x)
    assertAlmostEqual(o.v.y, o.B.y - o.A.y + o.M4.y - o.M3.y)




def test_nettoyer():
    f = Feuille()
    o = f.objets
    ex = f.executer
    ex('A=(5,4)')
    ex('B=(6,5.3)')
    ex('s=Segment(A, B)')
    ex('I=Milieu(s)')
    ex('M=Point(s)')
    ex('d=Droite(A,  B)')
    ex('C=(4, 8)')
    ex('d2=Droite(A, C)')

    ex('B.style(visible = False)')
    noms = o.noms
    assert(noms == set(("A", "B", "s", "I", "M", "d", "C", "d2", "B", "xmin", "xmax", "ymin", "ymax", "dpx", "dpy")))
    f.nettoyer()
    assert(o.noms == noms)

    ex('s.style(visible = False)')
    f.nettoyer()
    assert(o.noms == noms)

    ex('M.style(visible = False)')
    f.nettoyer()
    noms -= set(("M", "s"))
    assertEqual(o.noms, noms)

    ex('d.style(visible = False)')
    f.nettoyer()
    noms.remove("d")
    assertEqual(o.noms, noms)

    ex('I.style(visible = False)')
    f.nettoyer()
    noms -= set(("B", "I"))
    assertEqual(o.noms, noms)

    # Les textes vides sont supprimés.
    ex('txt = Texte()')
    noms.add('txt')
    assertEqual(o.noms, noms)
    f.nettoyer()
    noms.remove('txt')
    assertEqual(o.noms, noms)


def test_feuille_modifiee():
    f = Feuille()
    f.modifiee = True
    f.executer('A=(1,2)')
    assert(f.modifiee)
    f.modifiee = False
    f.executer('A.x = 3')
    assert(f.modifiee)
    f.modifiee = False
    f.historique.annuler()
    assert(f.modifiee)


def test_redefinir():
    f = Feuille()
    A = f.objets.A = Point()
    B = f.objets.B = Point()
    f.objets.AB = Segment(A, B)
    f.objets.AB.redefinir('Vecteur(A, B)')
    assert isinstance(f.objets.AB, Vecteur)
    assert f.objets.AB.egale(Vecteur(A, B))
    f.objets.txt = Texte('Hello', 2, 3)
    f.objets.txt.redefinir("Texte('Bonjour', 1, 4)")
    assert isinstance(f.objets.txt, Texte)
    assert f.objets.txt.texte == 'Bonjour'
    assert f.objets.txt.coordonnees == (1, 4)


def test_sauvegarde_label():
    f1 = Feuille(titre = "Ma feuille")
    f1.objets.A = (1, 2)
    A = f1.objets.A
    A.etiquette.style(couleur="b")
    legende = "Pour qui sont ces serpents qui sifflent sur nos têtes."
    A.label(legende)
    assertEqual(A.etiquette.style("couleur"), "b")
    assertEqual(A.label(), legende)
    sauvegarde = f1.sauvegarder()

    f2 = Feuille(titre="Nouvelle feuille")
    f2.charger(sauvegarde)
    A = f2.objets.A
    assertEqual(A.etiquette.style("couleur"), "b")
    assertEqual(A.label(), legende)
