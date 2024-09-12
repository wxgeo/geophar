# -*- coding: utf-8 -*-

##--------------------------------------#######
#                        Geolib                     #
##--------------------------------------#######
#    WxGeometrie
#    Dynamic geometry, graph plotter, and more for french mathematic teachers.
#    Copyright (C) 2005-2013  Nicolas Pourcelot
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

from math import cos, sin, hypot, ceil, floor, sqrt, pi, log10, copysign
import re
from functools import partial

import numpy

from sympy import sqrt as s_sqrt
from .contexte import contexte
from ..mathlib.universal_functions import arg as u_arg, sqrt as u_sqrt
from ..mathlib.printers import custom_str



def confondus(M, N):
    try:
        (xM, yM), (xN, yN) = M, N
    except Exception:
        return False
    eps = contexte['tolerance']
    return abs(xN - xM) < eps and abs(yM - yN) < eps


def distincts(M, N):
    try:
        (xM, yM), (xN, yN) = M, N
    except Exception:
        return False
    eps = contexte['tolerance']
    return abs(xN - xM) > eps or abs(yM - yN) > eps


def distincts2a2(*points):
    for i, M in enumerate(points):
        for N in points[i + 1:]:
            if not distincts(M, N):
                return False
    return True


def radian(val):
    unite = contexte['unite_angle']
    if unite == 'd':
        return 180*val/pi
    elif unite == 'g':
        return 200*val/pi
    assert unite == 'r'
    return val


## Fonctions rapides destinées essentiellement à géolib

def produit_scalaire(u, v):
    """Calcule le produit scalaire des vecteurs u et v.
    u et v doivent être de type list, tuple, array, ou geolib.Vecteur."""
    return sum(i*j for i, j in zip(u ,v))



#def angle_vectoriel(u, v):
#    u"""Renvoie une mesure sur ]-pi;pi] de l'angle formé par les vecteurs u et v.
#    u et v doivent être de type list, tuple, array, ou geolib.Vecteur, et de dimension 2."""
#    return clog(complex(*v)/complex(*u)).imag

def angle_vectoriel(u, v):
    """Renvoie une mesure sur ]-pi;pi] de l'angle formé par les vecteurs u et v.
    u et v doivent être de type list, tuple, array, ou geolib.Vecteur, et de dimension 2.

    Version compatible avec sympy."""
    return u_arg((v[0] + v[1]*1j)/(u[0] + u[1]*1j))

#~ def _angle_vectoriel_bis_(u, v):
    #~ u"Autre implémentation du produit vectoriel (un peu plus lente)."
    #~ return (cmp(u[0]*v[1]-v[0]*u[1], 0) or 1)*acos(produit_scalaire(u, v)/(hypot(*u)*hypot(*v)))


def norme(x, y):
    "Implémentation rapide de la norme d'un vecteur."
    if isinstance(x, (int, float)) or isinstance(y, (int, float)):
        return hypot(x, y)
    return u_sqrt(x**2 + y**2)



def distance(A, B):
    "Distance entre les points A et B."
    xA, yA = A
    xB,  yB = B
    return norme(xA - xB, yA - yB)

def carre_distance(A, B):
    "Carré de la distance entre les points A et B."
    xA, yA = A
    xB, yB = B
    return (xB - xA)**2+(yB - yA)**2

def vect(A, B):
    "Coordonnées du vecteur A>B."
    xA, yA = A
    xB, yB = B
    return xB - xA, yB - yA

def det(vec1, vec2):
    "Déterminant de deux vecteurs du plan."
    x1, y1 = vec1
    x2, y2 = vec2
    return x1*y2 - x2*y1

## Fonctions de formatage (pour l'affichage entre autres)

#~ def old_nchiffres(x, n = 1):
    #~ u"Arrondi x en fournissant n chiffres significatifs. Ex: nchiffres(2345, 2)."

    #~ return x and round(x/10**floor(log10(abs(x))-n+1))*10**floor(log10(abs(x))-n+1) # Attention au cas x = 0 !


def array_zip(*args):
    return (numpy.array(item) for item in zip(*args))


# Les deux fonctions qui suivent sont bien plus rapides que la classe Polynome pour fournir des solutions approchees.
# Elles servent comme routine dans geolib par exemple.

def delta(a, b, c):
    return b**2 - 4*a*c

