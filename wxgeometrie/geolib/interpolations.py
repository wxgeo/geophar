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
# en test ###############
from numpy import poly1d
from scipy.interpolate import PiecewisePolynomial
import fractions as frac
#########################
from .objet import Ref, Argument, Arguments

from .courbes import Courbe_generique
from .lignes import Tangente_courbe
from .contexte import contexte

from ..pylib import fullrange
from .. import param

class Interpolation_generique(Courbe_generique):
    u"""Classe mère de toutes les interpolations."""

    points = __points = Arguments("Point_generique")

    _style_defaut = param.interpolations

    def __init__(self, *points, **styles):
        self.__points = points = tuple(Ref(pt) for pt in points)
        Courbe_generique.__init__(self, **styles)


    def _affiche_extremites(self, vec_deb = None, vec_fin = None):
        couleur = self.style("couleur")
        niveau = self.style("niveau")
        epaisseur = self.style("epaisseur")
        debut = self.style("debut")
        fin = self.style("fin")

        # Début de la courbe
        plot = self._representation[-2]
        x, y = self.__points[0].coordonnees
        a, b = self.__points[1].coordonnees
        if vec_deb is None:
            vec_deb = (a - x, b - y)
        if debut is True:
            plot.set_data((x,), (y,))
            plot.set(visible=True, color=couleur, marker="o", markeredgecolor=couleur,
                     markersize=2*self.__canvas__.taille["o"], linewidth=epaisseur)
            plot.zorder = niveau
        elif debut is False:
            arc = self.rendu.arc(x, y, vec_deb)
            plot.set_data(*arc.get_data()) # À TESTER !!
            plot.set(visible=True, color=couleur, linewidth=epaisseur, marker="")
            plot.zorder = niveau
        else:
            plot.set_visible(False)

        # Fin de la courbe
        plot = self._representation[-1]
        x, y = self.__points[-1].coordonnees
        a, b = self.__points[-2].coordonnees
        if vec_fin is None:
            vec_fin = (a - x, b - y)
        if fin is True:
            plot.set_data((x,), (y,))
            plot.set(visible=True, color=couleur, marker="o", markeredgecolor=couleur,
                     markersize=2*self.__canvas__.taille["o"], linewidth=epaisseur)
            plot.zorder = niveau
        elif fin is False:
            arc = self.rendu.arc(x, y, vec_fin)
            plot.set_data(*arc.get_data()) # À TESTER !!
            plot.set(visible=True, color=couleur, linewidth=epaisseur, marker="")
            plot.zorder = niveau
        else:
            plot.set_visible(False)








class Interpolation_lineaire(Interpolation_generique):
    u"""Une interpolation linéaire.

    Interpolation entre les points donnés par des segments joints (courbe de classe C0).
    """

    points = __points = Arguments("Point_generique")

    def __init__(self, *points, **styles):
        if styles.get("points", None):
            points = styles.pop("points")
        self.__points = points = tuple(Ref(pt) for pt in points)
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
            # TODO: améliorer l'algo de détection (notamment si l'échelle
            # sur les 2 axes n'est pas la même).
            # Utiliser l'algorithme des segments.
            if abs(y2 - y1) < abs(x2 - x1):
                x_array = arange(x1, x2, pas if x1 < x2 else -pas)
                a = (y2 - y1)/(x2 - x1)
                b = y1 - a*x1
                y_array = a*x_array + b
            elif abs(y2 - y1) > contexte['tolerance']:
                y_array = arange(y1, y2, pas if y1 < y2 else -pas)
                a = (x2 - x1)/(y2 - y1)
                b = x1 - a*y1
                x_array = a*y_array + b
            else:
                continue
            self._xarray = append(self._xarray, x_array)
            self._yarray = append(self._yarray, y_array)

        self._affiche_extremites()






class Interpolation_quadratique(Interpolation_generique):
    u"""Une interpolation quadratique.

    Interpolation des points donnés par une courbe polynomiale par morceaux, et de classe C1.
    Pour chaque morceau, x(t)=at²+bt+c et y(t)=dt²+et+f, où t appartient à [0;1].
    """
    points = __points = Arguments("Point_generique")

    def __init__(self, *points, **styles):
        if "points" in styles:
            points = styles.pop("points")
        self.__points = points = tuple(Ref(pt) for pt in points)
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
            self._yarray = append(self._yarray, v)

        self._affiche_extremites(vec_fin = (dx0, dy0))






