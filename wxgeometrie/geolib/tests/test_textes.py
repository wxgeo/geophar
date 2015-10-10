# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from tools.testlib import rand
from wxgeometrie.geolib import Texte


def test_Texte():
    t = Texte("spam & eggs", rand(), rand())
    assert(t.texte == "spam & eggs")

def test_style_temporaire():
    # Le pseudo-style `nouveau_texte` est utilisé pour indiquer qu'un texte
    # vient d'être créé. Ceci permet que, lorsque l'utilisateur clique
    # quelque part pour créer un texte, puis appuie sur [ESC], le texte
    # soit aussitôt supprimé, au lieu de créer un texte vide.
    t = Texte("blabla", nouveau_texte=True)
    del t._style['nouveau_texte']