def racines(a, b, c, exact=False):
    d = delta(a, b, c)
    if not d:
        return [-b/(2*a)]
    if d > 0:
        rac = (s_sqrt(d) if exact else sqrt(d))
        return [(-rac-b)/(2*a) , (rac-b)/(2*a)]
    return []




def point_dans_polygone(couple, polygone):
    """Détermine si un point est à l'intérieur d'un polygone.
    D'après un algorithme de Paul Bourke."""
    x, y = couple
    dedans = False
    n = len(polygone)
    p1x, p1y = polygone[0]
    for i in range(1, n + 1):
        p2x, p2y = polygone[i % n]
        if min(p1y, p2y) < y <= max(p1y, p2y) and x <= max(p1x, p2x):
            if p1y != p2y:
                xinters = (y - p1y)*(p2x - p1x)/(p2y - p1y) + p1x
                if p1x == p2x or x <= xinters:
                    dedans = not dedans
        p1x, p1y = p2x, p2y

    return dedans


def enveloppe_convexe(*points):
    """Donne l'enveloppe convexe d'un ensemble de points.
    D'après Dinu C. Gherman (Andrew's Monotone Chain Algorithm)."""
    def det(p, q, r):
        return (q[0]*r[1] + p[0]*q[1] + r[0]*p[1]) - (q[0]*p[1] + r[0]*q[1] + p[0]*r[1])

    # Get a local list copy of the points and sort them.
    points = sorted(points)
    # Build upper half of the hull.
    upper = [points[0], points[1]]
    for p in points[2:]:
        upper.append(p)
        # Le déterminant est positif ssi l'on tourne à gauche
        while len(upper) > 2 and det(*upper[-3:]) >= 0:
            del upper[-2]
    # Build lower half of the hull.
    points.reverse()
    lower = [points[0], points[1]]
    for p in points[2:]:
        lower.append(p)
        while len(lower) > 2 and det(*lower[-3:]) >= 0:
            del lower[-2]
    # Remove duplicates.
    del lower[0], lower[-1]
    # Concatenate both halfs and return.
    return upper + lower


def point_dans_enveloppe_convexe(point, polygone):
    """Détermine si un point est à l'intérieur de l'enveloppe convexe d'un polygone."""
    def det(p, q, r):
        return (q[0]*r[1] + p[0]*q[1] + r[0]*p[1]) - (q[0]*p[1] + r[0]*q[1] + p[0]*r[1])

    xmin = min(pt[0] for pt in polygone)
    xmax = max(pt[0] for pt in polygone)
    ymin = min(pt[1] for pt in polygone)
    ymax = max(pt[1] for pt in polygone)
    if not(xmin < point[0] < xmax and ymin < point[1] < ymax):
        return False
    # Get a local list copy of the points and sort them.
    points = sorted(tuple(polygone) + (point,))
    # Build upper half of the hull.
    upper = [points[0], points[1]]
    for p in points[2:]:
        upper.append(p)
        # Le déterminant est positif ssi l'on tourne à gauche
        while len(upper) > 2 and det(*upper[-3:]) >= 0:
            del upper[-2]
    if point in upper:
        return False
    # Build lower half of the hull.
    points.reverse()
    lower = [points[0], points[1]]
    for p in points[2:]:
        lower.append(p)
        while len(lower) > 2 and det(*lower[-3:]) >= 0:
            del lower[-2]
    return point not in lower

'''
def distance_point_ellipse(centre, rx, ry, point):
    u"""Distance approchée entre un point et une ellipse orientée selon les axes.

    D'après http://www.spaceroots.org/documents/distance/node9.html"""
    a,  b = centre
    x, y = point
    # L'ellipse est déjà orientée selon les axes, on prend le centre de l'ellipse comme origine
    x -= a
    y -= b
    # On se ramène au premier cadran, (Ox) et (Oy) étant des axes de symétrie de l'ellipse
    x = abs(x)
    y = abs(y)
    # On s'arrange pour que rx soit le semi-grand axe
    if rx < ry:
        rx, ry = ry, rx
        x, y = y, x
    # Cas particulier : ellipse réduite à un point
    if rx < param.tolerance:
        return x**2 + y**2
    f = (rx - ry)/rx
    # Cas particulier : le point est confondu avec le centre de l'ellipse
    if x**2 + y**2 < param.tolerance**2:
        return ry
    # Cas général : http://www.spaceroots.org/documents/distance/node9.html
    s = sqrt(x**2 + y**2)
    cos0 = x/s
    sin0 = y/s
    t0 = sin0/(1 - cos0)
    a = ((1 - f)*cos0)**2 + sin0**2
    b = (1 - f)**2*x*cos0 + y*sin0
    c = (1 - f)**2*(x**2 - rx**2) + y**2
    k0 = c/(b + sqrt(b**2 - a*c))
    # Nouveau point :
    x0 = x - k*cos0
    y0 = x - k*sin0
    phi = atan2(y, x*(1 - f)**2)
'''


