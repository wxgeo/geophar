# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from tools.testlib import rand
#from wxgeometrie.geolib import (Point, Segment, Droite, Cercle, Vecteur, Variable, Polygone,
#                    Vecteur_libre, Droite_equation, Cercle_equation, Angle, Mediatrice,
#                    Arc_cercle, Demidroite, Milieu, Carre, Rectangle, Barycentre,
#                    Reflexion, Homothetie, Rotation, Translation, Representant,
#                    Triangle, Feuille, Fonction, Parallelogramme, contexte, Texte,
#                    RIEN, TEXTE, FORMULE, NOM)

from wxgeometrie.geolib import Point, Vecteur_libre, Droite_equation, Cercle_equation

def rand_pt():
    return Point(rand(), rand())

def rand_vec():
    return Vecteur_libre(rand(), rand())

def rand_dte():
    return Droite_equation(rand(), rand(), rand())

def rand_cercle():
    a = rand()
    b = rand()
    c = (a**2+b**2-abs(rand()))/4
    return Cercle_equation(a, b, c)
