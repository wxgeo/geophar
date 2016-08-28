# -*- coding: utf-8 -*-

##--------------------------------------#######
#   Mathlib 2 (sympy powered) #
##--------------------------------------#######
#WxGeometrie
#Dynamic geometry, graph plotter, and more for french mathematic teachers.
#Copyright (C) 2005-2013  Nicolas Pourcelot
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
    ("Algèbre", []),
    ("Analyse", []),
    ("Symboles", []),
    ("Arithmétique", []),
    ("Statistiques", []),
    ("Matrices", []),
    ("Divers", []),
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

from .custom_functions import derivee, moyenne, variance, ecart_type, \
                               covariance, linreg, aide, normal, binomial, \
                               inv_normal, fluctu, confiance


__classement__["Statistiques"].append(("Moyenne", "moyenne", "Moyenne de la série, éventuellement coefficientée."
                                     " Ex: moyenne((12; 13; 15); (1; 1; 2))"))
__classement__["Statistiques"].append(("Variance", "variance", "Variance de la série, éventuellement coefficientée."
                                     " Ex: variance((12; 13; 15); (1; 1; 2))"))
__classement__["Statistiques"].append(("Écart-type", "ecart_type",
                        "Écart-type de la série, éventuellement coefficientée."
                                     " Ex: ecart_type((12; 13; 15); (1; 1; 2))"))
__classement__["Statistiques"].append(("Covariance", "covariance", "Covariance de deux séries."
                                     " Ex: covariance((1;2;3);(2;5;7))"))
__classement__["Statistiques"].append(("Droite de régression", "linreg",
                "Retourne (a, b) pour une droite d'ajustement d'équation y=ax+b"
                                     " (moindres carrés). Ex: linreg((1;2;3);(2;5;7))"))
__classement__["Statistiques"].append(("Loi normale", "normal",
                "Usage: normal(a, b, mu, sigma). Retourne P(a \u2264 X \u2264 b), où "
                "X suit une loi normale d'espérance mu et de variance sigma²."))
__classement__["Statistiques"].append(("Loi binomiale", "binomial",
                "Usage: normal(a, b, n, p). Retourne P(a \u2264 X \u2264 b), où "
                "X suit une loi binomiale de paramètres n et p."))
__classement__["Statistiques"].append(("Inverser la loi normale", "inv_normal",
                "Usage: inv_normal(p). Retourne a tel que P(X \u2264 a)=p, où "
                "X suit une loi normale centrée réduite."))
__classement__["Statistiques"].append(("Intervalle de fluctuation", "fluctu",
                "Usage: fluctu(p, n, seuil). Retourne l'intervalle de fluctuation "
                "pour un échantillon de taille n, et une proportion p."))
__classement__["Statistiques"].append(("Intervalle de confiance", "confiance",
                "Usage: estim95(f, n). Retourne l'intervalle de confiance "
                "pour un échantillon de taille n, et une fréquence f."))

from .sympy_functions import expand
developper = developpe = expand
__classement__["Algèbre"].append(("Développe", "developpe", "Développer une expression."))

from .sympy_functions import factor
factoriser = factorise = factor
__classement__["Algèbre"].append(("Factorise", "factorise", "Factoriser une expression."))

from .custom_functions import canonique
__classement__["Algèbre"].append(("Forme canonique", "canonique", "Mettre sous forme canonique un polynôme de degré 2."))

from .custom_functions import discriminant
__classement__["Algèbre"].append(("Discriminant", "discriminant", "Calcule le discriminant d'un polynôme de degré 2."))

from .sympy_functions import together
rassembler = rassemble = together
__classement__["Algèbre"].append(("Une seule fraction", "rassemble", "Mettre sur le même dénominateur."))


from .sympy_functions import evalf
evaluer = evalue = evalf
__classement__["Algèbre"].append(("Évalue", "evalue", "Calculer une valeur approchée."))

from .solvers import resoudre
solve = resous = resoudre
__classement__["Algèbre"].append(("Résous", "resous", "Résoudre une (in)équation ou un système. ex: resous(2x-3>0 et 3x+1<=0)"))

__classement__["Algèbre"].append(None)

#~ from .sympy_functions import cfactor
#~ cfactoriser = cfactorise = cfactor
#~ __classement__[u"Algèbre"].append((u"Factorise dans C", "cfactorise", u"Factoriser une expression dans le corps des complexes."))

from sympy import conjugate
conjug = conjugue = conjuguer = conjugate
__classement__["Algèbre"].append(("Conjuguer", "conjug", "Calculer le conjugué d'un nombre complexe."))

__classement__["Algèbre"].append(None)

from .sympy_functions import sum
somme = sum
__classement__["Algèbre"].append(("Somme", "somme", "Calculer une somme."))

from .sympy_functions import product
produit = product
__classement__["Algèbre"].append(("Produit", "produit", "Calculer un produit."))

__classement__["Algèbre"].append(None)

