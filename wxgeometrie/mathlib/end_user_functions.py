#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#   Mathlib 2 (sympy powered) #
##--------------------------------------#######
#WxGeometrie
#Dynamic geometry, graph plotter, and more for french mathematic teachers.
#Copyright (C) 2005-2010  Nicolas Pourcelot
#
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

# version unicode

## Les fonctions qui doivent être accessibles par l'utilisateur final
## "from end_user_functions import *" doit donner un résultat propre.
from ..pylib import OrderedDict

__classement__ = OrderedDict((
    (u"Algèbre", []),
    (u"Analyse", []),
    (u"Symboles", []),
    (u"Arithmétique", []),
    (u"Statistiques", []),
    (u"Divers", []),
##    (u"LaTeX", []),
))

del OrderedDict

from .universal_functions import abs, acos, asin, atan, ceil, cos, cosh, exp, floor,\
                                 ln, log, sin, sinh, sqrt, tan, tanh, arg


from sympy import LambertW, gamma, Sum, Integral

# Alias
arcsin = asin
arccos = acos
arctan = atan

from .custom_functions import derivee, moyenne, variance, ecart_type, covariance, linreg, aide


__classement__[u"Statistiques"].append((u"Moyenne", "moyenne", u"Moyenne de la série, éventuellement coefficientée."
                                     u" Ex: moyenne((12, 13, 15), (1, 1, 2))"))
__classement__[u"Statistiques"].append((u"Variance", "variance", u"Variance de la série, éventuellement coefficientée."
                                     u" Ex: variance((12, 13, 15), (1, 1, 2))"))
__classement__[u"Statistiques"].append((u"Écart-type", "ecart_type", u"Écart-type de la série, éventuellement coefficientée."
                                     u" Ex: ecart_type((12, 13, 15), (1, 1, 2))"))
__classement__[u"Statistiques"].append((u"Covariance", "covariance", u"Covariance de deux séries."
                                     u" Ex: covariance((1,2,3),(2,5,7))"))
__classement__[u"Statistiques"].append((u"Droite de régression", "linreg", u"Retourne (a, b) pour une droite d'ajustement d'équation y=ax+b"
                                     u" (moindres carrés). Ex: linreg((1,2,3),(2,5,7))"))

from .sympy_functions import expand
developpe = expand
__classement__[u"Algèbre"].append((u"Développe", "developpe", u"Développer une expression."))

from .sympy_functions import factor
factorise = factor
__classement__[u"Algèbre"].append((u"Factorise", "factorise", u"Factoriser une expression."))

from .sympy_functions import together
rassemble = together
__classement__[u"Algèbre"].append((u"Une seule fraction", "rassemble", u"Mettre sur le même dénominateur."))

from .sympy_functions import evalf
evalue = evalf
__classement__[u"Algèbre"].append((u"Évalue", "evalue", u"Calculer une valeur approchée."))

from .custom_functions import resoudre
solve = resous = resoudre
__classement__[u"Algèbre"].append((u"Résous", "resous", u"Résoudre une (in)équation ou un système dans R. ex: resous(2x-3>0 et 3x+1<=0"))

__classement__[u"Algèbre"].append(None)

from .sympy_functions import cfactor
cfactorise = cfactor
__classement__[u"Algèbre"].append((u"Factorise dans C", "cfactorise", u"Factoriser une expression dans le corps des complexes."))

from sympy import conjugate
conjug = conjugue = conjuguer = conjugate
__classement__[u"Algèbre"].append((u"Conjuguer", "conjug", u"Calculer le conjugué d'un nombre complexe."))

__classement__[u"Algèbre"].append(None)

from .sympy_functions import sum
somme = sum
__classement__[u"Algèbre"].append((u"Somme", "somme", u"Calculer une somme."))

from .sympy_functions import product
produit = product
__classement__[u"Algèbre"].append((u"Produit", "produit", u"Calculer un produit."))

__classement__[u"Algèbre"].append(None)

from .sympy_functions import mat
Matrice = Matrix = Mat = matrix = matrice = mat
__classement__[u"Algèbre"].append((u"Matrice", "mat", u"Génère une matrice. ex: mat([[1,2],[3,4]]), mat(4,4,0), mat(4,4,2*li+3*co)"))


from .sympy import isprime
premier = isprime
__classement__[u"Arithmétique"].append((u"Premier ?", "premier", u"Tester si un nombre est premier."))

from .sympy_functions import divisors
diviseurs = divisors
__classement__[u"Arithmétique"].append((u"Diviseurs", "diviseurs", u"Chercher les diviseurs d'un nombre."))

