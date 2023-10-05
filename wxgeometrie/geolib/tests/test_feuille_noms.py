# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

import re
from math import cos, pi, e, sqrt

from wxgeometrie.geolib.tests.geotestlib import rand_pt
from wxgeometrie.geolib import (
    Triangle_rectangle, DescripteurFeuille, Point, Segment,
    Vecteur, Fonction, Variable, Feuille, Angle, contexte, Arc_cercle,
    Texte, Droite, Carre, Triangle, Polygone, Cercle, Parallelogramme,
    Droite_equation, Cercle_equation, Courbe, Formule,
    Representant
)
from wxgeometrie.geolib.routines import nice_display
from wxgeometrie.geolib.feuille import parse_equation, is_equation

import tools.unittest

class GeolibTest(tools.unittest.TestCase):

    def test_abreviations(self):
        f = Feuille(titre = "Feuille de travail n°1")
        o = f.objets

        self.assertIn("Point", o)
        self.assertIn("Variable", o)
        self.assertIn("Texte", o)
        self.assertIn("point", o)
        self.assertIn("variable", o)
        self.assertIn("texte", o)

        o.txt = ["salut"]
        self.assertIsInstance(o.txt, Texte)
        self.assertEqual(o.txt.texte, "salut")
        o.s = ["Hé, ça marche !"]
        self.assertIsInstance(o.s, Texte)
        self.assertEqual(o.s.texte, "Hé, ça marche !")

        o.A = (1, 2)
        o.k = 7
        self.assertIsInstance(o.A, Point)
        self.assertIsInstance(o.k, int)
        o.h = 'A.x'
        o.A.x = 15
        self.assertEqual(o.h, 15)
        o.h = "A.x-10"
        self.assertEqual(o.h, 5)
        self.assertEqual(o.h - 3, 2)
        o.h = pi/3
        self.assertAlmostEqual(cos(o.h), 1/2)
        o.B = (-1, 3)
        o.u = o.A>o.B
        self.assertIsInstance(o.u, Vecteur)
        self.assertEqual(o.u.coordonnees, (o.B.x - o.A.x, o.B.y - o.A.y))
        o.C = 2-3j
        self.assertIsInstance(o.C, Point)
        self.assertEqual(o.C.z, 2-3j)
        o.C.x = "A.x"
        #print 'o.C.x.val:', o.C.x.val, type(o.C.x.val)
        self.assertIsInstance(o.C.x, (float, int))
        self.assertEqual(o.C.x, o.A.x)
        o.A.coordonnees = -11, 3
        self.assertEqual(o.C.coordonnees[0], -11)
        o.B.x = "A.x + 1"
        self.assertIsInstance(o.B.x, (float, int))
        self.assertEqual(o.B.x, o.A.x + 1)
        o.A.coordonnees = 30, -5
        self.assertEqual(o.B.coordonnees[0], 31)
        o.A(-3.6, 0.4)
        self.assertEqual(o.C.coordonnees[0], -3.6)
        # 'o.EFG = Triangle' doit être accepté comme alias de 'o.EFG = Triangle()'
        o.EFG = Triangle
        self.assertIsInstance(o.EFG, Triangle)

    def test_nommage_automatique(self):
        f = Feuille()
        M1 = f.objets._ = Point()
        self.assertIn("M1", f.objets)
        M2 = f.objets._ = Point(1, 3)
        self.assertIn("M2", f.objets)
        f.objets._ = Droite(M1, M2)
        self.assertIn("d1", f.objets)
        f.objets._ = Cercle(M1, M2)
        self.assertIn("c1", f.objets)
        f.objets._ = Segment(M1, M2)
        self.assertIn("s1", f.objets)

    def test_noms_aleatoires(self):
        f = Feuille()
        f.executer('A1=(1,2)')
        f.executer('A2=(1,0)')
        M = Point()
        s = Segment()
        g = Fonction('2x+7')
        self.assertEqual(f.nom_aleatoire(M), 'M1')
        self.assertEqual(f.nom_aleatoire(s), 's1')
        self.assertEqual(f.nom_aleatoire(g), 'f1')
        self.assertEqual(f.nom_aleatoire(M, prefixe='A'), 'A3')
        # f0, f1, etc. sont réservés aux fonctions
        nom = f.nom_aleatoire(M, prefixe='f')
        self.assertTrue(re.match('[A-Za-z]{8}[0-9]+$', nom))

    def test_prime(self):
        # Cf. issue 129
        f = Feuille()
        f.executer('F = Fonction("2x+7")')
        self.assertRaises(NameError, f.executer, "F'' = (1, 4)")
        f.executer("G''' = (-3, 6)")
        self.assertRaises(NameError, f.executer, 'G = Fonction("3x+2")')
        self.assertRaises(NameError, f.executer, '''H' = Fonction("2x-4")''')
        self.assertRaises(NameError, f.executer, "f1' = (1, 2)")

    def test_nommage_intelligent(self):
        f = Feuille()
        o = f.objets

        o.AB = Segment()
        self.assertEqual(o.AB.point1.nom, "A")
        self.assertEqual(o.AB.point2.nom, "B")
        del o.AB
        del o.B

        o.AB = Segment(o.A)
        self.assertEqual(o.AB.point2.nom, "B")

        o.D = Point()
        o.CD = Segment(point2 = o.D)
        self.assertEqual(o.CD.point1.nom, "C")

        o.clear()

        # o.clear() ne doit pas supprimer les mots clefs
        self.assertIn('erreur', o)

        o.EFG = Triangle()
        self.assertEqual(o.EFG.point1.nom, "E")
        self.assertEqual(o.EFG.point2.nom, "F")
        self.assertEqual(o.EFG.point3.nom, "G")

        o.MNP = Triangle_rectangle()
        self.assertEqual(o.MNP.point1.nom, "M")
        self.assertEqual(o.MNP.point2.nom, "N")
        self.assertEqual(o.MNP.sommets[2].nom, "P")
        self.assertEqual(o.P.mode_affichage, 'nom')


        o.ABCD = Carre()
        self.assertEqual(o.ABCD.point1.nom, "A")
        self.assertEqual(o.ABCD.point2.nom, "B")
        self.assertEqual(o.ABCD.sommets[2].nom, "C")
        self.assertEqual(o.ABCD.sommets[3].nom, "D")


    def test_nommage_intelligent_lent(self):
        #FIXME: accélérer la création du polygone.
        f = Feuille()
        s = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        p = f.objets[s] = Polygone(26)
        self.assertEqual(list(pt.nom for pt in p.points), list(s))


    def test_nommage_intelligent_vecteur_et_representant(self):
        f = Feuille()
        o = f.objets
        o.AB = Vecteur()
        self.assertEqual(o.AB.point1.nom, "A")
        self.assertEqual(o.AB.point2.nom, "B")
        o.CD = Representant(o.AB)
        self.assertEqual(o.CD.origine.nom, "C")
        self.assertEqual(o.CD.extremite.nom, "D")


    def test_acces_objets(self):
        f = Feuille()
        o = f.objets
        o.A = (1, 2)
        self.assertIs(o["A"], o.A)
        o.A_prime = (7, -1.5)
        self.assertIs(o["A`"], o.A_prime)
        exec("b=Vecteur_libre()", o)
        self.assertIn("b", o)
        exec("del b", o)
        self.assertNotIn("b", o)


    def test_noms_latex(self):
        f = Feuille()
        f.objets.A = Point()
        self.assertEqual(f.objets.A.nom, "A")
        self.assertEqual(f.objets.A.nom_latex, "$A$")
        f.objets.B1 = Point()
        self.assertEqual(f.objets.B1.nom, "B1")
        self.assertEqual(f.objets.B1.nom_latex, "$B_{1}$")
        f.objets.C17 = Point()
        self.assertEqual(f.objets.C17.nom, "C17")
        self.assertEqual(f.objets.C17.nom_latex, "$C_{17}$")
        f.objets.objet5 = Point()
        self.assertEqual(f.objets.objet5.nom, "objet5")
        self.assertEqual(f.objets.objet5.nom_latex, "$objet_{5}$")
        f.objets.Delta = Point()
        self.assertEqual(f.objets.Delta.nom, "Delta")
        self.assertEqual(f.objets.Delta.nom_latex, "$\\Delta$")
        f.objets.delta = Point()
        self.assertEqual(f.objets.delta.nom, "delta")
        self.assertEqual(f.objets.delta.nom_latex, "$\\delta$")
        f.objets.phi15 = Point()
        self.assertEqual(f.objets.phi15.nom, "phi15")
        self.assertEqual(f.objets.phi15.nom_latex, "$\\phi_{15}$")
        f.objets.A_prime_prime = Point()
        self.assertEqual(f.objets.A_prime_prime.nom, "A_prime_prime")
        self.assertEqual(f.objets.A_prime_prime.nom_latex, "$A''$")
        f.objets["A'B'"] = Point()
        self.assertEqual(f.objets.A_primeB_prime.nom, "A_primeB_prime")
        self.assertEqual(f.objets.A_primeB_prime.nom_latex, "$A'B'$")
        f.objets.A_prime71 = Point()
        self.assertEqual(f.objets.A_prime71.nom, "A_prime71")
        self.assertEqual(f.objets.A_prime71.nom_latex, "$A'_{71}$")
        f.objets.A17B22 = Point()
        self.assertEqual(f.objets.A17B22.nom, "A17B22")
        self.assertEqual(f.objets.A17B22.nom_latex, "$A_{17}B_{22}$")

        f.objets.C_prime = Cercle()
        self.assertEqual(f.objets.C_prime.nom_latex, "$\\mathscr{C}'$")
        f.objets.u = Vecteur()
        self.assertEqual(f.objets.u.nom_latex, "$\\vec u$")
        f.objets.u_prime = Vecteur()
        self.assertEqual(f.objets.u_prime.nom_latex, "$\\overrightarrow{u'}$")

    def test_info(self):
        f = Feuille()
        o = f.objets
        with contexte(decimales = 2):
            A = o.A = Point(5, 7)
            self.assertEqual(A.info, "Point A de coordonnées (5 ; 7)")
            B = o.B = Point(6.5, 9.3)
            self.assertEqual(B.info, "Point B de coordonnées (6,5 ; 9,3)")
            s = o.s = Segment(A, B)
            self.assertEqual(s.info, "Segment s de longueur 2,75")
            c = o.c = Cercle(s)
            self.assertEqual(c.info, "Cercle c de rayon 1,37")
            d = o.d = Droite(A, B)
            self.assertEqual(d.info, "Droite d d'équation -2,3 x + 1,5 y + 1 = 0")
            C = o.C = Point(-1.5, 2.7)
            a = o.a = Arc_cercle(A, B, C)
            self.assertEqual(a.info, 'Arc a de longueur 7,5')
            alpha = o.alpha = Angle(A, B, C)
            self.assertEqual(alpha.info, 'Angle alpha de valeur 0,3 rad')
        with contexte(decimales = 3):
            self.assertEqual(a.info, 'Arc a de longueur 7,505')