class Interpolation_cubique(Interpolation_generique):
    u"""Une interpolation cubique.

    Interpolation des points donnés par une courbe polynomiale par morceaux, de vecteur tangent horizontal aux sommets, et de classe C1 en général (ie. si x_n!=x_{n-1}).
    Pour chaque morceau, x(t)=at^3+bt^2+ct+d et y(t)=et^3+ft^2+gt+h, où t appartient à [0;1], et y'(0)=y'(1)=0.
    """

    points = __points = Arguments("Point_generique")

    def __init__(self, *points, **styles):
        if "points" in styles:
            points = styles.pop("points")
        self.__points = points = tuple(Ref(pt) for pt in points)
        Interpolation_generique.__init__(self, *points, **styles)


    def _creer_figure(self):
        n = len(self.__points)
        couleur = self.style("couleur")
        niveau = self.style("niveau")
        style = self.style("style")
        epaisseur = self.style("epaisseur")
        courbure = self.style("courbure")
        if courbure is None:
            courbure = 1
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
                dx0 = courbure*abs(x1 - x0)
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
                    dx1 = courbure*abs(x1 - x0)
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
            self._yarray = append(self._yarray, v)

        self._affiche_extremites(vec_deb = (dx0, dy0), vec_fin = (dx1, dy1))


class interpol1():
    u"""
    Classe d'interpolation. Elle contient la liste des x, y et nombre dérivé ain\
    si que la fonction d'interpolation.
    @param self.interpol: La fonction d'interpolation
    @type self.interpol: numpy.lib.polynomial
    @param self.tangentes: liste des droites tangentes
    @type self.tangentes: list of numpy.lib.polynomial
    """
    
    def __init__(self, xl = [], yl = [], derivl = []):
        self.xl = xl
        self.yl = yl
        self.derivl = [frac.Fraction(x) for x in derivl]
        self.tangentes = []
        self.interpol = self.poly_inter(xl, yl, derivl)
        for i in range(len(xl)):
            self.tangentes.append(poly1d([derivl[i], -1*derivl[i]*xl[i]+yl[i]]))


    def __call__(self, t):
        u"""
        calcule l'image de t par la fonction d'interpolation.
        @type t: float or array of float etc..
        """
        return self.interpol(t)


    def poly_inter(self, xl, yl, derivl):
        u"""
        create the interpolation function: passing through points of (xl, yl)
        and with derivate in derivl at xl abscisses.
        
        @type xl: list
        @param xl: abscisses list
        @type yl: list
        @param yl: ord list
        @type derivl: list
        @param derivl: value of the derivate at each point
        
        @return : numpy.lib.polynomial
        """
        # two lists of polynoms: the Lagrange interpolation ones
        # and the local construction ones before product
        inter = []
        local = []
        for x in xl:
            i = xl.index(x)
            yi, di = yl[i], derivl[i]
            xl.remove(x)
            # poly1d True: for definition by roots
            # squared for transparency up to derivation
            p = poly1d(xl, True)**2
            p_der = p.deriv()
            inter.append(p)
            li = p_der(float(x))/p(float(x))
            gi = di - yi * li
            # compute the local fun. coef made to match the interpolation
            local.append(poly1d([gi, yi - gi * x]))
            # reverse xl to its initial value
            xl.insert(i, x)
        f = [local[i] * inter[i] / inter[i](float(xl[i]))  for i in range(len(xl))]
        return sum(f)


    def list_tangentes(self):
        u"""
        renvoie la liste des équations réduites des tangentes au format tex

        @return: string
        """
        out = u''
        for i in range(len(self.xl)):
            out += "$"+droite2eqn(self.xl[i], self.yl[i], self.derivl[i], name="d_"+str(i+1))+"$\\\\"
            out += '\n'
        return out

    def plot_all(self, color='b', xstep = 0.5, ystep = 0.5, plain_tan=False):
        u"""
        Trace la fonction ainsi que les tangentes (droites ou flèches).
        @param color: couleur des tangentes
        @type color: char
        @param xstep: le pas de la grille en x
        @type xstep: float
        @param ystep: le pas de la grille en y
        @type ystep: float
        @param plain_tan: détermine si on trace des droites (True) ou des \ 
        flèches (False) pour les tangentes.
        @type plain_tan: boolean
        @return: None
        """
        num_points = 200
        delta_x = self.xl[-1] - self.xl[0]
        my = min(self.yl)
        My = max(self.yl)
        delta_y = My - my
        x_bound = [ self.xl[0]-0.3*delta_x,  self.xl[-1]+0.3*delta_x]
        y_bound = [my-0.1*delta_y, My+0.1*delta_y]
        t = arange(self.xl[0]-0.3*delta_x, self.xl[-1]+0.3*delta_x, 1.6*delta_x/num_points)
        #courbe
        plot(t, self.interpol(t), color)
        #points de passage
        for i in range(len(self.xl)):
            plot(self.xl[i], self.yl[i], 'go')
        #tangentes
        if plain_tan: # droites completes
            for d in self.tangentes:
                plot(t, d(t),'k')
        else:
        #juste des fleches - A AMELIORER
            arrow_params = {'head_width': 0.1, 'head_starts_at_zero':True, 'shape': 'full'}
            for i in range(len(self.xl)):
                arrow(self.xl[i], self.yl[i], xstep*self.derivl[i].denominator*1.1,\
                          ystep*self.derivl[i].numerator*1.1, **arrow_params)
                arrow(self.xl[i], self.yl[i], -xstep*self.derivl[i].denominator*1.1,\
                          -ystep*self.derivl[i].numerator*1.1, **arrow_params)
        #grille
        bgrid([ math.floor(x_bound[0]/ xstep) * xstep, x_bound[1]], [math.floor(y_bound[0]/ystep)*ystep, y_bound[1]],\
                    xstep, ystep, 'k:')
        xlim(tuple(x_bound))
        ylim(tuple(y_bound))
        show()


