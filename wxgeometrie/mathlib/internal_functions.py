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

## Cette librairie contient des fonctions mathématiques à usage interne

from numpy import roots as nroots

from sympy import Mul, Float, Basic, Poly, together, expand, powsimp, roots,\
                    sympify, div, Symbol
from ..pylib import warning
from .. import param


def _simplify(expr):
    u"""Simplifie une expression.

    Alias de simplify (sympy 0.6.4).
    Mais simplify n'est pas garanti d'être stable dans le temps.
    (Cf. simplify.__doc__)."""
    return together(expand(Poly.cancel(powsimp(expr))))
#TODO: Mettre à jour simplify

def _is_num(val):
    return isinstance(val, (float, Float))

def poly_factor(polynome, variable, corps = None, approchee = None):
    u"""Factorise un polynome à une variable.

    Le corps peut être R ou C.
    Par défaut, le corps de factorisation est celui des coefficients."""
    from .sympy_functions import simplifier_racines
    if approchee is None:
        # Paramètre utilisé en interne par 'l'interpreteur' de commandes
        # (cf. méth. evaluer() de la classe Interprete(), dans custom_objects.py)
        approchee = getattr(param, 'calcul_approche', False)

    if polynome.is_Mul:
        return reduce(lambda x,y:x*y, [poly_factor(fact, variable, corps = corps) for fact in polynome.args], 1)
    sym_poly = polynome.as_poly(variable)
    coeffs = sym_poly.all_coeffs()

    if any(_is_num(coeff) for coeff in coeffs):
        approchee = True
        racines_brutes = {}.fromkeys(nroots(coeffs),  1)
    else:
        if corps == "R":
            if not all(coeff.is_real for coeff in coeffs):
                raise ValueError, "factorisation dans 'R' impossible."
        elif corps is None:
            if all(coeff.is_real for coeff in coeffs):
                corps = "R"
            else:
                corps = "C"
        racines_brutes = roots(polynome, variable, cubics=True, quartics=True)
    racines = list((simplifier_racines(racine), mult) for racine, mult in racines_brutes.iteritems())

    if approchee:
        nbr_racines = sum(multiplicite for racine, multiplicite in racines)
        if nbr_racines < sym_poly.degree():
            # On cherche une approximation des racines manquantes
            sol_approchees = list(nroots(coeffs))
            # On associe à chaque racine l'approximation qui lui correspond
            for racine, multiplicite in racines:
                distances = [(sol, abs(complex(racine) - sol)) for sol in sol_approchees]
                distances.sort(key = lambda x:x[1])
                for i in range(multiplicite):
                    distances.pop(0)
                # Les racines approchées qui restent ne correspondent à aucune racine exacte
                sol_approchees = [sol for sol, distance in distances]
            racines.extend((sympify(sol), sol_approchees.count(sol)) for sol in set(sol_approchees))

    coefficient = coeffs[0]
    produit = 1
    if corps == "R":
        racines_en_stock = []
        multiplicites_en_stock = []
        for racine, multiplicite in racines:
            if not isinstance(racine, Basic):
                racine = sympify(racine)
            reel = racine.is_real
            if not reel:
                # is_real n'est pas fiable (26/11/2009)
                # cf. ((54*6**(1/3)*93**(1/2) - 162*I*6**(1/3)*31**(1/2) - 522*6**(1/3) + 6*6**(2/3)*(-522 + 54*93**(1/2))**(1/3) + 522*I*3**(1/2)*6**(1/3) + 6*I*3**(1/2)*6**(2/3)*(-522 + 54*93**(1/2))**(1/3) - 24*(-522 + 54*93**(1/2))**(2/3))/(36*(-522 + 54*93**(1/2))**(2/3))).is_real
                re, im = racine.expand(complex=True).as_real_imag()
                reel = im.is_zero or im.evalf(80).epsilon_eq(0,'10e-80')
                if reel:
                    racine = re
                # Approximation utile (?) pour la factorisation de certains polynômes de degrés 3 et 4
                # De toute manière, une vérification de la factorisation par division euclidienne
                # a lieu à la fin de l'algorithme.
            if reel:
                produit *= (variable - racine)**multiplicite
            else:
                conjuguee = racine.conjugate()
                if conjuguee in racines_en_stock:
                    produit *= (variable**2 - 2*re*variable + re**2 + im**2)**multiplicite
                    i = racines_en_stock.index(conjuguee)
                    racines_en_stock.pop(i)
                    multiplicites_en_stock.pop(i)
                else:
                    racines_en_stock.append(racine)
                    multiplicites_en_stock.append(multiplicite)
        if racines_en_stock:
            # Il reste des racines qu'on n'a pas réussi à appareiller.
            P = 1
            for racine, multiplicite in zip(racines_en_stock, multiplicites_en_stock):
                P *= (variable - racine)**multiplicite
            produit *= P.expand()
    else:
        for racine, multiplicite in racines:
            produit *= (variable - racine)**multiplicite
#    print produit
    quotient, reste = div(polynome, coefficient*produit, variable)
    if reste != 0 and not approchee:
        raise NotImplementedError
    poly_factorise = coefficient*produit*quotient
    if isinstance(poly_factorise, Mul) and poly_factorise.args[0] == 1.:
        poly_factorise = Mul(*poly_factorise.args[1:])
        # sinon, poly_factor(x**2+2.5*x+1,x) donne 1.0*(x + 0.5)*(x + 2.0)
    return poly_factorise

def syms(expression):
    u"""Retourne la liste des symboles utilisés par l'expression."""
    return tuple(expression.atoms(Symbol))

def extract_var(expression):
    u"""Retourne la variable de l'expression (renvoie un avertissement s'il y en a plusieurs, et 'x' par défaut s'il n'y en a pas)."""
    if hasattr(expression, "atoms"):
        symboles = expression.atoms(Symbol)
        if len(symboles) == 0:
            return Symbol("x")
        else:
            if len(symboles) > 1 and param.debug:
                warning("l'expression possede plusieurs variables.")
            return expression.atoms(Symbol).pop()
    else:
        return Symbol("x")

def count_syms(expression, symbole):
    u"""Compte le nombre d'occurence de la variable dans l'expression."""
    if expression.has(symbole):
        if expression.is_Atom:
            return 1
        else:
            return sum(count_syms(arg, symbole) for arg in expression.args)
    else:
        return 0
