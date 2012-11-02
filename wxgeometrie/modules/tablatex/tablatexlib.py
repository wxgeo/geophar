# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------##
#              WxGeometrie               #
#                tabvar                  #
##--------------------------------------##
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

import functools, math
import numpy

from sympy import oo, nan

from ...mathlib import universal_functions as maths
from ...mathlib.parsers import traduire_formule, simplifier_ecriture, convertir_en_latex
from ...mathlib.custom_functions import nul
from ...pylib import advanced_split
from ...geolib.routines import nice_str


maths.oo = oo
maths.nan = nan
maths.num_oo = numpy.inf
maths.num_nan = numpy.nan
maths.pi = math.pi
maths.e = math.e


resoudre = functools.partial(nul, intervalle = False)
# resoudre = sympy.solve

#TODO: déplacer autant que possibles ces fonctions vers le parser de mathlib.

def traduire_latex(expression):
    return traduire_formule(expression, fonctions=maths.__dict__, OOo=False,
                                                                  LaTeX=True)



def test_parentheses(chaine):
    u"""Retourne True si le parenthésage est correct, False sinon.

    Note: il s'agit d'un test rapide (on ne tient pas compte des guillemets, crochets...)"""
    count = 0
    n = 0
    k = 0
    while count >= 0:
        k += 1
        i = chaine.find('(', n)
        j = chaine.find(')', n)
        if i == -1:
            n = j
        elif j == -1:
            n = i
        else:
            n = min(i, j)
        if n == -1:
            break
        parenthese = chaine[n]
        assert parenthese in '()'
        count += (1 if parenthese == '(' else -1)
        n += 1
    return not count




def _extraire_facteurs(chaine):
    # 1. On enlève les parenthèses superflues
    while chaine[0] == '(' and chaine[-1] == ')' and test_parentheses(chaine[1:-1]):
        chaine = chaine[1:-1]
    # Premier test rapide
    if '*' not in chaine and '/' not in chaine:
        return [chaine]

    # 2. On regarde s'il s'agit d'une somme/différence
    # On commence par enlever les '+' ou '-' en début de chaîne (-2x n'est pas une différence)
    _chaine = chaine.lstrip('+-')
    for symbole in ('+', '-'):
        if len(advanced_split(_chaine, symbole)) > 1:
            return [chaine]
            # c'est une somme/différence, pas de décomposition en facteurs

    # 3. On découpe autour des '*' (en tenant compte des parenthèses)
    facteurs = advanced_split(chaine, '*')
    if len(facteurs) == 1:
        facteurs = advanced_split(chaine, '/')
        if len(facteurs) == 1:
            # Ce n'est ni un produit ni un quotient
            return facteurs

    # 4. On redécoupe récursivement chacun des facteurs
    decomposition = []
    for facteur in facteurs:
        decomposition.extend(extraire_facteurs(facteur))
    return decomposition

def extraire_facteurs(chaine):
##    chaine = _ajouter_mult_manquants(chaine, fonctions = maths.__dict__)
    chaine = traduire_formule(chaine, fonctions = maths.__dict__).replace('**', '^')
    # Pour faciliter la décomposition en produit,
    # il est important que la puissance ne soit pas notée '**'.
    return [simplifier_ecriture(facteur) for facteur in _extraire_facteurs(chaine)]
