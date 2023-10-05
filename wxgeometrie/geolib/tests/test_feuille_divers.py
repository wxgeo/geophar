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
    Droite_equation, Cercle_equation, Courbe, Formule
)
from wxgeometrie.geolib.routines import nice_display
from wxgeometrie.geolib.feuille import parse_equation, is_equation

import tools.unittest

class GeolibTest(tools.unittest.TestCase):

    def test_variables_composees_1(self):
        f = Feuille()
        A = f.objets.A = Point()
        B = f.objets.B = Point()
        A(-5, 13)
        B.x = A.x
        self.assertTrue(B.x == B.coordonnees[0] == A.x == -5)
        A(1, 9)
        self.assertTrue(B.x == B.coordonnees[0] == -5 and A.x == 1)
        B.x="A.x"
        A(17, 5)
        self.assertTrue(B.coordonnees[0] == B.x == 17)

    def test_variables_composees_2(self):
        f = Feuille()
        f.objets.M1 = Point(-1.27482678984, 1.69976905312)
        f.objets.M2 = Point(2.42032332564, 1.25635103926)
        f.objets.s1 = Segment(f.objets.M1,f.objets.M2)
        f.objets.M1(-2.77136258661, 2.91916859122)
        f.objets.M1(4.74826789838, -1.07159353349)
        f.objets.M5 = Point(-5.11778290993, 2.30946882217)
        f.objets.M6 = Point(-1.86605080831, 3.25173210162)
        f.objets.s4 = Segment(f.objets.M5,f.objets.M6)
        f.objets.M5(-5.59815242494, 2.34642032333)
        f.objets.M1(-2.42032332564, -1.60739030023)
        f.objets.M6(-1.86605080831, 3.25173210162)
        f.objets.M6.renommer('B', afficher_nom=True)
        f.objets.M6 = Point(2.91916859122, 3.5103926097)
        f.objets.M6.label('B.x', mode='formule')
        f.objets.B(-1.18244803695, 1.25635103926)
        f.objets.M6.supprimer()
        f.objets.B(-2.21709006928, 2.64203233256)
        f.objets.M6 = Point(-6.6143187067, 0.443418013857)
        f.objets.M6.renommer('C', afficher_nom=True)
        f.objets.C.x=f.objets.B.x
        f.objets.B(-3.17782909931, 3.36258660508)
        f.objets.C.x="B.x"
        f.objets.B(-4.74826789838, 3.47344110855)
        f.objets.B(-1.99538106236, 3.63972286374)
        self.assertTrue(f.objets.C.coordonnees[0] == f.objets.C.x == \
                        f.objets.B.coordonnees[0] == f.objets.B.x)

    def test_polygones_et_representants_de_vecteurs(self):
        f = Feuille()
        f.objets.A = A = rand_pt()
        f.objets.B = B = rand_pt()
        f.objets.C = C = rand_pt()
        f.objets.p = Parallelogramme(A, B, C)
        f.objets.S1.renommer("D")
        s = 'p=%s\nD=%s' % (repr(f.objets.p), repr(f.objets.D))
        del f.objets.p
        self.assertNotIn("D", f.objets)
        exec(s, f.objets)
        self.assertIn("D", f.objets)
        self.assertIs(f.objets.D, f.objets.p.sommets[3])

    def test_relier_point_axes(self):
        f = Feuille()
        M1 = f.objets.M1 = Point(-1.27482678984, 1.69976905312)
        M2 = f.objets.M2 = Point(2.42032332564, 1.25635103926)
        Mx = M1.relier_axe_x()
        self.assertEqual(Mx.x, M1.x)
        self.assertEqual(Mx.y, 0)
        self.assertEqual(Mx.label(), '$%s$' % nice_display(M1.x))
        self.assertEqual(Mx.label(), '$%s$' % nice_display(-1.27482678984))
        My = M2.relier_axe_y()
        self.assertEqual(My.x, 0)
        self.assertEqual(My.y, M2.y)
        self.assertEqual(My.label(), '$%s$' % nice_display(M2.y))


    def test_formules(self):
        f = Feuille()
        o = f.objets
        o.A = Point(e, 3)
        o.M = Point()
        o.M.label('{1/ln(A.x) + A.y}', mode='formule')

        # Détails d'implémentation (peut être modifié par la suite)
        self.assertEqual(o.M.mode_affichage, 'formule')
        self.assertEqual(o.M.etiquette.texte, '{1/ln(A.x)+A.y}')
        self.assertIsInstance(o.M.etiquette.formule, Formule)

        # Par contre, ceci doit rester valable quelle que soit l'implémentation !
        self.assertAlmostEqual(float(o.M.label()), 4.)
        o.A.x = e**2
        with contexte(separateur_decimal='.'):
            self.assertEqual(o.M.label(), '3.5')
        with contexte(separateur_decimal=','):
            self.assertEqual(o.M.label(), '3,5')


    def test_constantes(self):
        f = Feuille()
        self.assertAlmostEqual(f.objets.pi, 3.1415926535897931)
        self.assertAlmostEqual(f.objets.e, 2.7182818284590451)

    def test_modification_variable(self):
        f = Feuille()
        o = f.objets
        o.a = Variable(1)
        o.fa = "5*sin(4/(a+.5))-1.5"
        o.A = Point(o.a, o.fa)
        o.fa = "-5*sin(4/(a+.5))+5.5"
        o.A = Point(2, o.fa)
        self.assertAlmostEqual(o.A.x, 2)
        self.assertAlmostEqual(o.A.y, o.fa)

    def test_fenetre(self):
        f = Feuille()
        f.fenetre = -4, 8, -2, 10
        self.assertEqual(f.objets.xmin, -4)
        self.assertEqual(f.objets.xmax, 8)
        self.assertEqual(f.objets.ymin, -2)
        self.assertEqual(f.objets.ymax, 10)
        # Bornes inversées
        f.fenetre = 7, -8, 3, -1
        self.assertEqual(f.objets.xmin, -8)
        self.assertEqual(f.objets.xmax, 7)
        self.assertEqual(f.objets.ymin, -1)
        self.assertEqual(f.objets.ymax, 3)
        # Accès isolé à une borne
        f.objets.xmin += 2
        self.assertEqual(f.objets.xmin, -6)
        self.assertEqual(f.fenetre, (-6, 7, -1, 3))
        # Objet dépendant d'une borne
        f.objets.A = Point("xmin - 1", "ymax + 1")
        self.assertEqual(f.objets.A.xy, (-7, 4))
        f.objets.xmin = 3
        f.objets.ymax = f.objets.ymin + 10
        self.assertEqual(f.objets.A.xy, (2, 10))


    def test_dependances(self):
        f = Feuille()
        A = f.objets.A = Point(1, 2)
        B = f.objets.B = Point("A.x+1", "A.y-1")
        self.assertEqual(B.xy, (2, 1))
        f.objets.A = (8, 9)
        self.assertEqual(B.xy, (9, 8))
        f.objets.B = ("A.x+1", "A.y-1")
        self.assertEqual( B.xy, (9, 8))
        f.objets.A = Point(0, 2)
        self.assertEqual(B.xy,  (1, 1))
        f.objets.B = Point("A.x+1", "A.y-1")
        self.assertIs(f.objets.B, B)
        self.assertIs(f.objets.A, A)
        self.assertEqual(B.xy, (1, 1))
        f.objets.A = (5, 7)
        self.assertEqual(B.xy, (6, 6)) # FAIL


    def test_is_equation(self):
        self.assertTrue(is_equation("2*x+3*y=5"))
        self.assertTrue(is_equation("x=5"))
        self.assertTrue(is_equation("y=a*x**2+c*x-2*y"))
        self.assertTrue(is_equation("y*(x-2)=3"))

        # Affectations
        self.assertFalse(is_equation("a = 5"))
        self.assertFalse(is_equation("a += 3"))
        self.assertFalse(is_equation("B.x = 5"))
        self.assertFalse(is_equation("B.y -= 3"))
        self.assertFalse(is_equation("B.style(x=2)"))


    def test_parse_equation(self):
        d = dict(globals())
        s = parse_equation("x=2*y-3")
        exec(s, d)
        self.assertEqual(d['_'].equation, (1, -2, 3))
        s = parse_equation("(x-2)**2+(y-3)**2=49")
        exec(s, d)
        self.assertEqual(d['_'].rayon, 7)
        self.assertEqual(d['_'].centre.xy, (2, 3))
        s = parse_equation("y=ln(x)-1")
        exec(s, d)
        self.assertIsInstance(d['_'], Courbe)

