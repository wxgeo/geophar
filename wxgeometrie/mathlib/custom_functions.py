#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#           Mathlib 2 (sympy powered)         #
##--------------------------------------#######
#    WxGeometrie
#    Dynamic geometry, graph plotter, and more for french mathematic teachers.
#    Copyright (C) 2005-2010  Nicolas Pourcelot
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

## Cette librairie contient les fonctions de haut niveau non inclues dans sympy.

import math
from types import FunctionType

from sympy import (pi, E, Rational, Symbol, diff, log, floor,
                    sqrt, sympify, Float, nsimplify, Basic
                    )
from .custom_objects import Temps, Fonction, Decim
from .printers import custom_str
##from .. import param



#def deg(x):
#    u'Conversion radians -> degrés.'
#    return .MesureDegres(x)

def deg(x):
    u'Conversion radians -> degrés.'
    return x*180/pi

#def rad(x):
#    u'Conversion degrés -> radians.'
#    return x*sympy.pi/180

def jhms(s):
    u"Convertit un temps en secondes en jours-heures-minutes-secondes."
    return Temps(s = s)


def cbrt(x):
    u"Racine cubique de x."
    return cmp(x, 0)*math.exp(math.log(abs(x))/3)

def root(x, n):
    u"""Racine nième de x.

    N'est définie pour x négatif que si n est pair."""
    if n%2:
        return cmp(x, 0)*math.exp(math.log(abs(x))/n)
    return math.exp(math.log(x)/n)

def prod(facteurs):
    return reduce(lambda x,y:x*y, facteurs, 1)


def gcd(a, b):
    u"pgcd de a et de b"
    # algorithme d'Euclide
    a, b = max(abs(a),abs(b)), min(abs(a),abs(b))
    while b:
        a, b = b, a%b
    return a

def lcm(a, b):
    u"ppcm de a et de b"
    return a*b//gcd(a,b)

def pgcd(*termes):
    u"Le plus grand dénominateur commun à un nombre quelconque d'entiers."
    return reduce(lambda x,y:gcd(x,y), termes)


def ppcm(*termes):
    u"Le plus petit multiple commun à un nombre quelconque d'entiers."
    return reduce(lambda x,y:lcm(x,y), termes)



def n_premiers(n = 100, maximum = 50000): # securite face aux erreurs de frappe...!
    u"Donne la liste des n premiers nombres premiers."
    liste = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    m = liste[-1] + 2
    if n > maximum:
        raise OverflowError
    while len(liste) < n:
        r = math.sqrt(m)
        for k in liste:
            if k > r: # pas de diviseurs inferieurs à sa racine, donc le nombre est premier
                liste.append(m)
                break
            if not m%k:
                break
        m += 2
    return liste


# Approximation rationnelle par fractions continues
# cf. http://fr.wikipedia.org/wiki/Fraction_continue
def frac(valeur, n = 20, epsilon = 1e-15):
    u"Donne une fraction approximativement égale à la valeur."
    if isinstance(valeur, Rational):
        if isinstance(valeur, Decim):
            valeur = valeur.to_Rational()
    elif isinstance(valeur, Basic) and valeur.is_number \
            or isinstance(valeur, (float, int, long)):
        assert epsilon > 0
        p_ = 0
        p = 1
        q_ = 1
        q = 0
        x = valeur
        for i in xrange(n):
            a = int(x)
            p, p_ = a*p + p_, p
            q, q_ = a*q + q_, q
            delta = x - a
            if abs(delta) < epsilon or abs(valeur - p/q) < epsilon:
                return Rational(p, q)
            x = 1/delta
    elif isinstance(valeur, (list, tuple)):
        return expr.__class__(frac(item) for item in expr)
    elif isinstance(valeur, Basic):
        dico = {}
        for a in valeur.atoms():
            if isinstance(a, Decim):
                dico[a] = frac(a)
        return valeur.subs(dico)
    return valeur


def bin(n):
    u"Conversion en binaire."
    s = ""
    while n:
        s = str(n%2) + s
        n //= 2
    return s


def floats2rationals(expr):
    u"""Convertit tous les flottants d'une expression sympy en rationnels.

    Si l'expression est de type `list` ou `tuple`, la fonction est appelée
    récursivement.
    Sinon, si elle n'est pas de type sympy, l'expression est renvoyée telle
    qu'elle.
    """
    if isinstance(expr, (list, tuple)):
        return expr.__class__(floats2rationals(item) for item in expr)
    elif not isinstance(expr, Basic):
        return expr
    dico = {}
    for a in expr.atoms():
        if a.is_Float:
            dico[a] = nsimplify(a, rational=True)
    return expr.subs(dico)


def rationals2floats(expr, precision=None):
    u"""Convertit tous les rationnels d'une expression sympy en flottants.

    On peut spécifier via `precision` le nombre de chiffres significatifs.

    Si l'expression est de type `list` ou `tuple`, la fonction est appelée
    récursivement.
    Sinon, si elle n'est pas de type sympy, l'expression est renvoyée telle
    qu'elle.
    """
    if isinstance(expr, (list, tuple)):
        return expr.__class__(rationals2floats(item) for item in expr)
    elif not isinstance(expr, Basic):
        return expr
    dico = {}
    for a in expr.atoms():
        # Dans sympy, l'infini est un rationnel !
        if a.is_Rational and a.is_finite and not a.is_integer:
            dico[a] = Float(a, precision)
    return expr.subs(dico)

