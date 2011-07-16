# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                   Interpolation                    #
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

from numpy import array, arange, append

from .objet import Ref, Argument, Arguments
from .courbes import Courbe_generique

from ..pylib import fullrange
from .. import param

class Interpolation_generique(Courbe_generique):
    u"""Classe mère de toutes les interpolations."""

    points = __points = Arguments("Point_generique")
    debut = __fin = Argument("bool")
    fin = __debut = Argument("bool")

    _style_defaut = param.segments

    def __init__(self, *points, **styles):
        debut = styles.pop("debut", True)
        fin = styles.pop("fin", True)
        self.__points = points = tuple(Ref(pt) for pt in points)
        self.__debut = debut = Ref(debut)
        self.__fin = fin = Ref(fin)
        Courbe_generique.__init__(self, **styles)

##    def _extremite_arc(self, x, y, vecteur):
##        coeff0, coeff1 = self.__canvas__.coeffs()
##        if coeff0 == 0 or coeff1 == 0:
##            warning("Resolution d'affichage incorrecte (division par zero).")
##            return
##        vecteur = vecteur[0]/-coeff0, vecteur[1]/coeff1
##        if vecteur[0] == 0:
##            if vecteur[1] > 0:
##                angle = math.pi/2
##            else:
##                angle = -math.pi/2
##        else:
##            angle = math.arctan(vecteur[1]/vecteur[0])
##            if vecteur[0] < 0:
##                angle += math.pi
##        # donne l'angle d'incidence a l'extremite
##        t = arange(angle - math.pi/2, angle + math.pi/2, 0.05)
##        R = self.__canvas__.taille["("]
##
##        x, y = self.__canvas__.coo2pix(x, y)
##        return self.__canvas__.pix2coo(x + R*(cos(t) - math.cos(angle)), y + R*(sin(t) - math.sin(angle)))


    def _affiche_extremites(self, vec_deb = None, vec_fin = None):
        couleur = self.style("couleur")
        niveau = self.style("niveau")
        epaisseur = self.style("epaisseur")
        # Début de la courbe
        plot = self._representation[-2]
        x, y = self.__points[0].coordonnees
        a, b = self.__points[1].coordonnees
        if vec_deb is None:
            vec_deb = (x-a, y-b)
        if self.__debut == True:
            plot.set_data((x,), (y,))
            plot.set(visible=True, color=couleur, marker="o", markeredgecolor=couleur,
                     markersize=2*self.__canvas__.taille["o"], linewidth=epaisseur)
            plot.zorder = niveau
        elif self.__debut == False:
            plot.set_data(*self._extremite_arc(x, y, vec_deb))
            plot.set(visible=True, color=couleur, linewidth=epaisseur)
            plot.zorder = niveau
        else:
            plot.set_visible(False)

        # Fin de la courbe
        plot = self._representation[-1]
        x, y = self.__points[-1].coordonnees
        a, b = self.__points[-2].coordonnees
        if vec_fin is None:
            vec_fin = (x-a, y-b)
        if self.__fin == True:
            plot.set_data((x,), (y,))
            plot.set(visible=True, color=couleur, marker="o", markeredgecolor=couleur,
                     markersize=2*self.__canvas__.taille["o"], linewidth=epaisseur)
            plot.zorder = niveau
        elif self.__fin == False:
            arc = self.rendu.arc(x, y, vec_fin)
            plot.set_data(arc._x.data, arc._y.data) # À TESTER !!
            plot.set(visible=True, color=couleur, linewidth=epaisseur)
            plot.zorder = niveau
        else:
            plot.set_visible(False)








class Interpolation_lineaire(Interpolation_generique):
    u"""Une interpolation linéaire.

    Interpolation entre les points donnés par des segments joints (courbe de classe C0).
    """

    points = __points = Arguments("Point_generique")
    debut = __fin = Argument("bool")
    fin = __debut = Argument("bool")

    def __init__(self, *points, **styles):
        if styles.get("points", None):
            points = styles.pop("points")
        debut = styles.pop("debut", True)
        fin = styles.pop("fin", True)
        self.__points = points = tuple(Ref(pt) for pt in points)
        self.__debut = debut = Ref(debut)
        self.__fin = fin = Ref(fin)
        Interpolation_generique.__init__(self, *points, **styles)

    def _creer_figure(self):
        n = len(self.__points)
        couleur = self.style("couleur")
        niveau = self.style("niveau")
        style = self.style("style")
        epaisseur = self.style("epaisseur")
        if not self._representation:
            self._representation = [self.rendu.ligne() for i in xrange(n + 1)]

        self._xarray = array([])
        self._yarray = array([])

        if n < 2:
            return

        pas = self.__canvas__.pas()

        for i in xrange(n - 1):
            plot = self._representation[i]
            x1, y1 = self.__points[i].coordonnees
            x2, y2 = self.__points[i+1].coordonnees
            plot.set_data(array((x1, x2)), array((y1, y2)))
            plot.set(color=couleur, linestyle=style, linewidth=epaisseur)
            plot.zorder = niveau
            self._xarray = append(self._xarray, arange(x1, x2, pas))
            self._xarray = append(self._xarray, arange(x1, x2, pas))

        self._affiche_extremites()