def carre_distance_point_ellipse(centre, rx, ry, point, epsilon = None):
    """Distance approchée entre un point et une ellipse orientée selon les axes.

    Algorithme naïf, d'après moi-même. ;-)"""
    if epsilon is None:
        epsilon = contexte["tolerance"]
    xO, yO = centre
    x, y = point
    # L'ellipse est déjà orientée selon les axes, on prend le centre de l'ellipse comme origine
    x -= xO
    y -= yO
    # On se ramène au premier cadran, (Ox) et (Oy) étant des axes de symétrie de l'ellipse
    x = abs(x)
    y = abs(y)
    rx = abs(rx)
    ry = abs(ry)
    def f(t):
        return (rx*cos(t) - x)**2 + (ry*sin(t) - y)**2
    a = 0
    b = pi/2
    while b - a > epsilon:
        i = (a + b)/2
        fim = f(i - epsilon)
        fi = f(i)
        fip = f(i + epsilon)
        if fim < fi < fip:
            b = i
        elif fim > fi > fip:
            a = i
        else:
            break
    return fi



def segments_secants(p1, p2, p3, p4):
        d1 = direction_droite(p3, p4, p1)
        d2 = direction_droite(p3, p4, p2)
        d3 = direction_droite(p1, p2, p3)
        d4 = direction_droite(p1, p2, p4)
        return ((d1>0 and d2<0) or (d1<0 and d2>0)) and ((d3>0 and d4<0) or (d3<0 and d4>0))

def direction_droite(pi, pj, pk):
    xi, yi = pi
    xj, yj = pj
    xk, yk = pk
    return (xk - xi)*(yj - yi) - (yk - yi)*(xj - xi)



def trigshift(t, a = 0):
    "Retourne le représentant de t[2pi] situé dans l'intervalle [a; a+2pi[."
    return t + 2*pi*ceil((a - t)/(2*pi))


def distance_segment(M, A, B, d):
    """Teste si la distance entre le point M et le segment [AB] est inférieure à d.

    M, A et B sont des couples de réels, et d un réel.
    Cf. "distance_point_segment.odt" dans "developpeurs/maths/".
    """
    x, y = M
    if A is None or B is None:
        if A is None and B is None:
            return False
        A = B = A or B
    xA, yA = A
    xB, yB = B
    x1 = min(xA, xB) - d; x2 = max(xA, xB) + d
    y1 = min(yA, yB) - d; y2 = max(yA, yB) + d
    if x1 < x < x2 and y1 < y < y2:
        norme2 = ((xB - xA)**2 + (yB - yA)**2)
        if norme2 > contexte['tolerance']:
            return ((yA - yB)*(x - xA) + (xB - xA)*(y - yA))**2/norme2 < d**2
        else:   # les extrémités du segment sont confondues
            return (x - xA)**2 + (y - yA)**2 < d**2
    else:
        return False


# ----------------------
# Fonctions de formatage
# ----------------------

def nchiffres(x, n = 1):
    """Arrondi x en fournissant n chiffres significatifs.

    >>> from wxgeometrie.geolib.routines import nchiffres
    >>> nchiffres(2345, 2)
    2300
    """
    if x:
        k = 10**floor(log10(abs(x))-n+1)
        return round(x/k)*k
    return x # Attention au cas x = 0 !


TRAILING_ZEROS = re.compile(r"\.[0-9]*0+(?![0-9])")

def strip_trailing_zeros(s):
    """"Supprime tous les zeros inutiles des nombres flottants.

    >>> from wxgeometrie.geolib.routines import strip_trailing_zeros
    >>> strip_trailing_zeros("4.0000")
    '4'
    >>> strip_trailing_zeros("4.200*x + 3.007*y + 5.0*z + .010 = 0")
    '4.2*x + 3.007*y + 5*z + .01 = 0'
    """
    return re.sub(TRAILING_ZEROS, lambda m:m.group().rstrip('0').rstrip('.'), s)