class Interpolation_polynomiale_par_morceau(Interpolation_generique, interpol1):
    u"""Une courbe d'interpolation polynomiale par morceaux.
    Elle utilise l'interpolation par morceau de scipy pour construire la fonction
    c'est la classe scipy.interpolate.PiecewisePolynomial

    elle passe par les points (xl, yl) et avec le nombre derive dans derivl a 
    l'abs xl abscisses.

    exemple::

    >>>A = Point(-1,-2)
    >>>B = Point(2,1)
    >>>C = Point(8,-3)
    >>>d = Interpolation_polynomiale_par_morceau(A,B,C, derivees=[-1,0.5,2])
    
    @type xl: list
    @param xl: abscisses list
    @type yl: list
    @param yl: ord list
    @type derivl: list
    @param derivl: value of the derivate at each point
    
    @return : numpy.lib.polynomial
    """
    points = __points = Arguments("Point_generique")

    def __init__(self, *points, **styles): #, derivl = []
        self.__derivees = derivees = styles.pop('derivees', len(points)*[0])
        debut = styles.pop("debut", True)
        fin = styles.pop("fin", True)
        if styles.get("points", None):
            points = styles.pop("points")
        self.__points = points = tuple(Ref(pt) for pt in points)
        # en test: creation des tangentes: dictionnaire
        # key: nom du point, value: objet Tangente_courbe
        self.__tangentes = []
        # boucle avec ruse enumerate 
        # cf http://docs.python.org/tutorial/datastructures.html#dictionaries
        for i, P in enumerate(points):
            dico = {'point': P, 'cdir': self.__derivees[i]}
            self.__tangentes.append(Tangente_courbe(**dico))
 
        self.__debut = debut = Ref(debut)
        self.__fin = fin = Ref(fin)
        Interpolation_generique.__init__(self, *points, **styles)

    def poly_inter(self, xl, yl, derivl):
        yl_cum = [[yl[i], derivl[i]] for i in range(len(yl))]
        return PiecewisePolynomial(xl, yl_cum)


    def _creer_figure(self):
        n = len(self.__points)
        couleur = self.style("couleur")
        niveau = self.style("niveau")
        style = self.style("style")
        epaisseur = self.style("epaisseur")
        if not self._representation:
            self._representation = [self.rendu.ligne()]

        if n < 2:
            return
        #interpol doit être recalculé à chaque mise à jour
        self.xl = [P[0] for P in self.__points]
        self.yl = [P[1] for P in self.__points]
        self.interpol = self.poly_inter(self.xl, self.yl, self.__derivees)
        # de même les tangentes sont recalculées
        # il doit y avoir moyen de faire moins de calculs
        self.__tangentes = []
        for i in range(len(self.__points)):
            self.__tangentes.append(Tangente_courbe(point = self.__points[i],\
                                                        cdir = self.__derivees[i]))
            #self.__tangentes[i]._creer_figure()
 
        
        pas = self.__canvas__.pas()
        plot = self._representation[0]
        x1, y1 = self.__points[0].coordonnees
        x2, y2 = self.__points[-1].coordonnees
        xarray = arange(x1, x2, pas)
        yarray = self.interpol(xarray)
        plot.set_data(xarray, yarray)
        plot.set(color=couleur, linestyle=style, linewidth=epaisseur)
        plot.zorder = niveau
        self._xarray = xarray
        self._yarray = yarray
        
        #self._affiche_extremites()
