# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

import re
from math import cos, pi, e, sqrt

from tools.testlib import assertAlmostEqual, assertRaises
from wxgeometrie.geolib.tests.geotestlib import rand_pt
from wxgeometrie.geolib import (Triangle_rectangle, DescripteurFeuille, Point, Segment,
                    Vecteur, Fonction, Variable, Feuille, Angle, contexte, Arc_cercle,
                    Texte, Droite, Carre, Triangle, Polygone, Cercle, Parallelogramme,
                    NOM,
                    )

def test_abreviations():
    f = Feuille(titre = u"Feuille de travail n°1")
    o = f.objets

    assert(o.has_key("Point"))
    assert(o.has_key("Variable"))
    assert(o.has_key("Texte"))
    assert(o.has_key("point"))
    assert(o.has_key("variable"))
    assert(o.has_key("texte"))

    o.txt = ["salut"]
    assert(isinstance(o.txt, Texte))
    assert(o.txt.texte == "salut")
    o.s = [u"Hé, ça marche !"]
    assert(isinstance(o.s, Texte))
    assert(o.s.texte == u"Hé, ça marche !")

    o.A = (1, 2)
    o.k = 7
    assert(isinstance(o.A, Point))
    assert(isinstance(o.k, Variable))
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
    assert(isinstance(o.C.x.val, (float, int, long)))
    assert(o.C.x == o.A.x)
    o.A.coordonnees = -11, 3
    assert(o.C.coordonnees[0] == -11)
    o.B.x = "A.x + 1"
    assert(isinstance(o.B.x.val, (float, int, long)))
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

    o.ABCDEFGHIJKLMNOPQRSTUVWXYZ = Polygone(26)
    assert(  list(pt.nom for pt in o.ABCDEFGHIJKLMNOPQRSTUVWXYZ.points)\
                        == list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))

    o.clear()

    o.EFG = Triangle()
    assert(o.EFG.point1.nom == "E")
    assert(o.EFG.point2.nom == "F")
    assert(o.EFG.point3.nom == "G")

    o.MNP = Triangle_rectangle()
    assert(o.MNP.point1.nom == "M")
    assert(o.MNP.point2.nom == "N")
    assert(o.MNP.sommets[2].nom == "P")
    assert(o.P.style("legende") == NOM)


    o.ABCD = Carre()
    assert(o.ABCD.point1.nom == "A")
    assert(o.ABCD.point2.nom == "B")
    assert(o.ABCD.sommets[2].nom == "C")
    assert(o.ABCD.sommets[3].nom == "D")

def test_acces_objets():
    f = Feuille()
    o = f.objets
    o.A = (1, 2)
    assert(o["A"] is o.A)
    o.A_prime = (7, -1.5)
    assert(o["A`"] is o.A_prime)
    exec("b=Vecteur_libre()", o)
    assert("b" in o.keys())
    exec("del b", o)
    assert("b" not in o.keys())

def test_sauvegarde():
    f = Feuille(titre = "Ma feuille")
    o = f.objets
    o.A = (1, 2)
    o.B = (-1, 3)
    o.k = 7
    o.s = Segment(o.A, o.B)
    f.sauvegarder()

def test_rattachement_objets():
    A=Point()
#    assert(A.x == 0 and A.y == 0)
    x0, y0 = A.xy
    assert(isinstance(Point.__feuille__, DescripteurFeuille))
    assert(A.__feuille__ is None)
    f = Feuille()
    f.objets.A = A
    assert(A.__feuille__ is f)
    assert(A.x != x0 and A.y != y0)
    xmin, xmax, ymin, ymax = f.fenetre
    assert(xmin <= A.x <= xmax and ymin <= A.y <= ymax)

def test_variables_composees_1():
    f = Feuille()
    A = f.objets.A = Point()
    B = f.objets.B = Point()
    A(-5, 13)
    B.x = A.x
    assert(B.x == B.coordonnees[0] == A.x == -5)
    A(1, 9)
    assert(B.x == B.coordonnees[0] == -5 and A.x == 1)
    B.x="A.x"
    A(17, 5)
    assert(B.coordonnees[0] == B.x == 17)

def test_variables_composees_2():
    f = Feuille()
    f.objets.M1 = Point(-1.27482678984, 1.69976905312, legende=2)
    f.objets.M2 = Point(2.42032332564, 1.25635103926, legende=2)
    f.objets.s1 = Segment(f.objets.M1,f.objets.M2)
    f.objets.M1(-2.77136258661, 2.91916859122)
    f.objets.M1(4.74826789838, -1.07159353349)
    f.objets.M5 = Point(-5.11778290993, 2.30946882217, legende=2)
    f.objets.M6 = Point(-1.86605080831, 3.25173210162, legende=2)
    f.objets.s4 = Segment(f.objets.M5,f.objets.M6)
    f.objets.M5(-5.59815242494, 2.34642032333)
    f.objets.M1(-2.42032332564, -1.60739030023)
    f.objets.M6(-1.86605080831, 3.25173210162)
    f.objets.M6.renommer('B', legende = 1)
    f.objets.M6 = Point(2.91916859122, 3.5103926097, legende=2)
    f.objets.M6.style(**{'legende': 3, 'label': u'B.x'})
    f.objets.B(-1.18244803695, 1.25635103926)
    f.objets.M6.supprimer()
    f.objets.B(-2.21709006928, 2.64203233256)
    f.objets.M6 = Point(-6.6143187067, 0.443418013857, legende=2)
    f.objets.M6.renommer('C', legende = 1)
    f.objets.C.x=f.objets.B.x
    f.objets.B(-3.17782909931, 3.36258660508)
    f.objets.C.x="B.x"
    f.objets.B(-4.74826789838, 3.47344110855)
    f.objets.B(-1.99538106236, 3.63972286374)
    assert(f.objets.C.coordonnees[0] == f.objets.C.x == f.objets.B.coordonnees[0] == f.objets.B.x)

