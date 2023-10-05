# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

import tools.unittest
from math import pi, sin, cos, sqrt
from random import random, randint

from wxgeometrie.geolib.tests.geotestlib import rand_pt
from wxgeometrie.geolib import (Point, Polygone, Milieu, Label_polygone, Barycentre,
                                Droite, Triangle, Angle, Vecteur,
                                Quadrilatere, Pentagone, Hexagone, Heptagone,
                                Octogone, Segment, Parallelogramme,
                                Triangle_isocele, Triangle_equilateral, Rectangle,
                                Carre, Polygone_regulier, Carre_centre,
                                Triangle_equilateral_centre, Polygone_regulier_centre,
                                Losange, Mediatrice, Triangle_isocele_rectangle,
                                Triangle_rectangle, contexte, Sommet, Cote, Feuille,
                                )

class GeolibTest(tools.unittest.TestCase):
    # def test_Cote(self):
    #     pass # À ÉCRIRE
    #
    # def test_Sommet(self):
    #     pass # À ÉCRIRE

    def test_Polygone(self):
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
        p = p0 = Polygone(A, B, C, D, E, F, G, H, I, J, K)
        self.assertIsInstance(p.etiquette, Label_polygone)
        self.assertTrue(p.sommets[0].confondu(A) and p.sommets[10].confondu(K))
        self.assertIn(Milieu(B, C), p.cotes[1])
        self.assertAlmostEqual(p.centre.coordonnees, Barycentre(A, B, C, D, E, F, G, H, I, J, K).coordonnees)
        # cas particuliers :
        t = Polygone(A, B, C)
        O = t.centre_cercle_circonscrit
        self.assertAlmostEqual(Segment(O, A).longueur, Segment(O, C).longueur)
        self.assertTrue(Droite(t.orthocentre, C).perpendiculaire(Droite(A, B)))
        self.assertIs(t.__class__, Triangle)
        p = Polygone(A, B, C,  D)
        self.assertIs(p.__class__, Quadrilatere)
        p = Polygone(A, B, C,  D, E)
        self.assertIs(p.__class__, Pentagone)
        p = Polygone(A, B, C,  D, E, F)
        self.assertIs(p.__class__, Hexagone)
        p = Polygone(A, B, C,  D, E, F, G)
        self.assertIs(p.__class__, Heptagone)
        p = Polygone(A, B, C,  D, E, F, G, H)
        self.assertIs(p.__class__, Octogone)
        self.assertTrue(p._hierarchie < p.sommets[0]._hierarchie < \
                        p.sommets[1]._hierarchie < p.sommets[7]._hierarchie < \
                        p._hierarchie + 1)
        # Test keyword 'points'
        p = Polygone(points = (A, B, C, D, E, F, G, H, I, J, K))
        self.assertEqual(p.centre.coordonnees, p0.centre.coordonnees)
        self.assertNotIn("points", p.style())
        # Syntaxe spéciale : Polygone créé sans arguments, ou avec un entier comme argument.
        p = Polygone()
        p = Polygone(2)
        self.assertIsInstance(p, Segment)
        p = Polygone(3)
        self.assertIsInstance(p, Triangle)
        p = Polygone(n = 5)
        self.assertIsInstance(p, Pentagone)
        p = Polygone(n = 12)
        self.assertEqual(len(p.points), 12)
        p = Polygone(23)
        self.assertEqual(len(p.points), 23)
        self.assertTrue(len(str(p.points)) < 30000)


    def test_Triangle(self):
        A = rand_pt()
        B = rand_pt()
        C = rand_pt()
        t = Triangle(A, B, C)
        O = t.centre_cercle_circonscrit
        self.assertAlmostEqual(Segment(O, A).longueur, Segment(O, C).longueur)

    def test_Quadrilatere(self):
        A = rand_pt()
        B = rand_pt()
        C = rand_pt()
        D = rand_pt()
        p = Quadrilatere(A, B, C, D)
        self.assertAlmostEqual(p.centre.coordonnees, Barycentre(A, B, C, D).coordonnees)

    def test_Pentagone(self):
        A = rand_pt()
        B = rand_pt()
        C = rand_pt()
        D = rand_pt()
        E = rand_pt()
        p = Pentagone(A, B, C, D, E)
        self.assertAlmostEqual(p.centre.coordonnees, Barycentre(A, B, C, D, E).coordonnees)

    def test_Hexagone(self):
        A = rand_pt()
        B = rand_pt()
        C = rand_pt()
        D = rand_pt()
        E = rand_pt()
        F = rand_pt()
        p = Hexagone(A, B, C, D, E, F)
        self.assertAlmostEqual(p.centre.coordonnees, Barycentre(A, B, C, D, E, F).coordonnees)

    def test_Heptagone(self):
        A = rand_pt()
        B = rand_pt()
        C = rand_pt()
        D = rand_pt()
        E = rand_pt()
        F = rand_pt()
        G = rand_pt()
        p = Heptagone(A, B, C, D, E, F, G)
        self.assertAlmostEqual(p.centre.coordonnees, Barycentre(A, B, C, D, E, F, G).coordonnees)

    def test_Octogone(self):
        A = rand_pt()
        B = rand_pt()
        C = rand_pt()
        D = rand_pt()
        E = rand_pt()
        F = rand_pt()
        G = rand_pt()
        H = rand_pt()
        p = Octogone(A, B, C, D, E, F, G, H)
        self.assertAlmostEqual(p.centre.coordonnees, Barycentre(A, B, C, D, E, F, G, H).coordonnees)

    def test_Parallelogramme(self):
        A = rand_pt()
        B = rand_pt()
        C = rand_pt()
        p = Parallelogramme(A, B, C)
        D = p.sommets[3]
        self.assertTrue(Vecteur(A, B).egal(Vecteur(D, C)))

    def test_Rectangle(self):
        A = rand_pt()
        B = rand_pt()
        r = Rectangle(A, B)
        M, N, O, P = r.sommets
        diagonale1 = Segment(M, O)
        diagonale2 = Segment(N, P)
        self.assertAlmostEqual(diagonale1.longueur, diagonale2.longueur)
        cote = Droite(M, N)
        cote_oppose = Droite(O, P)
        self.assertTrue(cote.parallele(cote_oppose))

    def test_Losange(self):
        A = rand_pt()
        B = rand_pt()
        l = Losange(A, B)
        M, N, O, P = l.sommets
        diagonale1 = Droite(M, O)
        diagonale2 = Droite(N, P)
        self.assertTrue(diagonale1.perpendiculaire(diagonale2))
        cote = Droite(M, N)
        cote_oppose = Droite(O, P)
        self.assertTrue(cote.parallele(cote_oppose))

    def test_Polygone_regulier_centre(self):
        O = rand_pt()
        M = rand_pt()
        p = Polygone_regulier_centre(O, M, 15)
        self.assertEqual(len(p.cotes), 15)
        self.assertIs(p.centre, O)
        for Mi in p.sommets:
            self.assertAlmostEqual(Segment(O, Mi).longueur, Segment(O, M).longueur)
        for i in range(10):
            coeffs = tuple(random() for i in range(15))
            G = Barycentre(*zip(p.sommets, coeffs))
            self.assertIn(G, p)
        # cas particuliers :
        p = Polygone_regulier_centre(O, M, 3)
        self.assertIsInstance(p,  Triangle)
        p = Polygone_regulier_centre(O, M, 4)
        self.assertIsInstance(p,  Quadrilatere)
        self.assertTrue(len(str(p.points)) < 30000)

    def test_Triangle_equilateral_centre(self):
        O = rand_pt()
        M = rand_pt()
        p = Triangle_equilateral_centre(O, M)
        self.assertTrue(p.centre.existe and p.centre is O)
        self.assertTrue(p.centre_cercle_circonscrit.existe)
        self.assertTrue(p.centre_cercle_inscrit.existe)
        self.assertTrue(p.orthocentre.existe)
        self.assertTrue(p.orthocentre.confondu(
            p.centre, p.centre_cercle_circonscrit, p.centre_cercle_inscrit))

    def test_Triangle_isocele_rectangle(self):
        t = Triangle_isocele_rectangle((0, 0), (1, 1))
        self.assertAlmostEqual(t.point3.xy, (0, 1))
        self.assertAlmostEqual(t.aire, .5)

    def test_Carre_centre(self):
        O = rand_pt()
        M = rand_pt()
        p = Carre_centre(O, M)
        self.assertTrue(p.centre.existe and p.centre is O)
        self.assertEqual(len(p.cotes), 4)
        self.assertAlmostEqual(p.aire,  p.cotes[0].longueur**2)

    def test_Polygone_regulier(self):
        O = rand_pt()
        M = rand_pt()
        p = Polygone_regulier(O, M, 15)
        self.assertEqual(len(p.cotes), 15)
        self.assertIn(p.centre, Mediatrice(O, M))
        for i in range(15):
            self.assertAlmostEqual(Segment(p.sommets[i%15], p.sommets[(i+1)%15]).longueur, Segment(p.sommets[(i+2)%15], p.sommets[(i+3)%15]).longueur)
        p = Polygone_regulier(O, M, 3)
        self.assertIsInstance(p,  Triangle)
        p = Polygone_regulier(O, M, 4)
        self.assertIsInstance(p,  Quadrilatere)
        # Test de régression :
        # la taille de str(p.points) croissait exponentiellement.
        self.assertTrue(len(str(p.points)) < 30000)


    def test_Triangle_equilateral(self):
        O = rand_pt()
        M = rand_pt()
        p = Triangle_equilateral(O, M)
        self.assertTrue(p.centre.existe)
        self.assertTrue(p.centre_cercle_circonscrit.existe)
        self.assertTrue(p.centre_cercle_inscrit.existe)
        self.assertTrue(p.orthocentre.existe)
        self.assertTrue(p.orthocentre.confondu(p.centre, p.centre_cercle_circonscrit, p.centre_cercle_inscrit))

    def test_Carre(self):
        O = rand_pt()
        M = rand_pt()
        p = Carre(O, M)
        A, B, C, D = p.sommets
        self.assertTrue(p.centre.confondu(Milieu(A, C), Milieu(B, D)))
        self.assertTrue(A.confondu(O) and B.confondu(M))
        self.assertEqual(len(p.cotes), 4)
        self.assertAlmostEqual(p.aire,  p.cotes[0].longueur**2)
        # Test redéfinition d'un sommet
        c = Carre((3, 2), (7, 2))
        M = Point(0, 2)
        c.point1 = M
        self.assertIs(c.point1, M)
        self.assertTrue(c.regulier)
        self.assertAlmostEqual(c.aire, 49)
        self.assertAlmostEqual(c.point4.coordonnees, (0, 9))

    def test_Triangle_isocele(self):
        A = rand_pt()
        B = rand_pt()
        tri = Triangle_isocele(A, B, 2*pi/13)
        C = tri.point3
        a = Angle(B, A, C)
        self.assertAlmostEqual(a.radian, 2*pi/13)
        self.assertAlmostEqual(Segment(A, B).longueur, Segment(A, C).longueur)
        t1 = Triangle_isocele((0, 0), (1, 1), '90°')
        self.assertAlmostEqual(t1.point3.xy, (-1, 1))
        t2 = Triangle_isocele((0, 0), (2, 0), pi/3)
        self.assertAlmostEqual(t2.point3.xy, (2*cos(pi/3), 2*sin(pi/3)))
        with contexte(unite_angle='d'):
            t2.point3.xy = (0, 9)
            self.assertAlmostEqual(t2.point3.xy, (0, 2))
        with contexte(unite_angle='r'):
            t2.point3.xy = (0, 9)
            self.assertAlmostEqual(t2.point3.xy, (0, 2))


    def test_Triangle_rectangle(self):
        t = Triangle_rectangle(rand_pt(), rand_pt(), pi/7)
        a = Angle(t.point1, t.point3, t.point2)
        self.assertAlmostEqual(a.degre, 90)

    def test_issue_215(self):
        # Quand les angles sont en degré, les valeurs par défaut des triangles isocèles sont incorrectes
        with contexte(unite_angle='d'):
            for i in range(10):
                t = Triangle_isocele()
                self.assertTrue(abs(t.angle.rad) > pi/6)

    def test_Sommet(self):
        A = Point(1, 0)
        O = Point(0, 0)
        p = Carre_centre(O, A)
        self.assertEqual(len(p.sommets), 4)
        coordonnees = [sommet.xy for sommet in p.sommets]
        for elt0, elt1 in zip(coordonnees, [(1, 0), (0, 1), (-1, 0), (0, -1)]):
            self.assertAlmostEqual(elt0, elt1)
        # Si l'on tente de recréer un sommet, le sommet existant est renvoyé.
        S0 = p.sommets[0]
        self.assertNotEqual(S0.style('couleur'), 'y') # modifier la couleur dans le test sinon
        M0 = Sommet(p, 0, couleur='y')
        self.assertIs(M0, S0)
        self.assertEqual(S0.style('couleur'), 'y')

    def test_Cote(self):
        A = Point(1, 0)
        O = Point(0, 0)
        p = Carre_centre(O, A)
        self.assertEqual(len(p.cotes), 4)
        for cote in p.cotes:
            self.assertAlmostEqual(cote.longueur, sqrt(2))
        # Si l'on tente de recréer un côté, le côté existant est renvoyé.
        c0 = p.cotes[0]
        self.assertNotEqual(c0.style('couleur'), 'pink') # modifier la couleur dans le test sinon
        d0 = Cote(p, 0, couleur='pink')
        self.assertIs(d0, c0)
        self.assertEqual(c0.style('couleur'), 'pink')

    def test_cotes_sommets(self):
        # Teste qu'on puisse enregistrer plusieurs fois le même sommet ou le même
        # côté sur la feuille sans erreur
        f = Feuille()
        p = f.objets.p = Parallelogramme()
        self.assertIs(f.objets.S1, p.sommets[3])
        self.assertIs(f.objets.c1, p.cotes[0])
        # Ne doit pas renvoyer d'erreur :
        f.objets.S1 = Sommet(p, 3)
        f.objets.c1 = Cote(p, 0)
        self.assertIs(f.objets.S1, p.sommets[3])
        self.assertIs(f.objets.c1, p.cotes[0])


    def test_proprietes(self):
        A = Point(0, 0)
        B = Point(2, 0)
        C = Point(2, 1)
        D = Point(0, 1)
        p = Polygone(A, B, C, D)
        self.assertTrue(p.rectangle)
        self.assertFalse(p.losange)
        self.assertFalse(p.carre)
        self.assertTrue(p.parallelogramme)
        self.assertTrue(p.trapeze)
        C.x = 3
        self.assertFalse(p.rectangle)
        self.assertFalse(p.losange)
        self.assertFalse(p.carre)
        self.assertFalse(p.parallelogramme)
        self.assertTrue(p.trapeze)
        C.y = 4
        A = Point(0, 0)
        B = Point(1, -2)
        C = Point(2, 0)
        D = Point(1, 2)
        p = Polygone(A, B, C, D)
        self.assertFalse(p.rectangle)
        self.assertTrue(p.losange)
        self.assertFalse(p.carre)
        self.assertTrue(p.parallelogramme)
        self.assertTrue(p.trapeze)
