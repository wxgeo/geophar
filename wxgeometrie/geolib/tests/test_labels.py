# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

import wx_unittest, unittest

from wxgeometrie.geolib.tests.geotestlib import rand_pt
from wxgeometrie.geolib import Feuille, Segment

class GeolibTest(wx_unittest.TestCase):
    def test_Label_point(self):
        A = rand_pt()
        B = rand_pt()
        A.label("Position de l'hirondelle d'Afrique.")
        B.label("Position de l'hirondelle européenne.")
        self.assertEqual(A.label(), "Position de l'hirondelle d'Afrique.")
        self.assertEqual(B.label(), "Position de l'hirondelle européenne.")
        A.label(mode='nom')
        self.assertEqual(A.mode_affichage, 'nom')
        self.assertEqual(A.label(), '')
        f = Feuille()
        f.objets.A = A
        self.assertIs(A.feuille, f)
        self.assertIs(A.etiquette.feuille, f)
        self.assertEqual(A.nom_latex, '$A$')
        self.assertEqual(A.label(), '$A$')
        A.renommer("A'")
        self.assertEqual(A.label(), "$A'$")
        A.renommer("A''")
        self.assertEqual(A.label(), "$A''$")
        f.objets["B'"] = (1, 2)
        self.assertEqual(f.objets["B'"].label(), "$B'$")


    def test_Label_segment(self):
        f = Feuille()
        s = f.objets.s = Segment()
        self.assertEqual(s.label(), '')
        s.label('bonjour !')
        self.assertEqual(s.label(), 'bonjour !')
        s.label(mode='nom')
        self.assertEqual(s.label(), r'$\mathscr{s}$')


    @unittest.expectedFailure
    def test_Label_droite(self):
        raise NotImplementedError

    @unittest.expectedFailure
    def test_Label_demidroite(self):
        raise NotImplementedError

    @unittest.expectedFailure
    def test_Label_cercle(self):
        raise NotImplementedError

    @unittest.expectedFailure
    def test_Label_arc_cercle(self):
        raise NotImplementedError

    @unittest.expectedFailure
    def test_Label_polygone(self):
        raise NotImplementedError

    @unittest.expectedFailure
    def test_Label_angle(self):
        raise NotImplementedError

    def test_latex_incorrect(self):
        "On teste le comportement en cas de code LaTeX incorrect."
        A = rand_pt()
        A.label('2$')
        self.assertEqual(A.label(), r'2\$')
        A.label('US$2.50')
        self.assertEqual(A.label(), r'US\$2.50')
        A.label('$M__i$')
        self.assertEqual(A.label(), r'\$M__i\$')
        A.label('2$')

    def test_changement_mode(self):
        "Test pour les issues FS#240 et FS#266."
        A = rand_pt()
        f = Feuille()
        f.objets.A = A
        A.label('-6', 'formule')
        self.assertEqual(A.label(), '-6')
        self.assertEqual(A.legende, '{-6}')
        A.label('-3', 'texte')
        self.assertEqual(A.legende, '-3')
        A.x = -7
        A.label('A.x', 'formule')
        self.assertEqual(A.legende, '{A.x}')
        self.assertEqual(A.label(), '-7')
        # Il ne doit pas y avoir d'erreur : le changement de mode doit être
        # effectué **avant** le changement de texte.
        A.label('-----', 'texte')
        self.assertEqual(A.legende, '-----')
        self.assertEqual(A.label(), '-----')
