# -*- coding: utf-8 -*-

##--------------------------------------#######
#           Mathlib 2 (sympy powered)         #
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

## Cette librairie contient les fonctions de haut niveau non inclues dans sympy.

import math

from sympy import Rational, sqrt, S
from sympy.stats import Normal, Binomial, P
import sympy.stats






def _convertir_en_frequences(frequences, serie):
    if frequences is None:
        n = len(serie)
        return n*[Rational(1, n)]
    else:
        total = sum(frequences)
        if total != 1:
            return [val/total for val in frequences]
        return frequences

def moyenne(serie, coeffs = None):
    "Calcule l'espérance de la série des (xi, fi)."
    frequences = _convertir_en_frequences(coeffs, serie)
    return sum(xi*fi for xi, fi in zip(serie, frequences))

def variance(serie, coeffs = None):
    "Calcule la variance de la serie des (xi, fi)"
    frequences = _convertir_en_frequences(coeffs, serie)
    M = moyenne(serie, frequences)
    return sum(fi*(xi - M)**2 for xi, fi in zip(serie, frequences))

def ecart_type(serie, coeffs = None):
    "Retourne l'écart-type de la série des (xi, fi)."
    return sqrt(variance(serie, coeffs))

def covariance(serie1, serie2, coeffs = None):
    "Retourne la covariance des deux séries."
    assert len(serie1) == len(serie2), "Les deux séries doivent avoir le même nombre de valeurs."
    frequences = _convertir_en_frequences(coeffs, serie1)
    x_ = moyenne(serie1, frequences)
    y_ = moyenne(serie2, frequences)
    return sum(fi*(xi - x_)*(yi - y_) for xi, yi, fi in zip(serie1, serie2, frequences))

def linreg(serie1, serie2, coeffs = None):
    """Droite de régression par la méthode des moindres carrés.

    Retourne les coefficients a et b de l'équation y=ax+b
     de la droite de régression par la méthode des moindres carrés.

     >>> from wxgeometrie.mathlib.custom_functions import linreg
     >>> linreg((85.6,84.5,81,80.2,72.8,71.2,73,48.1),(78.7,77.6,75.2,71.1,67.7,66.3,59.1,46.8))
     (0.849191825268073, 4.50524942626518)
     """
    a = covariance(serie1, serie2)/variance(serie1)
    b = moyenne(serie2) - a*moyenne(serie1)
    return a, b




def proba(relation):
    if relation is True:
        return S.One
    elif relation is False:
        return S.Zero
    else:
        return P(relation)


def inv_normal(p):
    """
    Lower tail quantile for standard normal distribution function.

    This function returns an approximation of the inverse cumulative
    standard normal distribution function.  I.e., given P, it returns
    an approximation to the X satisfying P = Pr{Z <= X} where Z is a
    random variable from the standard normal distribution.

    The algorithm uses a minimax approximation by rational functions
    and the result has a relative error whose absolute value is less
    than 1.15e-9.

    Author:      Peter John Acklam
    Time-stamp:  2000-07-19 18:26:14
    E-mail:      pjacklam@online.no
    WWW URL:     http://home.online.no/~pjacklam
    """

    if p <= 0 or p >= 1:
        # The original perl code exits here, we'll throw an exception instead
        raise ValueError("Argument to inv_normal %f must be in open interval (0,1)" % p)

    # Coefficients in rational approximations.
    a = (-3.969683028665376e+01,  2.209460984245205e+02, \
         -2.759285104469687e+02,  1.383577518672690e+02, \
         -3.066479806614716e+01,  2.506628277459239e+00)
    b = (-5.447609879822406e+01,  1.615858368580409e+02, \
         -1.556989798598866e+02,  6.680131188771972e+01, \
         -1.328068155288572e+01 )
    c = (-7.784894002430293e-03, -3.223964580411365e-01, \
         -2.400758277161838e+00, -2.549732539343734e+00, \
          4.374664141464968e+00,  2.938163982698783e+00)
    d = (7.784695709041462e-03,  3.224671290700398e-01, \
          2.445134137142996e+00,  3.754408661907416e+00)

    # Define break-points.
    plow  = 0.02425
    phigh = 1 - plow

    # Rational approximation for lower region:
    if p < plow:
       q  = math.sqrt(-2*math.log(p))
       return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)

    # Rational approximation for upper region:
    if phigh < p:
       q  = math.sqrt(-2*math.log(1-p))
       return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)

    # Rational approximation for central region:
    q = p - 0.5
    r = q*q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def fluctu(probabilite, taille=1000, seuil=None):
    """Intervalle de fluctuation.

    Retourne l'intervalle de fluctuation correspondant à un échantillon de taille
    `taille`, lorsque la probabilité est `probabilite`.

    Par défaut, lorsque le seuil n'est pas fixé, l'approximation
    [p - 1.96*sqrt(p(1-p)/n), p + 1.96*sqrt(p(1-p)/n)] est utilisée,
    pour un seuil environ égal à 95%.
    """
    if seuil is None:
        # Approximation usuelle pour un seuil à 95%
        a = 1.96
    else:
        # P(-a < X < a) == seuil <=> P(X < a) == (seuil + 1)/2
        a = inv_normal((seuil + 1)/2)
    delta = a*math.sqrt(probabilite*(1 - probabilite)/taille)
    return probabilite - delta, probabilite + delta


def confiance(frequence, taille=1000, seuil=None):
    """Intervalle de confiance au seuil de 95%.

    Retourne l'intervalle de confiance correspondant à un échantillon de taille
    `taille`, lorsque la fréquence observée sur l'échantillon est `frequence`.

    Par défaut, si seuil n'est pas fixé, l'approximation utilisée est
    [f - 1/sqrt(n), f + 1/sqrt(n)], pour un seuil environ égal à 95%.
    """
    if seuil is not None:
        return fluctu(frequence, taille, seuil)
    delta = 1/math.sqrt(taille)
    return frequence - delta, frequence + delta


def normal(a, b, mu=0, sigma=1):
    """Retourne P(a < X < b), où X suit la loi normale N(mu, sigma²).
    """
    X = Normal('X', mu, sigma)
    return (proba(X <= b) - proba(X < a)).evalf()


def binomial(a, b, n, p):
    """Retourne P(a <= X <= b), où X suit la loi binomiale B(n, p).

    ..note:: Taper binomial(a, a, n, p) pour calculer P(X = a).
    """
    X = Binomial('X', n, p)
    return (proba(X <= b) - proba(X < a)).evalf()


def va(loi, *parametres):
    # [key for key, val in sympy.stats.__dict__.items()
    #                if isinstance(val, types.FunctionType)
    #                   and len(key) > 1 and key[0].isupper()]
    loi = loi.capitalize()
    synonymes = {'Binomiale': 'Binomial',  'Hypergeometrique': 'Hypergeometric',
                 'Uniforme': 'Uniform', 'De': 'Die', 'Piece': 'Coin',
                 'Triangulaire': 'Triangular', 'Normale': 'Normal',
                }
    loi = synonymes.get(loi, loi)
    try:
        return sympy.stats.__dict__[loi]('X', *parametres)
    except KeyError:
        raise KeyError('Loi "%s" inconnue !' % loi)
