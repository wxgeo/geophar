# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

from random import random, randint
import wx_unittest

from wxgeometrie.geolib import (
    Objet, Objet_avec_coordonnees, Objet_avec_equation,
    Objet_avec_coordonnees_modifiables, Objet_avec_valeur,
)

class GeolibTest(wx_unittest.TestCase):

    def test_Objet(self):
        O = Objet()
        O = Objet_avec_coordonnees()
        O = Objet_avec_coordonnees_modifiables()
        O = Objet_avec_equation()
        O = Objet_avec_valeur()

        def attrib1():
            O.attribut_bidon = None
            return
        self.assertRaises(AttributeError, attrib1)

        def attrib2():
            print(O.attribut_bidon)
            return
        self.assertRaises(AttributeError, attrib2)

