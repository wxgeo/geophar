# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from random import random

from tools.testlib import assertAlmostEqual, assertEqual, randint, assertRaises
from wxgeometrie.geolib import (Objet, Objet_avec_coordonnees, Objet_avec_equation,
                                Objet_avec_coordonnees_modifiables, Objet_avec_valeur,
                                Objet_numerique
                               )



def test_Objet():
    O = Objet()
    O = Objet_avec_coordonnees()
    O = Objet_avec_coordonnees_modifiables()
    O = Objet_avec_equation()
    O = Objet_avec_valeur()
    O = Objet_numerique()
    # Les attributs publiques doivent être déclarés:
    try:
        O.attribut_bidon = None
    except AttributeError:
        # On teste que l'attribut non déclaré ne peut pas être affecté.
        pass
    else:
        assert False
    # Les attributs publiques doivent être déclarés:
    try:
        print(O.attribut_bidon)
    except AttributeError:
        # On teste que l'attribut non déclaré ne peut pas être lu.
        pass
    else:
        assert False
