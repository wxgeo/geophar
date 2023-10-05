# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

import wx_unittest, unittest
from random import random, randint
import pytest
from sympy import sympify as symp

from wxgeometrie.geolib.tests.geotestlib import rand_pt, rand_cercle

from wxgeometrie.geolib import (
    Glisseur_arc_cercle, Glisseur_cercle, Glisseur_demidroite,
    Glisseur_droite, Point, Demidroite, Droite,
    Glisseur_segment, Point_equidistant, Centre,
    Centre_cercle_inscrit, Centre_cercle_circonscrit,
    Orthocentre, Projete_demidroite, Projete_segment,
    Projete_arc_cercle, Projete_cercle, Segment,
    Projete_droite, Centre_gravite, Label_point,
    Point_reflexion, Point_homothetie, Cercle,
    Point_rotation, Point_translation, Point_final,
    Arc_points, Arc_cercle, Triangle, Milieu,
    Barycentre, Mediatrice, Droite_equation,
    Cercle_equation, Polygone, Rotation, Translation,
    Vecteur, Vecteur_libre, Representant, Reflexion,
    Homothetie, Nuage, Fonction, Point_interpolation,
)

class GeolibTest(wx_unittest.TestCase):
    def test_Point(self):
        A = Point(1, 2)
        self.assertIsInstance(A.etiquette, Label_point)
        self.assertEqual(A.x, 1)
        self.assertEqual(A.y, 2)
        self.assertEqual(type(A.coordonnees),  tuple)
        A.x = 5
        A.y = 7
        self.assertEqual(A.coordonnees, (5, 7))
        self.assertEqual(A.mode_affichage, 'nom')
        # Test du typage dynamique
        d = Droite(rand_pt(), rand_pt())
        B = Point(d)
        self.assertIsInstance(B, Glisseur_droite)
        c = Cercle(A, 3)
        C = Point(c)
        self.assertIsInstance(C, Glisseur_cercle)
        d = Demidroite(rand_pt(), rand_pt())
        B = Point(d)
        self.assertIsInstance(B, Glisseur_demidroite)
        s = Segment(rand_pt(), rand_pt())
        B = Point(s)
        self.assertIsInstance(B, Glisseur_segment)
        a = Arc_points(Point(), Point(1, 1),  Point(1, 2))
        B = Point(a)
        self.assertIsInstance(B, Glisseur_arc_cercle)

    def test_Point_sympy(self):
        A = Point('1/2', '2/3')
        self.assertEqual(A.x, symp('1/2'))
        self.assertAlmostEqual(A.coordonnees, (1/2, 2/3))


    def test_Milieu(self):
        A = Point(1,2)
        B = Point(2,4)
        I = Milieu(A,B)
        self.assertTrue(I.x == (A.x+B.x)/2 and I.y == (A.y+B.y)/2)
        self.assertEqual(type(I.coordonnees),  tuple)
        C = Point('1/3', '1')
        D = Point('1', '1')
        J = Milieu(C, D)
        self.assertEqual(J.x, symp('2/3'))


    def test_Barycentre(self):
        M = Point(3, 4)
        A = Point(1,2)
        B = Point(2,4)
        I = Milieu(A,B)
        K = Barycentre(M, A, B, (I, -4))
        self.assertEqual(K.x,  0)
        self.assertEqual(K.y,  2)
        self.assertFalse(Barycentre(M, A, (B, -2)).existe)
        self.assertEqual(type(K.coordonnees),  tuple)
        # Test keyword 'points_ponderes'
        G = Barycentre(points_ponderes = (M, A, B, (I, -4)))
        self.assertEqual(K.coordonnees, G.coordonnees)
        self.assertNotIn("point_ponderes", G.style())

    def test_Point_final(self):
        A = Point(random(),random())
        C = Point(random(),random())
        u = Vecteur_libre(random(),random())
        v = Vecteur(Point(random(),  random()),  Point(random(),  random()))
        w = Representant(Vecteur(Point(random(),  random()),  Point(random(),  random())),  A)
        F = Point_final(C,  (u, v, w), (-2, 1.5, 4))
        self.assertEqual(type(F.coordonnees),  tuple)
        self.assertAlmostEqual(F.x,  C.x -2*u.x+1.5*v.x+4*w.x)
        self.assertAlmostEqual(F.y,  C.y -2*u.y+1.5*v.y+4*w.y)

    def test_Point_translation(self):
        u = Vecteur_libre(1.56, 2.78)
        v = Vecteur(Point(1.1457, 2.7895), Point(2.458, -8.25))
        A = Point(5.256, -7.231)
        tu = Translation(u)
        tv = Translation(v)
        Au = Point_translation(A, tu)
        Av = Point_translation(A, tv)
        self.assertAlmostEqual(Au.coordonnees,  (6.816, -4.451))
        self.assertAlmostEqual(Av.coordonnees, (6.5683, -18.2705))

    def test_Point_rotation(self):
        A = Point(1, -4)
        r = Rotation(Point(-2, 7.56), 4.25)
        B = Point_rotation(A, r)
        self.assertAlmostEqual(r(A).coordonnees, B.coordonnees)
        self.assertAlmostEqual(B.coordonnees,  (-13.684339450863803, 10.031803308717693))
        A = Point('1',  '0')
        r = Rotation(('0', '0'), 'pi/4')
        B = Point_rotation(A, r)
        C = Point('sqrt(2)/2', 'sqrt(2)/2')
        self.assertTrue(C.x == B.x and C.y == B.y)

    def test_Point_homothetie(self):
        A = Point(1, -2)
        h = Homothetie(A, -3)
        M = Point(2, 7)
        self.assertAlmostEqual(Point_homothetie(M, h).coordonnees, (-2, -29))
    #    self.assertIs(Point_homothetie(A, h), A)   -> méthode __new__ ?

    def test_Point_reflexion(self):
        d = Droite_equation(1, 6, -2)
        r = Reflexion(d)
        M = Point(random()+randint(0,50)-randint(0,50), random()+randint(0,50)-randint(0,50))
        m = Mediatrice(M,  Point_reflexion(M, r))
        self.assertAlmostEqual(d.equation_reduite,  m.equation_reduite)

    def test_Projete_droite(self):
        d = Droite_equation(1.25, -7.12, 2.15)
        A = Point(1.52, 2.14)
        M = Projete_droite(A, d)
        self.assertIn(M, d)
        self.assertTrue(Droite(A, M)._perpendiculaire(d))

    def test_Projete_cercle(self):
        c = Cercle_equation(1, -2, -20)
        self.assertTrue(c.existe)
        A = Point(randint(0,50) - randint(0,50) + random(), randint(0,50) - randint(0,50) + random())
        P = Projete_cercle(A, c)
        self.assertTrue(P.existe)
        self.assertIn(P, c)
        self.assertIn(P, Demidroite(c.centre, A))
        A.coordonnees = c.centre.coordonnees
        self.assertFalse(P.existe)

    def test_Projete_arc_cercle(self):
        O = Point(23.15, -12.75)
        A = Point(-12.5, 7.14)
        B = Point(7.15, 8.64)
        a = Arc_cercle(O, A, B)
        M = rand_pt()
        P = Projete_arc_cercle(M, a)
        self.assertIn(P, a)
        M.coordonnees = a.centre.coordonnees
        self.assertFalse(P.existe)
        M.coordonnees = -17.826266675199999, 11.760911186
        self.assertIs(type(P.coordonnees), tuple)
        self.assertAlmostEqual(A.coordonnees, P.coordonnees)
        self.assertTrue(A.confondu(P))

    def test_Projete_segment(self):
        s = Segment(rand_pt(), rand_pt())
        M = rand_pt()
        self.assertIn(Projete_segment(M, s), s)
        A = Point(0, 1)
        B = Point(2, 1)
        s = Segment(A, B)
        M = Point(1, 7.15)
        P = Projete_segment(M, s)
        self.assertAlmostEqual(Milieu(A, B).coordonnees, P.coordonnees)
        M.x = .5
        self.assertAlmostEqual(Barycentre((A, 3), (B, 1)).coordonnees, P.coordonnees)
        M.x = -1
        self.assertAlmostEqual(A.coordonnees, P.coordonnees)
        M.x = 3
        self.assertAlmostEqual(B.coordonnees, P.coordonnees)


    def test_Projete_demidroite(self):
        d = Demidroite(rand_pt(), rand_pt())
        M = rand_pt()
        self.assertIn(Projete_demidroite(M, d), d)
        A = Point(0, 1)
        B = Point(2, 1)
        s = Demidroite(A, B)
        M = Point(1, 7.15)
        P = Projete_demidroite(M, s)
        self.assertAlmostEqual(Milieu(A, B).coordonnees, P.coordonnees)
        M.x = .5
        self.assertAlmostEqual(Barycentre((A, 3), (B, 1)).coordonnees, P.coordonnees)
        M.x = -1
        self.assertAlmostEqual(A.coordonnees, P.coordonnees)
        M.x = 3
        self.assertAlmostEqual(Barycentre((A, -1), (B, 3)).coordonnees, P.coordonnees)


    def test_Centre_gravite(self):
        A = rand_pt()
        B = rand_pt()
        C = rand_pt()
        I = Milieu(B, C)
        J = Milieu(A, C)
        K = Milieu(A, B)
        G = Centre_gravite(Triangle(A, B, C))
        self.assertAlmostEqual(Segment(A, G).longueur, 2*Segment(I, G).longueur)
        self.assertAlmostEqual(Segment(B, G).longueur, 2*Segment(J, G).longueur)
        self.assertAlmostEqual(Segment(C, G).longueur, 2*Segment(K, G).longueur)

    def test_Orthocentre(self):
        A, B, C = rand_pt(), rand_pt(), rand_pt()
        p = Polygone(A, B, C)
        H = Orthocentre(p)
        self.assertTrue(Droite(A, H).perpendiculaire(Droite(B, C)))
        self.assertTrue(Droite(B, H).perpendiculaire(Droite(A, C)))
        self.assertTrue(Droite(C, H).perpendiculaire(Droite(B, A)))

    def test_Centre_cercle_circonscrit(self):
        A, B, C = rand_pt(), rand_pt(), rand_pt()
        p = Polygone(A, B, C)
        O= Centre_cercle_circonscrit(p)
        self.assertTrue(O.confondu(Point_equidistant(A, B, C)))

    def test_Centre_cercle_inscrit(self):
        A, B, C = rand_pt(), rand_pt(), rand_pt()
        p = Polygone(A, B, C)
        I = Centre_cercle_inscrit(p)
        P = Projete_segment(I, Segment(B, C))
        Q = Projete_segment(I, Segment(A, C))
        R = Projete_segment(I, Segment(A, B))
        c = Cercle(I, P)
        self.assertTrue(P in c and Q in c and R in c)

    def test_Centre(self):
        c = rand_cercle()
        O = Centre(c)
        M = Glisseur_cercle(c)
        self.assertAlmostEqual(Segment(O, M).longueur, c.rayon)

    def test_Point_equidistant(self):
        A = rand_pt()
        B = rand_pt()
        C = rand_pt()
        P = Point_equidistant(A, B, C)
        self.assertAlmostEqual(Segment(A, P).longueur, Segment(B, P).longueur)
        self.assertAlmostEqual(Segment(A, P).longueur, Segment(C, P).longueur)
        self.assertIn(P, Mediatrice(A, B))

    def test_Glisseur_droite(self):
        A = rand_pt()
        B = rand_pt()
        d = Droite(A, B)
        M = Glisseur_droite(d)
        self.assertIn(M, d)
        M.k = 0
        self.assertEqual(M.k, 0)
        self.assertAlmostEqual(M.coordonnees, A.coordonnees)
        P = Point(*M.coordonnees)
        M.k = 1
        self.assertEqual(M.k, 1)
        self.assertAlmostEqual(M.coordonnees, B.coordonnees)
        M.k = 2
        self.assertEqual(M.k, 2)
        M.k = -1
        self.assertEqual(M.k, -1)
        Q = Point(*M.coordonnees)
        self.assertAlmostEqual(Droite(P, Q).equation_reduite, d.equation_reduite)
        M.k = 1.7
        M(*M.coordonnees)
        self.assertAlmostEqual(M.k, 1.7)


    def test_Glisseur_segment(self):
        A = rand_pt()
        B = rand_pt()
        s = Segment(A, B)
        M = Glisseur_segment(s)
        self.assertIn(M, s)
        M.k = 0
        self.assertEqual(M.k, 0)
        self.assertAlmostEqual(M.coordonnees, A.coordonnees)
        P = Point(*M.coordonnees)
        M.k = 1
        self.assertEqual(M.k, 1)
        self.assertAlmostEqual(M.coordonnees, B.coordonnees)
        M.k = 2
        self.assertEqual(M.k, 1) # 0<=k<=1 pour un segment
        self.assertIn(M, s)
        M.k = -1
        self.assertEqual(M.k, 0) # 0<=k<=1 pour un segment
        self.assertIn(M, s)
        M.k = 1
        Q = Point(*M.coordonnees)
        self.assertAlmostEqual(Droite(P, Q).equation_reduite, s.equation_reduite)
        M.k = 1.7
        M(*M.coordonnees)
        self.assertAlmostEqual(M.k, 1)

    def test_Glisseur_demidroite(self):
        A = rand_pt()
        B = rand_pt()
        d = Demidroite(A, B)
        M = Glisseur_demidroite(d)
        self.assertIn(M, d)
        M.k = 0
        self.assertEqual(M.k, 0)
        self.assertAlmostEqual(M.coordonnees, A.coordonnees)
        P = Point(*M.coordonnees)
        M.k = 1
        self.assertEqual(M.k, 1)
        self.assertAlmostEqual(M.coordonnees, B.coordonnees)
        M.k = 2
        self.assertEqual(M.k, 2)
        M.k = -1
        self.assertEqual(M.k, 0) # k>=0 pour une demi-droite
        M.k = 1
        Q = Point(*M.coordonnees)
        self.assertAlmostEqual(Droite(P, Q).equation_reduite, d.equation_reduite)
        M.k = 1.7
        M(*M.coordonnees)
        self.assertAlmostEqual(M.k, 1.7)

    def test_Glisseur_cercle(self):
        c = rand_cercle()
        M = Glisseur_cercle(c)
        self.assertIn(M, c)
        O = c.centre
        M.coordonnees = O.coordonnees
        # il faudrait compléter un peu

    def test_Glisseur_arc_cercle(self):
        A = rand_pt()
        B = rand_pt()
        C = rand_pt()
        a = Arc_cercle(A, B, C)
        M = Glisseur_arc_cercle(a)
        self.assertIn(M, a)
        O = a.centre
        M.coordonnees = O.coordonnees
        # il faudrait compléter un peu


    def test_Point_interpolation(self):
        A = Point(1, 2)
        P = Point_interpolation(A)
        self.assertIs(P.point, A)
        self.assertIsNone(P.derivee)

    @unittest.expectedFailure
    def test_Glisseur_courbe(self):
        f = Fonction('x^2+3x-1')
        M = Point(f, 2)
        self.assertEqual(f(2), 2**+3+2-1)
        self.assertEqual(M.y, f(2))

    def test_Nuage(self):
        A = rand_pt()
        B = rand_pt()
        C = rand_pt()
        D = rand_pt()
        while D in (A, B, C):
            D = rand_pt()
        n = Nuage(A, B, C)
        self.assertEqual(n.points, (A, B, C))
        self.assertIn(A, n)
        self.assertIn(B, n)
        self.assertIn(C, n)
        self.assertNotIn(D, n)

    @unittest.expectedFailure
    def test_NuageFonction(self):
        f = Fonction('x^2+3')
        m = Nuage(f, 0.5, 1, 2, 3, 4)
        self.assertIn((2, 2**2+3), m)

    def test_Centre_alias(self):
        "Centre et Centre_gravite sont interchangeables."
        A = rand_pt()
        B = rand_pt()
        C = rand_pt()
        G = Centre(Triangle(A, B, C))
        self.assertAlmostEqual(G.x, (A.x + B.x + C.x)/3)
        self.assertAlmostEqual(G.y, (A.y + B.y + C.y)/3)
        ce = Cercle(A, 1)
        G = Centre_gravite(ce)
        self.assertAlmostEqual(G.xy, A.xy)