def _Pow2list(expression):
    u"""On décompose une puissance en liste de facteurs."""
    base, puissance = expression.as_base_exp()
    if puissance.is_integer:
        return int(puissance)*[base]
    elif base == E:
        coeff = puissance.as_coeff_mul()[0]
        if coeff.is_integer:
            return int(abs(coeff))*[base**(puissance/abs(coeff))]
    return [expression]

def _Mul2list(expression):
    u"""On décompose un produit en une liste de facteurs ; les puissances sont converties préalablement en produits."""
    liste = []
    if expression.is_Mul:
        for facteur in expression.args:
            liste += _Pow2list(facteur)
        return liste
    return _Pow2list(expression)


def auto_collect(expression):
    u"""Factorise une expression en utilisant sympy.collect, sans préciser manuellement ce par quoi factoriser."""
    if expression.is_Add:
        dico = {}
        liste0 = _Mul2list(expression.args[0])
        for elt in liste0:
            dico[elt] = liste0.count(elt)
        for terme in expression.args[1:]:
            liste = _Mul2list(terme)
            for elt in liste0:
                dico[elt] = min(dico[elt], liste.count(elt))
        produit = 1
        for key in dico:
            produit *= key**dico[key]
        return produit*sum(arg/produit for arg in expression.args)
    return expression


def derivee(f):
    if isinstance(f, FunctionType):
        x = Symbol('x')
        return Fonction(x, diff(f(x), x))
    return Fonction(f.variables[0], diff(f.expression, f.variables[0]))


def _convertir_frequences(frequences, serie):
    if frequences is None:
        n = len(serie)
        return n*[Rational(1, n)]
    else:
        total = sum(frequences)
        if total != 1:
            return [val/total for val in frequences]
        return frequences

def moyenne(serie, coeffs = None):
    u"Calcule l'espérance de la série des (xi, fi)."
    frequences = _convertir_frequences(coeffs, serie)
    return sum(xi*fi for xi, fi in zip(serie, frequences))

def variance(serie, coeffs = None):
    u"Calcule la variance de la serie des (xi, fi)"
    frequences = _convertir_frequences(coeffs, serie)
    M = moyenne(serie, frequences)
    return sum(fi*(xi - M)**2 for xi, fi in zip(serie, frequences))

def ecart_type(serie, coeffs = None):
    u"Retourne l'écart-type de la série des (xi, fi)."
    return sqrt(variance(serie, coeffs))

def covariance(serie1, serie2, coeffs = None):
    u"Retourne la covariance des deux séries."
    assert len(serie1) == len(serie2), u"Les deux séries doivent avoir le même nombre de valeurs."
    frequences = _convertir_frequences(coeffs, serie1)
    x_ = moyenne(serie1, frequences)
    y_ = moyenne(serie2, frequences)
    return sum(fi*(xi - x_)*(yi - y_) for xi, yi, fi in zip(serie1, serie2, frequences))

def linreg(serie1, serie2, coeffs = None):
    u"""Droite de régression par la méthode des moindres carrés.

    Retourne les coefficients a et b de l'équation y=ax+b
     de la droite de régression par la méthode des moindres carrés.

     >>> from wxgeometrie.mathlib.custom_functions import linreg
     >>> linreg((85.6,84.5,81,80.2,72.8,71.2,73,48.1),(78.7,77.6,75.2,71.1,67.7,66.3,59.1,46.8))
     (0.849191825268073, 4.50524942626518)
     """
    a = covariance(serie1, serie2)/variance(serie1)
    b = moyenne(serie2) - a*moyenne(serie1)
    return a, b


def pstfunc(chaine):
    u"Convertit une chaine représentant une fonction pst-trick en une fonction "
    args = []
    dict_op = {'mul':'*','add':'+','exp':'**','div':'/','sub':'-'}
    dict_fn = {'ln':'ln'}

    def code_arg(s):
        return '(' + str(sympify(s)) + ')'

    for s in chaine.split(' '):
        if s in dict_op:
            assert len(args) >= 2, 'Il faut deux arguments pour ' + s
            args[-2] = code_arg(dict_op[s].join(args[-2:]))
            args.pop()
        elif s in dict_fn:
            args[-1] = code_arg(dict_fn[s] + '(' + args[-1] + ')')
        elif s:
            args.append(code_arg(s))
    assert len(args) == 1, 'Il doit rester un seul argument a la fin.'
    return custom_str(sympify(args[0]))

def aide(fonction):
    u"Retourne (si possible) de l'aide sur la fonction saisie."
    if getattr(fonction, '__name__', None) and getattr(fonction, '__doc__', None):
        hlp = "\n== Aide sur %s ==" %fonction.__name__
        for ligne in fonction.__doc__.split('\n'):
            hlp += '\n' + ligne.lstrip()
        return hlp
    else:
        from end_user_functions import __classement__
        for val in __classement__.itervalues():
            if val[1] == getattr(fonction, '__name__', str(fonction)):
                hlp = "\n== Aide sur %s ==\n" %fonction.__name__
                hlp += val[2]
                return hlp
        return "Pas d'aide disponible."

def arrondir(valeur, chiffres = 0):
    # Nombre de chiffres de la partie entière :
    n = floor(log(valeur, 10)) + 1
    return sympify(valeur).evalf(chiffres + n)