class Interpolation_quadratique(Interpolation_generique):
    u"""Une interpolation quadratique.

    Interpolation des points donnés par une courbe polynomiale par morceaux, et de classe C1.
    Pour chaque morceau, x(t)=at²+bt+c et y(t)=dt²+et+f, où t appartient à [0;1].
    """
    points = __points = Arguments("Point_generique")
    debut = __fin = Argument("bool")
    fin = __debut = Argument("bool")

    def __init__(self, *points, **styles):
        if styles.get("points", None):
            points = styles.pop("points")
        debut = styles.pop("debut", True)
        fin = styles.pop("fin", True)
        self.__points = points = tuple(Ref(pt) for pt in points)
        self.__debut = debut = Ref(debut)
        self.__fin = fin = Ref(fin)
        Interpolation_generique.__init__(self, *points, **styles)


    def _creer_figure(self):
        n = len(self.__points)
        couleur = self.style("couleur")
        niveau = self.style("niveau")
        style = self.style("style")
        epaisseur = self.style("epaisseur")
        if not self._representation:
            self._representation = [self.rendu.ligne() for i in xrange(n + 1)]

        self._xarray = array([])
        self._yarray = array([])

        if n < 2:
            return

        pas = self.__canvas__.pas()
        t = fullrange(0, 1, pas)
        for i in xrange(n - 1):
            plot = self._representation[i]
            x0, y0 = self.__points[i].coordonnees
            x1, y1 = self.__points[i+1].coordonnees
            if i == 0:
                dx0, dy0 = x1 - x0, y1 - y0
            a, b, c = x1 - dx0 - x0, dx0, x0
            d, e, f = y1 - dy0 - y0, dy0, y0
            u = (a*t + b)*t + c
            v = (d*t + e)*t + f
            plot.set_data(u, v)
            plot.set(color=couleur, linestyle=style, linewidth=epaisseur)
            plot.zorder = niveau

            dx0 = 2*a + b
            dy0 = 2*d + e

            self._xarray = append(self._xarray, u)
            self._xarray = append(self._xarray, v)

        self._affiche_extremites(vec_fin = (dx0, dy0))






class Interpolation_cubique(Interpolation_generique):
    u"""Une interpolation cubique.

    Interpolation des points donnés par une courbe polynomiale par morceaux, de vecteur tangent horizontal aux sommets, et de classe C1 en général (ie. si x_n!=x_{n-1}).
    Pour chaque morceau, x(t)=at^3+bt^2+ct+d et y(t)=et^3+ft^2+gt+h, où t appartient à [0;1], et y'(0)=y'(1)=0.
    """

    points = __points = Arguments("Point_generique")
    debut = __fin = Argument("bool")
    fin = __debut = Argument("bool")
    courbure = __courbure = Argument("Variable_generique")

    def __init__(self, *points, **styles):
        if styles.get("points", None):
            points = styles.pop("points")
        debut = styles.pop("debut", True)
        fin = styles.pop("fin", True)
        courbure = styles.pop("courbure", 1)
        self.__points = points = tuple(Ref(pt) for pt in points)
        self.__debut = debut = Ref(debut)
        self.__fin = fin = Ref(fin)
        self.__courbure = courbure = Ref(fin)
        Interpolation_generique.__init__(self, *points, **styles)


    def _creer_figure(self):
        n = len(self.__points)
        couleur = self.style("couleur")
        niveau = self.style("niveau")
        style = self.style("style")
        epaisseur = self.style("epaisseur")
        if not self._representation:
            self._representation = [self.rendu.ligne() for i in xrange(n + 1)]

        self._xarray = array([])
        self._yarray = array([])

        if n < 2:
            return

        pas = self.__canvas__.pas()
        t = fullrange(0, 1, pas)
        for i in xrange(n - 1):
            plot = self._representation[i]
            x0, y0 = self.__points[i].coordonnees
            x1, y1 = self.__points[i+1].coordonnees
            if i == 0:
                dx0 = x1 - x0
                dy0 = y1 - y0
            else:
                dx0 = self.__courbure*abs(x1 - x0)
                if dx1 != 0:
                    dy0 = dy1/dx1*dx0
                else:
                    dx0 = dx1
                    dy0 = dy1
            if i < n - 2:
                x2, y2 = self.__points[i+2].coordonnees
                if cmp(y0, y1) == cmp(y1, y2):
                    dy1 = y2 - y0
                    dx1 = x2 - x0
                else:
                    dy1 = 0
                    dx1 = self.__courbure*abs(x1 - x0)
            else:
                dy1 = y1 - y0
                dx1 = x1 - x0
            a = 2*(x0 - x1) + dx0 + dx1
            b = 3*(x1 - x0) -2*dx0 - dx1
            c = dx0
            d = x0
            e = 2*(y0 - y1) + dy0 + dy1
            f = 3*(y1 - y0) -2*dy0 - dy1
            g = dy0
            h = y0
            u = ((a*t + b)*t + c)*t + d
            v = ((e*t + f)*t + g)*t + h
            plot.set_data(u, v)
            plot.set(color=couleur, linestyle=style, linewidth=epaisseur)
            plot.zorder = niveau

            self._xarray = append(self._xarray, u)
            self._xarray = append(self._xarray, v)

        self._affiche_extremites(vec_deb = (dx0, dy0), vec_fin = (dx1, dy1))
