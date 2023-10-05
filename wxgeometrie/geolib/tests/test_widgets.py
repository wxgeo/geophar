# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

import tools.unittest, unittest

from random import randint, random
from wxgeometrie.geolib import Champ, Bouton

def rand():
    return randint(0,50) - randint(0,50) + random()

class TestGeolib(tools.unittest.TestCase):

    def test_Champ(self):
        champ = Champ('', 4, 3, couleur_fond='#ffffb5',
                      prefixe=(r"Combien vaut 1+1 ? "),
                      alignement_horizontal='left',
                      alignement_vertical='bottom',
                      attendu='2')
        points = 0

        def valider(reponse, attendu):
            return reponse.strip() == attendu

        def evt_valider(**kw):
            nonlocal points
            points = (5 if kw['correct'] else 1)

        champ.valider = valider
        champ.evt_valider = evt_valider

        champ.texte = '3'
        self.assertEqual(champ.label(), "Combien vaut 1+1 ? $3$")
        self.assertFalse(champ.correct)
        self.assertEqual(points, 1)
        champ.texte = '2'
        self.assertEqual(champ.label(), "Combien vaut 1+1 ? $2$")
        self.assertTrue(champ.correct)
        self.assertEqual(points, 5)
        champ.texte = ' 3 '
        self.assertFalse(champ.correct)
        self.assertEqual(points, 1)
        champ.texte = ' 2   '
        self.assertTrue(champ.correct)
        self.assertEqual(points, 5)

@unittest.expectedFailure
def test_Bouton():
    raise NotImplementedError