from .sympy_functions import mat, transpose, det, vecteurs_propres, valeurs_propres
Matrice = Matrix = Mat = matrix = matrice = mat
vep = vecteurs_propres
vap = valeurs_propres
determinant = det
tr = transposee = transpose
__classement__["Matrices"].append(("Matrice", "mat", "Créer une matrice. ex: mat([[1;2];[3;4]]); mat(4;4;0); mat(4;4;2*li+3*co)"))
__classement__["Matrices"].append(("Transpose", "tr", "Transpose une matrice. ex: tr(M)"))
__classement__["Matrices"].append(("Déterminant", "det", "Calcul le déterminant d'une matrice. ex: det(M)"))
__classement__["Matrices"].append(("Valeurs propres", "vap", "Valeurs propres d'une matrice avec ordre de multiplicité. ex: vap(M)"))
__classement__["Matrices"].append(("Vecteurs propres", "vep", "Base de vecteurs propres d'une matrice. ex: vep(M)"))


from sympy import isprime
premier = isprime
__classement__["Arithmétique"].append(("Premier ?", "premier", "Tester si un nombre est premier."))

from .sympy_functions import divisors
diviseurs = divisors
__classement__["Arithmétique"].append(("Diviseurs", "diviseurs", "Chercher les diviseurs d'un nombre."))

# Alias
facteurs = factors = factor
__classement__["Arithmétique"].append(("Facteurs premiers", "facteurs", "Décomposer un nombre en facteurs premiers."))

from .custom_functions import pgcd
gcd = pgcd
__classement__["Arithmétique"].append(("PGCD", "pgcd", "Calculer le PGCD de plusieurs entiers."))

from .custom_functions import ppcm
lcm = ppcm
__classement__["Arithmétique"].append(("PPCM", "ppcm", "Calculer le PPCM de plusieurs entiers."))

__classement__["Arithmétique"].append(None)

from .custom_functions import jhms
hms = jhms
__classement__["Divers"].append(("Conversion j-h-min-s", "jhms", "Convertir un temps en secondes en jours, heures, minutes et secondes."))

from .custom_functions import deg
__classement__["Divers"].append(("Conversion en degrés", "deg", "Convertir un angle de radians en degrés. (Ex: deg(pi/3), ou pi/3>>deg)."))

from .custom_functions import frac
__classement__["Divers"].append(("Convertir en fraction", "frac", "Convertir un nombre décimal en fraction."))

ent = floor
__classement__["Divers"].append(("Partie entière", "ent", "Partie entière d'un nombre (ex: -2,4 -> -3)."))

from .custom_functions import arrondir
round = arrondi = arrondis = arrondir
__classement__["Divers"].append(("Arrondi", "arrondi", "Arrondit à n chiffres après la virgule-3)."))


from sympy import factorial
factoriel = factorial
__classement__["Arithmétique"].append(("Factoriel", "factoriel", "factoriel(n) vaut 1*2*3*4*5*...*n."))

from sympy import ff
arrangements = nAr = nA = ff
__classement__["Arithmétique"].append(("Arrangements", "nAr", "Nombre d'arrangements."))

from sympy import binomial as binome
combinaisons = combi = nCr = nC = binome
__classement__["Arithmétique"].append(("Combinaisons", "nCr", "Nombre de combinaisons."))

from .sympy_functions import limit
lim = limite = limit
__classement__["Analyse"].append(("Limite", "limite", "Calculer une limite. Ex: 'limite(1/x; x; 0+)', 'limite(x^2; x; -oo)'"))

from .sympy_functions import diff
derive = diff
__classement__["Analyse"].append(("Dérive", "derive", "Dériver une expression. Ex: 'derive(2x+7; x)' et 'derive(2x+7; x; 2)' (dérivée seconde)"))

from .sympy_functions import integrate
integrale = integral = integre = integrate
__classement__["Analyse"].append(("Intègre", "integre", "Intégrer une expression. Ex: 'integre(x+1; x)' et 'integre(x+1; (x; -1; 1))"))

from .sympy_functions import series
taylor = series
__classement__["Analyse"].append(("Taylor", "taylor", "Développement limité. Ex: 'taylor(cos(x); x; 0; 5)'"))

from sympy import pi
__classement__["Symboles"].append(("pi", "pi", "Le nombre pi (3,14...)."))

from sympy import oo
__classement__["Symboles"].append(("oo", "oo", "L'infini positif."))

from sympy import E
e = E
__classement__["Symboles"].append(("e", "e", "Le nombre e = exp(1)."))

from sympy import I
i = I
__classement__["Symboles"].append(("i", "i", "Le nombre imaginaire i."))

##from custom_functions import pstfunc
##__classement__[u"LaTeX"].append((u"Fonction pst-plot", "pstfunc", u"Conversion d'une formule pst-plot en fonction."))


__classement__["Divers"].append(None)

from .custom_functions import pstfunc
__classement__["Divers"].append(("Import d'une fonction \\psplot", "pstfunc", 'Pour utilisateurs de LaTeX. Ex: pstfunc("4 1 2.71818 0.039 x mul neg exp sub div")'))

__classement__["Divers"].append(None)

__classement__["Divers"].append(("Aide", "aide", "Fournit un complément d'aide sur certaines fonctions. Ex: aide(linreg)"))
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