def nice_display(x):
    if isinstance(x, float):
        x = round(x, contexte["decimales"])
        if abs(x - int(x)) < contexte["tolerance"]:
            x = int(x)
    elif hasattr(x, 'valeur'):
        return nice_display(x.valeur)
    s = strip_trailing_zeros(str(x).replace('**', '^'))
    if contexte["separateur_decimal"] == ',':
        s = s.replace('.', ',')
    return s


def arrondir(x):
    """Arrondi le nombre : un seul chiffre significatif, compris entre 1 et 5.
    Transforme automatiquement le nombre en entier selon le cas."""
    n = nchiffres(x, sqrt(.5))
    if int(n) == n:
        n = int(n)
    return n


def arrondir_1_2_5(x):
    """Arrondit x à un nombre de la forme k*10^p, avec k dans {1, 2, 5},
    et p entier relatif.

    >>> from wxgeometrie.geolib.routines import arrondir_1_2_5
    >>> arrondir_1_2_5(250)
    200
    >>> arrondir_1_2_5(4527)
    5000
    >>> arrondir_1_2_5(0.0078)
    0.01
    """
    p = floor(log10(abs(x)))
    k = x/10**p
    if k < 1.4142135623730951:
        # 10**(log10(2)/2)
        k = 1
    elif k < 3.1622776601683795:
        # 10**((log10(2)+log10(5))/2)
        k = 2
    elif k < 7.0710678118654746:
        # 10**((log10(5) + 1)/2)
        k = 5
    else:
        k = 1
        p += 1
    return k*10**p


def arrondir_1_25_5(x):
    """Arrondit x à un nombre de la forme k*10^p, avec k dans {1, 2.5, 5},
    et p entier relatif.

    >>> from wxgeometrie.geolib.routines import arrondir_1_25_5
    >>> arrondir_1_25_5(200)
    250
    >>> arrondir_1_25_5(4527)
    5000
    >>> arrondir_1_25_5(0.0078)
    0.01
    """
    p = floor(log10(abs(x)))
    k = x/10**p
    if k < 1.5811388300841898:
        # 10**(log10(2.5)/2)
        k = 1
    elif k < 3.5355339059327378:
        # 10**((log10(2.5)+log10(5))/2)
        k = 25
        p -= 1
    elif k < 7.0710678118654746:
        # 10**((log10(5) + 1)/2)
        k = 5
    else:
        k = 1
        p += 1
    return k*10**p



def formatage(eqn):
    """Améliore l'affichage des équations.

    >>> from wxgeometrie.geolib.routines import formatage
    >>> formatage('1 x + -1/3 y + 1 = 0')
    'x - 1/3 y + 1 = 0'
    >>> formatage('-1 x + -1 y + -1 = 0')
    '-x - y - 1 = 0'
    >>> formatage('2 x + 0 y - 28 = 0')
    '2 x - 28 = 0'
    >>> formatage(u'x\xb2 + y\xb2 + -1 x + -4/3 y + -47/36 = 0') == u'x\xb2 + y\xb2 - x - 4/3 y - 47/36 = 0'
    True
    """
    #FIXME: pour l'instant, ça ne marche qu'avec x et y (il ne faut
    # pas qu'il y ait de xy dans l'équation, ni de t, etc.)
    if eqn.startswith('1 '):
        eqn = eqn[2:]
    return eqn.replace("+ -1", "- 1").replace('-1 x', '-x').replace('-1 y', '-y')\
              .replace("+ -", "- ").replace('- 1 x', '- x').replace('- 1 y', '- y')\
              .replace('+ 1 x', '+ x').replace('+ 1 y', '+ y')\
              .replace('+ 0 x ', '').replace('+ 0 y ', '').replace('+ 0 ', '')


def nice_str(x):
    """Convertit en chaîne de caractères les objets mathématiques.

    Améliore le formatage de ces objets:
      * Supprime les 0 inutiles.

        >>> from wxgeometrie.geolib.routines import nice_str
        >>> nice_str(8.0)
        '8'

      * Remplace le point par une virgule pour les décimaux.

        >>> nice_str(8.2)
        '8,2'

      * Personnalise un peu l'affichage de certains objets sympy,
        pour correspndre aux notations française.

        >>> from sympy import oo, log
        >>> nice_str(oo)
        '+oo'
        >>> nice_str(log(7))
        'ln(7)'

    """
    return strip_trailing_zeros(custom_str(x)).replace('.', ',')


sign = partial(copysign, 1)
