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

# version unicode

## Cette librairie est une interface pour sympy :
## Elle modifie si nécessaire le comportement de fonctions sympy.

import types

import sympy, numpy

import custom_objects
import internal_functions
import custom_functions
import param

def expand(expression, variable = None):
    expression = sympy.expand(expression)
    if isinstance(expression, sympy.Basic) and expression.is_rational_function():
        if variable is None:
           variable = internal_functions.extract_var(expression)
        return sympy.apart(expression, variable)
    return expression


def evalf(expression, precision = 60):
    u"""Evalue l'expression en respectant sa structure.

    Par exemple, un polynôme factorisé reste factorisé après évaluation.
    """
    if not isinstance(expression, sympy.Basic):
        if hasattr(expression, 'evalf'):
            return expression.evalf(precision)
        elif hasattr(expression, '__float__'):
            return float(expression)
        return expression
    elif expression.is_Atom or isinstance(expression, sympy.Function):
        return expression.evalf(precision)
    else:
        return expression.func(*(evalf(arg) for arg in expression.args))


def factor(expression, variable = None, ensemble = None, decomposer_entiers = True):
    if isinstance(expression, (int, long, sympy.Integer)):
        if decomposer_entiers:
            return custom_objects.ProduitEntiers(*sympy.factorint(expression).iteritems())
        else:
            return expression


    elif isinstance(expression, sympy.Basic) and expression.is_polynomial():
        if variable is None:
            variable = internal_functions.extract_var(expression)
        if variable is None:
            # polynôme à plusieurs variables
            return sympy.factor(expression)
        else:
            try:
                return internal_functions.poly_factor(expression, variable, ensemble)
            except NotImplementedError:
                print_error()
                return expression
    resultat = sympy.together(expression)
    if resultat.is_rational_function():
        num, den = resultat.as_numer_denom()
        if den != 1:
            return factor(num, variable, ensemble, decomposer_entiers)/factor(den, variable, ensemble, decomposer_entiers)
    else:
        resultat = custom_functions.auto_collect(resultat)
        if resultat.is_Mul:
            produit = 1
            for facteur in resultat.args:
                produit *= factor(facteur, variable, ensemble, decomposer_entiers)
            return produit
        return resultat


def cfactor(expression, variable = None):
    return factor(expression, variable, ensemble = "C")


def series(expression, variable = None, point = 0, ordre = 5):
    if variable is None:
        if internal_functions.syms(expression):
            variable = internal_functions.syms(expression)[0]
        else:
            variable = sympy.Symbol("x")
    return getattr(expression, "series")(variable, point, ordre)


def diff(expression, variable = None, n = 1):
    if isinstance(expression, custom_objects.Fonction):
        return custom_functions.derivee(expression)
    if variable is None and hasattr(expression, "atoms") and len(expression.atoms(sympy.Symbol)) == 1:
        variable = expression.atoms(sympy.Symbol).pop()
    return sympy.diff(expression, variable, n)


def divisors(n):
    return sympy.divisors(int(n))


def limit(expression, *args):
    args = list(args)
    if args[-1] == "-" or args[-1] == "+":
        dir = args.pop()
    else:
        dir = None
    if len(args) == 1 and len(expression.atoms(sympy.Symbol)) == 1:
        args = [expression.atoms(sympy.Symbol).pop()] + args
    if dir is None:
        limite_gauche = sympy.limit(expression, args[0], args[1], "-")
        limite_droite = sympy.limit(expression, args[0], args[1], "+")
        if limite_gauche == limite_droite:
            return limite_gauche
        return limite_gauche, limite_droite
    else:
        return  sympy.limit(expression, args[0], args[1], dir)

def integrate(expression, *args):
    if len(args) == 3 and isinstance(args[0], sympy.Symbol) \
                               and not isinstance(args[1], sympy.Symbol) \
                               and isinstance(args[1], sympy.Basic) \
                               and not isinstance(args[2], sympy.Symbol) \
                               and isinstance(args[2], sympy.Basic):
        return sympy.integrate(expression, (args[0], args[1], args[2]))
    elif len(args) == 2 and len(internal_functions.syms(expression)) <= 1 \
                               and not isinstance(args[0], sympy.Symbol) \
                               and isinstance(args[0], sympy.Basic) \
                               and not isinstance(args[1], sympy.Symbol) \
                               and isinstance(args[1], sympy.Basic):
        if internal_functions.syms(expression):
            return sympy.integrate(expression, (internal_functions.syms(expression)[0], args[0], args[1]))
        else:
            return sympy.integrate(expression, (sympy.Symbol("x"), args[0], args[1]))
    return sympy.integrate(expression, *args)

