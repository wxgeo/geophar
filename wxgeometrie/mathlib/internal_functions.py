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

## Cette librairie contient des fonctions mathématiques à usage interne

import math
import cmath
import pylab
import sympy
from pylib import *
import sympy_functions
import universal_functions

## Fonctions rapides destinées essentiellement à géolib

##def produit_scalaire(u, v):
##    u"""Calcule le produit scalaire des vecteurs u et v.
##    u et v doivent être de type list, tuple, array, ou geolib.Vecteur."""
##    return sum(i*j for i, j in zip(u ,v))
##
##
##
###def angle_vectoriel(u, v):
###    u"""Renvoie une mesure sur ]-pi;pi] de l'angle formé par les vecteurs u et v.
###    u et v doivent être de type list, tuple, array, ou geolib.Vecteur, et de dimension 2."""
###    return cmath.log(complex(*v)/complex(*u)).imag
##
##def angle_vectoriel(u, v):
##    u"""Renvoie une mesure sur ]-pi;pi] de l'angle formé par les vecteurs u et v.
##    u et v doivent être de type list, tuple, array, ou geolib.Vecteur, et de dimension 2.
##
##    Version compatible avec sympy."""
##    return universal_functions.arg((v[0] + v[1]*1j)/(u[0] + u[1]*1j))
##
###~ def _angle_vectoriel_bis_(u, v):
##    #~ u"Autre implémentation du produit vectoriel (un peu plus lente)."
##    #~ return (cmp(u[0]*v[1]-v[0]*u[1], 0) or 1)*math.acos(produit_scalaire(u, v)/(math.hypot(*u)*math.hypot(*v)))
##
##
##def norme(x, y):
##    u"Implémentation rapide de la norme d'un vecteur."
##    if isinstance(x, (int, float, long)) or isinstance(y, (int, float, long)):
##        return math.hypot(x, y)
##    return universal_functions.sqrt(x**2 + y**2)
##
##
##
##def distance(A, B):
##    u"Distance entre les points A et B."
##    xA, yA = A
##    xB,  yB = B
##    return norme(xA - xB, yA - yB)
##
##def carre_distance(A, B):
##    u"Carré de la distance entre les points A et B."
##    xA, yA = A
##    xB, yB = B
##    return (xB - xA)**2+(yB - yA)**2
##
##def vect(A, B):
##    u"Coordonnées du vecteur A>B."
##    xA, yA = A
##    xB, yB = B
##    return xB - xA, yB - yA
##
##
#### Fonctions de formatage (pour l'affichage entre autres)
##
###~ def old_nchiffres(x, n = 1):
##    #~ u"Arrondi x en fournissant n chiffres significatifs. Ex: nchiffres(2345, 2)."
##
##    #~ return x and round(x/10**floor(log10(abs(x))-n+1))*10**floor(log10(abs(x))-n+1) # Attention au cas x = 0 !
##
##def nchiffres(x, n = 1):
##    u"Arrondi x en fournissant n chiffres significatifs. Ex: nchiffres(2345, 2)."
##    if x:
##        k = 10**math.floor(math.log10(abs(x))-n+1)
##        return round(x/k)*k
##    return x # Attention au cas x = 0 !
##
##def nice_display(x):
##    if isinstance(x, float):
##        x = round(x, param.decimales_affichees)
##        if abs(x - int(x)) < param.tolerance:
##            x = int(x)
##    elif hasattr(x, 'valeur'):
##        return nice_display(x.valeur)
##    return str(x).replace('**', '^')
##
##
##
##def arrondir(x):
##    u"""Arrondi le nombre : un seul chiffre significatif, compris entre 1 et 5.
##    Transforme automatiquement le nombre en entier selon le cas."""
##    n = nchiffres(x, math.sqrt(.5))
##    if int(n) == n:
##        n = int(n)
##    return n
##
##
##def array_zip(*args):
##    return (pylab.array(item) for item in zip(*args))
##
##
### Les deux fonctions qui suivent sont bien plus rapides que la classe Polynome pour fournir des solutions approchees.
### Elles servent comme routine dans geolib par exemple.
##
##def delta(a, b, c):
##    return b**2 - 4*a*c
##
##def racines(a, b, c):
##    d = delta(a, b, c)
##    if not d:
##        return [-b/(2*a)]
##    if d > 0:
##        rac = math.sqrt(d)
##        return [(-rac-b)/(2*a) , (rac-b)/(2*a)]
##    return []
##
##
##
##
##def point_dans_polygone(couple, polygone):
##    u"""Détermine si un point est à l'intérieur d'un polygone.
##    D'après un algorithme de Paul Bourke."""
##    x, y = couple
##    dedans = False
##    n = len(polygone)
##    p1x, p1y = polygone[0]
##    for i in range(1, n + 1):
##        p2x, p2y = polygone[i % n]
##        if min(p1y, p2y) < y <= max(p1y, p2y) and x <= max(p1x, p2x):
##            if p1y != p2y:
##                xinters = (y - p1y)*(p2x - p1x)/(p2y - p1y) + p1x
##                if p1x == p2x or x <= xinters:
##                    dedans = not dedans
##        p1x, p1y = p2x, p2y
##
##    return dedans
##
##
##def enveloppe_convexe(*points):
##    u"""Donne l'enveloppe convexe d'un ensemble de points.
##    D'après Dinu C. Gherman (Andrew's Monotone Chain Algorithm)."""
##    def det(p, q, r):
##        return (q[0]*r[1] + p[0]*q[1] + r[0]*p[1]) - (q[0]*p[1] + r[0]*q[1] + p[0]*r[1])
##
##    # Get a local list copy of the points and sort them.
##    points = sorted(points)
##    # Build upper half of the hull.
##    upper = [points[0], points[1]]
##    for p in points[2:]:
##        upper.append(p)
##        # Le déterminant est positif ssi l'on tourne à gauche
##        while len(upper) > 2 and det(*upper[-3:]) >= 0:
##            del upper[-2]
##    # Build lower half of the hull.
##    points.reverse()
##    lower = [points[0], points[1]]
##    for p in points[2:]:
##        lower.append(p)
##        while len(lower) > 2 and det(*lower[-3:]) >= 0:
##            del lower[-2]
##    # Remove duplicates.
##    del lower[0], lower[-1]
##    # Concatenate both halfs and return.
##    return upper + lower
##
##
##def point_dans_enveloppe_convexe(point, polygone):
##    u"""Détermine si un point est à l'intérieur de l'enveloppe convexe d'un polygone."""
##    def det(p, q, r):
##        return (q[0]*r[1] + p[0]*q[1] + r[0]*p[1]) - (q[0]*p[1] + r[0]*q[1] + p[0]*r[1])
##
##    xmin = min(pt[0] for pt in polygone)
##    xmax = max(pt[0] for pt in polygone)
##    ymin = min(pt[1] for pt in polygone)
##    ymax = max(pt[1] for pt in polygone)
##    if not(xmin < point[0] < xmax and ymin < point[1] < ymax):
##        return False
##    # Get a local list copy of the points and sort them.
##    points = sorted(tuple(polygone) + (point,))
##    # Build upper half of the hull.
##    upper = [points[0], points[1]]
##    for p in points[2:]:
##        upper.append(p)
##        # Le déterminant est positif ssi l'on tourne à gauche
##        while len(upper) > 2 and det(*upper[-3:]) >= 0:
##            del upper[-2]
##    if point in upper:
##        return False
##    # Build lower half of the hull.
##    points.reverse()
##    lower = [points[0], points[1]]
##    for p in points[2:]:
##        lower.append(p)
##        while len(lower) > 2 and det(*lower[-3:]) >= 0:
##            del lower[-2]
##    return point not in lower
##
##'''
##def distance_point_ellipse(centre, rx, ry, point):
##    u"""Distance approchée entre un point et une ellipse orientée selon les axes.
##
##    D'après http://www.spaceroots.org/documents/distance/node9.html"""
##    a,  b = centre
##    x, y = point
##    # L'ellipse est déjà orientée selon les axes, on prend le centre de l'ellipse comme origine
##    x -= a
##    y -= b
##    # On se ramène au premier cadran, (Ox) et (Oy) étant des axes de symétrie de l'ellipse
##    x = abs(x)
##    y = abs(y)
##    # On s'arrange pour que rx soit le semi-grand axe
##    if rx < ry:
##        rx, ry = ry, rx
##        x, y = y, x
##    # Cas particulier : ellipse réduite à un point
##    if rx < param.tolerance:
##        return x**2 + y**2
##    f = (rx - ry)/rx
##    # Cas particulier : le point est confondu avec le centre de l'ellipse
##    if x**2 + y**2 < param.tolerance**2:
##        return ry
##    # Cas général : http://www.spaceroots.org/documents/distance/node9.html
##    s = math.sqrt(x**2 + y**2)
##    cos0 = x/s
##    sin0 = y/s
##    t0 = sin0/(1 - cos0)
##    a = ((1 - f)*cos0)**2 + sin0**2
##    b = (1 - f)**2*x*cos0 + y*sin0
##    c = (1 - f)**2*(x**2 - rx**2) + y**2
##    k0 = c/(b + math.sqrt(b**2 - a*c))
##    # Nouveau point :
##    x0 = x - k*cos0
##    y0 = x - k*sin0
##    phi = math.atan2(y, x*(1 - f)**2)
##'''
##
##
##def carre_distance_point_ellipse(centre, rx, ry, point, epsilon = param.tolerance):
##    u"""Distance approchée entre un point et une ellipse orientée selon les axes.
##
##    Algorithme naïf, d'après moi-même. ;-)"""
##    xO, yO = centre
##    x, y = point
##    # L'ellipse est déjà orientée selon les axes, on prend le centre de l'ellipse comme origine
##    x -= xO
##    y -= yO
##    # On se ramène au premier cadran, (Ox) et (Oy) étant des axes de symétrie de l'ellipse
##    x = abs(x)
##    y = abs(y)
##    rx = abs(rx)
##    ry = abs(ry)
##    def f(t):
##        return (rx*math.cos(t) - x)**2 + (ry*math.sin(t) - y)**2
##    a = 0
##    b = math.pi/2
##    while b - a > epsilon:
##        i = (a + b)/2
##        fim = f(i - epsilon)
##        fi = f(i)
##        fip = f(i + epsilon)
##        if fim < fi < fip:
##            b = i
##        elif fim > fi > fip:
##            a = i
##        else:
##            break
##    return fi
##
##
##
##def segments_secants(p1, p2, p3, p4):
##        d1 = direction_droite(p3, p4, p1)
##        d2 = direction_droite(p3, p4, p2)
##        d3 = direction_droite(p1, p2, p3)
##        d4 = direction_droite(p1, p2, p4)
##        return ((d1>0 and d2<0) or (d1<0 and d2>0)) and ((d3>0 and d4<0) or (d3<0 and d4>0))
##
##def direction_droite(pi, pj, pk):
##    xi, yi = pi
##    xj, yj = pj
##    xk, yk = pk
##    return (xk - xi)*(yj - yi) - (yk - yi)*(xj - xi)