# Alias
facteurs = factors = factor
__classement__[u"Arithmétique"].append((u"Facteurs premiers", "facteurs", u"Décomposer un nombre en facteurs premiers."))

from .custom_functions import pgcd
gcd = pgcd
__classement__[u"Arithmétique"].append((u"PGCD", "pgcd", u"Calculer le PGCD de plusieurs entiers."))

from .custom_functions import ppcm
lcm = ppcm
__classement__[u"Arithmétique"].append((u"PPCM", "ppcm", u"Calculer le PPCM de plusieurs entiers."))

__classement__[u"Arithmétique"].append(None)

from .custom_functions import jhms
hms = jhms
__classement__[u"Divers"].append((u"Conversion j-h-min-s", "jhms", u"Convertir un temps en secondes en jours, heures, minutes et secondes."))

from .custom_functions import deg
__classement__[u"Divers"].append((u"Conversion en degrés", "deg", u"Convertir un angle de radians en degrés. (Ex: deg(pi/3), ou pi/3>>deg)."))

from .custom_functions import frac
__classement__[u"Divers"].append((u"Convertir en fraction", "frac", u"Convertir un nombre décimal en fraction."))

ent = floor
__classement__[u"Divers"].append((u"Partie entière", "ent", u"Partie entière d'un nombre (ex: -2,4 -> -3)."))

from .custom_functions import arrondir
round = arrondi = arrondis = arrondir
__classement__[u"Divers"].append((u"Arrondi", "arrondi", u"Arrondit à n chiffres après la virgule-3)."))


from sympy import factorial
factoriel = factorial
__classement__[u"Arithmétique"].append((u"Factoriel", "factoriel", u"factoriel(n) vaut 1*2*3*4*5*...*n."))

from sympy import ff
arrangements = nAr = nA = ff
__classement__[u"Arithmétique"].append((u"Arrangements", "nAr", u"Nombre d'arrangements."))

from sympy import binomial
combinaisons = binome = nCr = nC = Binomial = binomial
__classement__[u"Arithmétique"].append((u"Combinaisons", "nCr", u"Nombre de combinaisons."))

from .sympy_functions import limit
lim = limite = limit
__classement__[u"Analyse"].append((u"Limite", "limite", u"Calculer une limite. Ex: 'limite(1/x,x,0+)', 'limite(x^2,x,-oo)'"))

from .sympy_functions import diff
derive = diff
__classement__[u"Analyse"].append((u"Dérive", "derive", u"Dériver une expression. Ex: 'derive(2x+7,x)' et 'derive(2x+7,x,2)' (dérivée seconde)"))

from .sympy_functions import integrate
integrale = integral = integre = integrate
__classement__[u"Analyse"].append((u"Intègre", "integre", u"Intégrer une expression. Ex: 'integre(x+1,x)' et 'integre(x+1,(x,-1,1))"))

from .sympy_functions import series
taylor = series
__classement__[u"Analyse"].append((u"Taylor", "taylor", u"Développement limité. Ex: 'series(cos(x),x,0,5)'"))

from sympy import pi
__classement__[u"Symboles"].append((u"pi", "pi", u"Le nombre pi (3,14...)."))

from sympy import oo
__classement__[u"Symboles"].append((u"oo", "oo", u"L'infini positif."))

from sympy import E
e = E
__classement__[u"Symboles"].append((u"e", "e", u"Le nombre e = exp(1)."))

from sympy import I
i = I
__classement__[u"Symboles"].append((u"i", "i", u"Le nombre imaginaire i."))

##from custom_functions import pstfunc
##__classement__[u"LaTeX"].append((u"Fonction pst-plot", "pstfunc", u"Conversion d'une formule pst-plot en fonction."))


__classement__[u"Divers"].append(None)

from .custom_functions import pstfunc
__classement__[u"Divers"].append((u"Import d'une fonction \\psplot", "pstfunc", u'Pour utilisateurs de LaTeX. Ex: pstfunc("4 1 2.71818 0.039 x mul neg exp sub div")'))

__classement__[u"Divers"].append(None)

__classement__[u"Divers"].append((u"Aide", "aide", u"Fournit un complément d'aide sur certaines fonctions. Ex: aide(linreg)"))
help = aide


from .graphes import Graph
Graphe = Graph

#~ class Exp1_bis(sympy.core.numbers.Exp1):
    #~ def tostr(self, level=0):
        #~ return 'e'

#~ e = Exp1_bis()

#~ del Exp1_bis

#~ class ImaginaryUnit_bis(sympy.core.numbers.ImaginaryUnit):
    #~ def tostr(self, level=0):
        #~ return 'i'

#~ i = ImaginaryUnit_bis()

#~ del ImaginaryUnit_bis