def sum(expression, *args):
    if len(args) == 3 and isinstance(args[0], sympy.Symbol) \
                               and not isinstance(args[1], sympy.Symbol) \
                               and isinstance(args[1], sympy.Basic) \
                               and not isinstance(args[2], sympy.Symbol) \
                               and isinstance(args[2], sympy.Basic):
        return sympy.sum(expression, (args[0], args[1], args[2]))
    elif len(args) == 2 and len(internal_functions.syms(expression)) <= 1 \
                               and not isinstance(args[0], sympy.Symbol) \
                               and isinstance(args[0], sympy.Basic) \
                               and not isinstance(args[1], sympy.Symbol) \
                               and isinstance(args[1], sympy.Basic):
        if internal_functions.syms(expression):
            return sympy.sum(expression, (internal_functions.syms(expression)[0], args[0], args[1]))
        else:
            return sympy.sum(expression, (sympy.Symbol("x"), args[0], args[1]))
    return sympy.sum(expression, *args)

def product(expression, *args):
    if len(args) == 3 and isinstance(args[0], sympy.Symbol) \
                               and not isinstance(args[1], sympy.Symbol) \
                               and isinstance(args[1], sympy.Basic) \
                               and not isinstance(args[2], sympy.Symbol) \
                               and isinstance(args[2], sympy.Basic):
        return sympy.product(expression, (args[0], args[1], args[2]))
    elif len(args) == 2 and len(internal_functions.syms(expression)) <= 1 \
                               and not isinstance(args[0], sympy.Symbol) \
                               and isinstance(args[0], sympy.Basic) \
                               and not isinstance(args[1], sympy.Symbol) \
                               and isinstance(args[1], sympy.Basic):
        if internal_functions.syms(expression):
            return sympy.product(expression, (internal_functions.syms(expression)[0], args[0], args[1]))
        else:
            return sympy.product(expression, (sympy.Symbol("x"), args[0], args[1]))
    return sympy.product(expression, *args)

def solve(expression, *variables, **kw):
    ensemble = kw.get("ensemble", "R")
    if not variables:
        variables = internal_functions.syms(expression)
    if len(variables) == 1:
        solutions = sympy.solve(expression, variables[0])
        if ensemble == "R":
            return tuple(solution for solution in solutions if solution.is_real)
        elif ensemble == "Q":
            return tuple(solution for solution in solutions if solution.is_rational)
        elif ensemble == "N":
            return tuple(solution for solution in solutions if solution.is_integer)
        else:
            return solutions
    else:
        return sympy.solve(expression, variables)

def csolve(expression, *variables):
    return solve(expression, *variables, **{ensemble: "C"})

def qsolve(expression, *variables):
    return solve(expression, *variables, **{ensemble: "Q"})

def nsolve(expression, *variables):
    return solve(expression, *variables, **{ensemble: "N"})

def simplifier_racines(expression):
    try:
        if getattr(expression, "is_Pow", False):
            return sympy.sqrtdenest(expression)
        elif getattr(expression, "is_Mul", False):
            return reduce(lambda x,y:x*y, [simplifier_racines(fact) for fact in expression.args], 1)
        elif getattr(expression, "is_Add", False):
            return reduce(lambda x,y:x+y, [simplifier_racines(term) for term in expression.args], 0)
        return expression
    except TypeError:
        if param.debug:
            print "Warning: error occured during expression denesting:", expression
        return expression

def mat(*args):
    if len(args) >= 2:
        args = list(args)
        args[0] = int(args[0])
        args[1] = int(args[1])
        if len(args) == 2:
            args.append(lambda i,j:i==j,)
        elif not isinstance(args[2], types.FunctionType):
            if isinstance(args[2], sympy.Basic):
                li = sympy.Symbol("li")
                co = sympy.Symbol("co")
                args = [[args[2].subs({co: j+1, li: i+1}) for j in xrange(args[1])] for i in xrange(args[0])]
            else:
                args[2] = lambda i, j, val = args[2]: val
#    print args, [type(arg) for arg in args], args[2](1, 1), type(args[2](1, 1))
    return custom_objects.Matrice(*args)

def together(expression):
    return sympy.cancel(sympy.together(expression))