def test_polygones_et_representants_de_vecteurs():
    f = Feuille()
    f.objets.A = A = rand_pt()
    f.objets.B = B = rand_pt()
    f.objets.C = C = rand_pt()
    f.objets.p = Parallelogramme(A, B, C)
    f.objets.S1.renommer("D")
    s = repr(f.objets.p)
    del f.objets.p
    assert("D" not in f.objets)
    exec("p=" + s, f.objets)
    assert("D" in f.objets)
    assert(f.objets.D is f.objets.p.sommets[3])

def test_relier_point_axes():
    f = Feuille()
    f.objets.M1 = Point(-1.27482678984, 1.69976905312, legende=2)
    f.objets.M2 = Point(2.42032332564, 1.25635103926, legende=2)
    f.objets.s1 = Segment(f.objets.M1, f.objets.M2)
    f.objets.M1.relier_axe_x()
    f.objets.M1.relier_axe_y()

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
    f.objets.u_prime = Vecteur()
    assert(f.objets.u_prime.nom_latex == "$\\vec u'$")

def test_formules():
    f = Feuille()
    o = f.objets
    o.A = Point(e, 3)
    o.M = Point()
    o.M.label(u'{1/ln(A.x)}', True)
    assert(eval(o.M.label()) == 1)

def test_constantes():
    f = Feuille()
    assertAlmostEqual(f.objets.pi, 3.1415926535897931)
    assertAlmostEqual(f.objets.e, 2.7182818284590451)

def test_modification_variable():
    f = Feuille()
    o = f.objets
    o.a = Variable(1)
    o.fa = "5*sin(4/(a+.5))-1.5"
    o.A = Point(o.a, o.fa)
    o.fa = "-5*sin(4/(a+.5))+5.5"
    o.A = Point(o.a, o.fa)
    assertAlmostEqual(o.A.x, o.a)
    assertAlmostEqual(o.A.y, o.fa)

def test_info():
    f = Feuille()
    o = f.objets
    with contexte(decimales = 2):
        A = o.A = Point(5, 7)
        assert(A.info == u"Point A de coordonnées (5, 7)")
        B = o.B = Point(6.5, 9.3)
        assert(B.info == u"Point B de coordonnées (6.5, 9.3)")
        s = o.s = Segment(A, B)
        assert(s.info == u"Segment s de longueur 2.75")
        c = o.c = Cercle(s)
        assert(c.info == u"Cercle c de rayon 1.37")
        d = o.d = Droite(A, B)
        assert(d.info == u"Droite d d'équation -2.3 x + 1.5 y + 1 = 0")
        C = o.C = Point(-1.5, 2.7)
        a = o.a = Arc_cercle(A, B, C)
        assert(a.info == u'Arc a de longueur 7.5')
        alpha = o.alpha = Angle(A, B, C)
        assert(alpha.info == u'Angle alpha de valeur 0.3')
    with contexte(decimales = 3):
        assert(a.info == u'Arc a de longueur 7.505')


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
    f.executer("=((i,sqrt(i)) for i in (3,4,5,6))")
    assert(o.M2.xy == (3, sqrt(3)))
    assert(o.M3.xy == (4, sqrt(4)))
    assert(o.M4.xy == (5, sqrt(5)))
    assert(o.M5.xy == (6, sqrt(6)))


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
    assert(noms == set(("A", "B", "s", "I", "M", "d", "C", "d2", "B")))
    f.nettoyer()
    assert(o.noms == noms)

    ex('s.style(visible = False)')
    f.nettoyer()
    assert(o.noms == noms)

    ex('M.style(visible = False)')
    f.nettoyer()
    noms -= set(("M", "s"))
    assert(o.noms == noms)

    ex('d.style(visible = False)')
    f.nettoyer()
    noms.remove("d")
    assert(o.noms == noms)

    ex('I.style(visible = False)')
    f.nettoyer()
    noms -= set(("B", "I"))
    assert(o.noms == noms)


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


def test_issue_186():
    f = Feuille()
    f.executer("c=Cercle")
    assertRaises(NameError, f.executer, "C_'=_")
    assert(f.objets.has_key("c"))

def test_redefinir():
    f = Feuille()
    A = f.objets.A = Point()
    B = f.objets.B = Point()
    f.objets.AB = Segment(A, B)
    f.objets.AB.redefinir('Vecteur(A, B)')
    assert isinstance(f.objets.AB, Vecteur)
    assert f.objets.AB == Vecteur(A, B)
    f.objets.txt = Texte('Hello', 2, 3)
    f.objets.txt.redefinir("Texte('Bonjour', 1, 4)")
    assert isinstance(f.objets.txt, Texte)
    assert f.objets.txt.texte == 'Bonjour'
    assert f.objets.txt.coordonnees == (1, 4)

def test_issue_176():
    f = Feuille()
    A = f.objets.A = Point()
    B = f.objets.B = Point()
    f.objets.s = Segment(A, B)
    del f.objets.A, f.objets.B, f.objets.s
    assert set(('A', 'B', 's')).isdisjoint(f.objets.noms)