def _simplify(expr):
    u"""Simplifie une expression.

    Alias de sympy.simplify (sympy 0.6.4).
    Mais sympy.simplify n'est pas garanti d'être stable dans le temps.
    (Cf. sympy.simplify.__doc__)."""
    return sympy.together(sympy.expand(sympy.Poly.cancel(sympy.powsimp(expr))))


def _is_num(val):
    return isinstance(val, (float, sympy.Float))

def poly_factor(polynome, variable, corps = None, approchee = None):
    u"""Factorise un polynome à une variable.

    Le corps peut être R ou C.
    Par défaut, le corps de factorisation est celui des coefficients."""
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
        racines_brutes = {}.fromkeys(numpy.roots(coeffs),  1)
    else:
        if corps == "R":
            if not all(coeff.is_real for coeff in coeffs):
                raise ValueError, "factorisation dans 'R' impossible."
        elif corps is None:
            if all(coeff.is_real for coeff in coeffs):
                corps = "R"
            else:
                corps = "C"
        racines_brutes = sympy.roots(polynome, variable, cubics=True, quartics=True)
    racines = list((sympy_functions.simplifier_racines(racine), mult) for racine, mult in racines_brutes.iteritems())

    if approchee:
        nbr_racines = sum(multiplicite for racine, multiplicite in racines)
        if nbr_racines < sym_poly.degree():
            # On cherche une approximation des racines manquantes
            sol_approchees = list(numpy.roots(coeffs))
            # On associe à chaque racine l'approximation qui lui correspond
            for racine, multiplicite in racines:
                distances = [(sol, abs(complex(racine) - sol)) for sol in sol_approchees]
                distances.sort(key = lambda x:x[1])
                for i in range(multiplicite):
                    distances.pop(0)
                # Les racines approchées qui restent ne correspondent à aucune racine exacte
                sol_approchees = [sol for sol, distance in distances]
            racines.extend((sympy.sympify(sol), sol_approchees.count(sol)) for sol in set(sol_approchees))

    coefficient = coeffs[0]
    produit = 1
    if corps == "R":
        racines_en_stock = []
        multiplicites_en_stock = []
        for racine, multiplicite in racines:
            if not isinstance(racine, sympy.Basic):
                racine = sympy.sympify(racine)
            reel = racine.is_real
            if not reel:
                # is_real n'est pas fiable (26/11/2009)
                # cf. ((54*6**(1/3)*93**(1/2) - 162*I*6**(1/3)*31**(1/2) - 522*6**(1/3) + 6*6**(2/3)*(-522 + 54*93**(1/2))**(1/3) + 522*I*3**(1/2)*6**(1/3) + 6*I*3**(1/2)*6**(2/3)*(-522 + 54*93**(1/2))**(1/3) - 24*(-522 + 54*93**(1/2))**(2/3))/(36*(-522 + 54*93**(1/2))**(2/3))).is_real
                re, im = racine.as_real_imag()
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
    quotient, reste = sympy.div(polynome, coefficient*produit, variable)
    if reste != 0 and not approchee:
        raise NotImplementedError
    return coefficient*produit*quotient

def syms(expression):
    u"""Retourne la liste des symboles utilisés par l'expression."""
    return tuple(expression.atoms(sympy.Symbol))

def extract_var(expression):
    u"""Retourne la variable de l'expression (renvoie un avertissement s'il y en a plusieurs, et 'x' par défaut s'il n'y en a pas)."""
    if hasattr(expression, "atoms"):
        symboles = expression.atoms(sympy.Symbol)
        if len(symboles) == 0:
            return sympy.Symbol("x")
        else:
            if len(symboles) > 1 and param.debug:
                warning("l'expression possede plusieurs variables.")
            return expression.atoms(sympy.Symbol).pop()
    else:
        return sympy.Symbol("x")

def count_syms(expression, symbole):
    u"""Compte le nombre d'occurence de la variable dans l'expression."""
    if expression.has_any_symbols(symbole):
        if expression.is_Atom:
            return 1
        else:
            return sum(count_syms(arg, symbole) for arg in expression.args)
    else:
        return 0
