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

import re, functools, math
import numpy

from sympy import oo, nan

from ...mathlib import universal_functions as maths
from ...mathlib.parsers import traduire_formule, simplifier_ecriture
from ...mathlib.custom_functions import nul
from ...pylib import find_closing_bracket, advanced_split
from ... import param


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
    return traduire_formule(  expression,
                                            fonctions = maths.__dict__,
##                                            variables = '[_A-Za-z][_A-Za-z0-9]*',
                                            OOo = False,
                                            LaTeX = True,
                                            changer_separateurs = True,
                                            separateurs_personnels = (',', ';'))





def convertir_en_latex(chaine):
    u"Convertit une chaine représentant un calcul en code LaTeX."
    #TODO: problème avec les puissances qui contiennent des fractions
    #TODO: incorporer cette fonction à mathlib, et mettre en place des tests unitaires
    #TODO: c'est assez lent, à optimiser ?
    # (environ 0.5ms en conditions réelles, avec 10 à 20 appels par tableau).
##    time0 = time.time()
    chaine = chaine.replace("**", "^")
    chaine = re.sub(r'[ ]+', ' ', chaine)
    # inutile en LaTeX, mais ça peut simplifier certaines expressions regulieres
    chaine = re.sub(r'[ ]?/[ ]?', '/', chaine)
    chaine = re.sub(r'[ ]?\^[ ]?', '^', chaine)

    fonctions = ('cos', 'sin', 'tan', 'ln', 'log', 'exp', 'sqrt', '^')

    # On traite maintenant le (délicat) cas des fractions,
    # ie. 2/3, mais aussi (pi+3)/(5-e), ou cos(2)/3
    securite = 1000
    while "/" in chaine:
        securite -= 1
        if securite < 0:
            raise RuntimeError, "Boucle probablement infinie."
        i = chaine.find("/")

        # analyse des caractères précédents, pour localiser le numérateur
        k = i
        parentheses = 0
        # indices correspondants au début et à la fin du numérateur
        debut_numerateur = fin_numerateur = None
        #  exposant éventuel du numérateur
        puissance = ''

        while k > 0:
            k -= 1
            if chaine[k].isalnum():
                if fin_numerateur is None:
                    fin_numerateur = k
            elif chaine[k] == ")":
                if parentheses == 0:
                    fin_numerateur = k
                parentheses += 1
            elif chaine[k] == "(":
                parentheses -= 1
                if parentheses == 0:
                    debut_numerateur = k
                    break
            elif chaine[k] == '^':
                puissance = chaine[k:fin_numerateur + 1]
            elif parentheses == 0 and fin_numerateur is not None:
                debut_numerateur = k+1
                break
        if debut_numerateur is None:
            debut_numerateur = 0
        assert fin_numerateur is not None, "Numerateur introuvable"

        # On détecte la fonction qui précède éventuellement la parenthèse
        # par exemple, sqrt(2)/2 -> le numérateur est 'sqrt(2)', et pas '(2)'
        # TODO: réécrire tout ça plus proprement
        for func in fonctions:
            n = len(func)
            if chaine[:debut_numerateur].endswith(func) and\
                    (debut_numerateur == n or not chaine[debut_numerateur-n-1].isalpha()):
                debut_numerateur -= n

        numerateur = chaine[debut_numerateur : fin_numerateur+1].strip()
        if numerateur[0] == "(":
            if puissance:
                numerateur += puissance
            else:
                numerateur = numerateur[1:-1]


        # analyse des caractères suivants, pour localiser le dénominateur
        k = i
        parentheses = 0
        # indices correspondants au début et à la fin du numérateur
        debut_denominateur = fin_denominateur = None
        # exposant éventuel du dénominateur
        puissance = ''

        while k < len(chaine) - 1:
            k += 1
            if chaine[k].isalnum():
                if debut_denominateur is None:
                    debut_denominateur = k
            elif chaine[k] == "(":
                if parentheses == 0:
                    debut_denominateur = k
                parentheses += 1
            elif chaine[k] == ")":
                parentheses -= 1
                if parentheses == 0:
                    fin_denominateur = k
                    break
            elif parentheses == 0 and debut_denominateur is not None:
                fin_denominateur = k-1
                break
        if fin_denominateur is None:
           fin_denominateur = len(chaine)  - 1

        assert debut_denominateur is not None, "Denominateur introuvable"

        denominateur = chaine[i + 1:fin_denominateur + 1].strip()
        if chaine[fin_denominateur+1:].startswith('^'):
            m = re.match('[(][A-Za-z0-9.]+[)]|[A-Za-z0-9.]+', chaine[fin_denominateur + 2:])
            if m is not None:
                puissance = '^' + m.group()
                fin_denominateur += m.end() + 1
        if denominateur[0] == "(":
            if puissance:
                denominateur += puissance
            else:
                denominateur = denominateur[1:-1]

        if len(chaine) >= 10000:
            if param.verbose:
                print "Code en cours :"
                print chaine
            raise RuntimeError, 'Memory Leak probable.'
        # remplacement de la fraction python par une fraction LaTeX
        chaine = chaine[:debut_numerateur] + r"\frac{" + numerateur + "}{" + denominateur + "}" + chaine[fin_denominateur+1:]

    assert securite >= 0

    # Autres remplacements :
    chaine = re.sub(r"(?<!\w|\\)(pi|oo|e|sin|cos|tan|ln|log|exp|sqrt)(?!\w)", lambda m:"\\" + m.group(), chaine)
    for func in fonctions:
        i = 0
        while True:
            i = chaine.find(func + '(', i)
            if i == -1:
                break
            i += len(func) + 1
            j = find_closing_bracket(chaine, start = i , brackets = '()')
            chaine = chaine[:i-1] + '{' + chaine[i:j] + '}' + chaine[j+1:]

    chaine = chaine.replace("*", " ")

    # Puissances : 2^27 -> 2^{27}
    #chaine = re.sub(r'\^\([-0-9.]+\)', lambda m: '^{' + m.group()[2:-1] + '}', chaine)
    chaine = re.sub(r'\^-?[0-9.]+', lambda m: '^{' + m.group()[1:] + '}', chaine)


##    if param.debug:
##        print 'Temps pour conversion LaTeX:', time.time()- time0
    return "$" + chaine + "$"





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
