# -*- coding: utf-8 -*-
import os, sys
TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"../.."))
sys.path.insert(0, TOPDIR)

import wx_unittest

from random import randint, random
from wxgeometrie.geolib import Texte

def rand():
    return randint(0,50) - randint(0,50) + random()

class GeolibTest(wx_unittest.TestCase):
    def test_Texte(self):
        t = Texte("spam & eggs", rand(), rand())
        self.assertEqual(t.texte, "spam & eggs")

    def test_style_temporaire(self):
        # Le pseudo-style `nouveau_texte` est utilisé pour indiquer qu'un texte
        # vient d'être créé. Ceci permet que, lorsque l'utilisateur clique
        # quelque part pour créer un texte, puis appuie sur [ESC], le texte
        # soit aussitôt supprimé, au lieu de créer un texte vide.
        t = Texte("blabla", nouveau_texte=True)
        del t._style['nouveau_texte']
