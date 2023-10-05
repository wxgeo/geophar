# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

from math import sqrt
from random import random, randint

import wx_unittest
from wxgeometrie.geolib.tests.geotestlib import rand_pt
from wxgeometrie.geolib import (
    Tangente, Perpendiculaire, Parallele, Mediatrice,
    Droite_vectorielle, Point, Cercle, Droite,
    Bissectrice, Label_droite, Label_demidroite,
    Label_segment, Droite_equation, Milieu, Segment,
    Barycentre, Vecteur_libre, Demidroite, Demiplan,
)

from wxgeometrie.geolib import (
    Interpolation_polynomiale_par_morceaux,
    Glisseur_courbe, Tangente_glisseur_interpolation
)

class GeolibTest(wx_unittest.TestCase):

    def test_Segment(self):
        A = Point(4.5,  7.3)
        B = Point(4,  2.1)
        s = Segment(A,  B)
        self.assertIsInstance(s.etiquette, Label_segment)
        self.assertAlmostEqual(s.longueur, sqrt((B.x - A.x)**2 + (B.y - A.y)**2))
        I = Milieu(s.point1,  s.point2)
        self.assertEqual(I.coordonnees,  ((A.x+B.x)/2, (A.y+B.y)/2))
        M = Barycentre((A,  1),  (B,  -2))
        N = Barycentre((A,  -2),  (B,  1))
        self.assertIn(I, s)
        self.assertNotIn(M, s)
        self.assertNotIn(N, s)
        self.assertEqual(s.mode_affichage, 'rien')
        K = Point(s, 0.5)
        self.assertTrue(K.confondu(I))

    def test_Demidroite(self):
        A = Point(4.5,  7.3)
        B = Point(4,  2.1)
        s = Demidroite(A,  B)
        self.assertIsInstance(s.etiquette, Label_demidroite)
        self.assertRaises(AttributeError,  getattr,  s, "longueur")
        I = Milieu(s.origine,  s.point)
        self.assertEqual(I.coordonnees,  ((A.x+B.x)/2, (A.y+B.y)/2))
        M = Barycentre((A,  1),  (B,  -2))
        N = Barycentre((A,  -2),  (B,  1))
        self.assertIn(I, s)
        self.assertIn(M, s)
        self.assertNotIn(N, s)
        self.assertEqual(s.mode_affichage, 'rien')

    def test_Droite(self):
        A = Point(4.5,  7.3)
        B = Point(4,  2.1)
        d = Droite(A,  B)
        self.assertIsInstance(d.etiquette, Label_droite)
        self.assertRaises(AttributeError,  getattr,  d, "longueur")
        I = Milieu(d.point1,  d.point2)
        self.assertEqual(I.coordonnees,  ((A.x+B.x)/2, (A.y+B.y)/2))
        M = Barycentre((A,  1),  (B,  -2))
        N = Barycentre((A,  -2),  (B,  1))
        self.assertIn(I, d)
        self.assertIn(M, d)
        self.assertIn(N, d)
        self.assertIsInstance(d.equation,  tuple)
        self.assertEqual(d.mode_affichage, 'rien')
        # Test du typage dynamique
        d = Droite("y=x+1")
        self.assertIn(Point(0, 1), d)
        d = Droite(Point(1, 2), Vecteur_libre(1, 1))
        self.assertIn(Point(1, 2), d)
        self.assertIn(Point(2, 3), d)
        d2 = Droite("y=-x+1")
        self.assertIn(Point(0, 1), d2)
        self.assertIn(Point(1, 0), d2)



    def test_Droite_vectorielle(self):
        v = Vecteur_libre(1,  7)
        A = Point(-2, 3)
        d = Droite_vectorielle(A,  v)
        self.assertTrue(d.vecteur is v and d.point is A)
        self.assertAlmostEqual(v.y/v.x,  -d.equation[0]/d.equation[1])
        B = rand_pt()
        d1 = Droite_vectorielle(B, v)
        self.assertTrue(d.parallele(d1))

    def test_Parallele(self):
        d0 = Droite_equation(2,  1,  7)
        A = Point(-2, 3)
        d = Parallele(d0,  A)
        self.assertTrue(d.parallele(d0))
        self.assertTrue(d.droite is d0 and d.point is A)
        self.assertAlmostEqual(d0.equation[:1],  d.equation[:1])

    # def test_Droite_rotation(self):
    #     r = Rotation(Point(1.45, -2.59), math.pi/3)
    #     C = Point(1.458, -5.255)
    #     D = Point(3.478, -2.14788)
    #     d = Droite(C, D)
    #     # Dans ce qui suit, d1, d2 et d3 doivent correspondre à la même droite.
    #     d1 = Droite_rotation(d,  r)
    #     d2 = Droite(r(C), r(D))
    #     d3 = r(d)
    #     a, b, c = d1.equation
    #     self.assertAlmostEqual(d1.equation_reduite, d2.equation_reduite)
    #     self.assertAlmostEqual(d1.equation_reduite, d3.equation_reduite)
    #     self.assertAlmostEqual(d1.equation_reduite, (-a/b, -c/b))
    #     d = Droite_rotation(Droite_equation(1, -1, 1),  Rotation(Point(0, 0), math.pi/2))
    #     a, b, c = d.equation
    #     self.assertAlmostEqual(b/a,  1)
    #     self.assertAlmostEqual(c/a,  1)


    def test_Mediatrice(self):
        A = Point(4.5,  7.3)
        B = Point(-4.147,  2.1)
        s = Segment(A,  B)
        d0 = Mediatrice(s)
        d1 = Mediatrice(A,  B)
        I = Milieu(A,  B)
        self.assertIn(I, d0)
        self.assertIn(I, d1)
        a,  b,  c = s.equation
        a0,  b0,  c0 = d0.equation
        self.assertAlmostEqual(a*a0 + b*b0,  0)
        self.assertAlmostEqual(d0.equation,  d1.equation)

    def test_Perpendiculaire(self):
        d = Droite_equation(-1, 2, 0)
        M = Point()
        d0 = Perpendiculaire(d,  M)
        a,  b,  c = d.equation
        a0,  b0,  c0 = d0.equation
        self.assertTrue(d.perpendiculaire(d0))
        self.assertAlmostEqual(a*a0 + b*b0,  0)
        self.assertIn(M, d0)

    def test_Droite_equation(self):
        a = randint(0,50) - randint(0,50) + 0.1 # afin que a ne soit pas nul
        b = randint(0,50) - randint(0,50) + random()
        c = randint(0,50) - randint(0,50) + random()
        d, e, f = Droite_equation(a, b, c).equation
        self.assertAlmostEqual((e/d, f/d),  (b/a, c/a))
        self.assertEqual(Droite_equation(a, 0, 0).equation[1:],  (0, 0))
        self.assertEqual((Droite_equation(0, a, 0).equation[0], Droite_equation(0, a, 0).equation[2]),  (0, 0))
        self.assertFalse(Droite_equation(0, 0, 0).existe)
        d = Droite_equation("y=-5/2x-3/2")
        self.assertIn(Point(0, -1.5), d)
        self.assertIn(Point(-1, 1), d)
        d = Droite_equation("x=2*10**2")
        self.assertIn(Point(200, -1000), d)
        self.assertNotIn(Point(100, -1000), d)
        d = Droite_equation("2*x+2*y=1")
        self.assertIn(Point(0.5, 0), d)
        self.assertIn(Point(1, -0.5), d)
        d = Droite_equation("x+y=1")
        self.assertIn(Point(0, 1), d)
        self.assertIn(Point(1, 0), d)
        d = Droite_equation("x+2y=-2")
        self.assertIn(Point(0, -1), d)
        self.assertIn(Point(-2, 0), d)

    def test_Bissectrice(self):
        A = Point(1, -5)
        B = Point(1.5, -5.3)
        C = Point(3, -4)
        d = Bissectrice(A,  B,  C)
        a, b, c = d.equation
        d,  e = (0.0870545184921, -1.03861105199)
        self.assertAlmostEqual(b/a, d)
        self.assertAlmostEqual(c/a, e)

    def test_Tangente(self):
        A = Point(4.75, -2.56887)
        O = Point(2.56874, -85.2541)
        M = Point(7.854, -552.444)
        c = Cercle(O, A)
        d = Tangente(c, A)
        self.assertIn(A, d)
        self.assertNotIn(M, d)
        d1 = Tangente(c, M)
        self.assertIn(M, d1)
        self.assertNotIn(A, d1)
        self.assertFalse( Tangente(c, O).existe)

    def test_equation_formatee(self):
        self.assertEquals(Droite('y=x').equation_formatee, '-x + y = 0')

    def test_Demiplan(self):
        d = Droite('y=-x+1')
        P1 = Demiplan(d, Point(0, 0), True)
        P2 = Demiplan(d, Point(0, 0), False)
        self.assertIn(Point(0, 0), P1)
        self.assertIn(Point(1, 0), P1)
        self.assertIn(Point(0, 0), P2)
        self.assertNotIn(Point(1, 0), P2)


    ##def test_Tangente_courbe_interpolation(self):
        ##A = Point(-6, -1)
        ##B = Point(-3, 2)
        ##C = Point(-0.5, -1)
        ##D = Point(2.6, 1.1)
        ##inter = Interpolation_polynomiale_par_morceaux(A, B, C, D)
        ##T = Tangente_courbe_interpolation(inter, x= 2.)
        ### la tangente doit passer par M par construction
        ##self.assertAlmostEqual( T.xy(2), (2, inter.fonction(2)))
        ### son coef dir doit être la dérivée sur le point de passage
        ##self.assertAlmostEqual( -T.a / T.b, inter.fonction.derivative(2, 1))


    def test_Tangente_glisseur_interpolation(self):
        A = Point(-6, -1)
        B = Point(-3, 2)
        C = Point(-0.5, -1)
        D = Point(2.6, 1.1)
        inter = Interpolation_polynomiale_par_morceaux(A, B, C, D)
        M = Glisseur_courbe(inter, 2)
        T = Tangente_glisseur_interpolation(inter, M)
        # la tangente doit passer par M par construction
        self.assertAlmostEqual(T.xy(M.x), (M.x, M.y))
        # son coef dir doit etre la dérivée sur le glisseur
        self.assertAlmostEqual((float(-T.a)/float(T.b)),
                          inter.fonction(M.x, 1)) # dérivée première en M.x
        # rebelotte après déplacement du glisseur
        M.x = 1
        self.assertAlmostEqual(T.xy(M.x), (M.x, M.y))
        self.assertAlmostEqual((float(-T.a)/float(T.b)),
                          inter.fonction(M.x, 1))
