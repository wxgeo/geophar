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

from itertools import izip,chain
from numpy import isnan, isinf, sign, arange, inf, append

from sympy import oo

from .objet import Objet, Argument, Ref
from .routines import distance_segment
from .. import param


def inf_or_nan(x):
    return isinf(x) or isnan(x)


class Courbe_generique(Objet):
    u"""Classe mère de toutes les courbes."""

    _affichage_depend_de_la_fenetre = True
    _style_defaut = param.courbes

    def __init__(self, **styles):
        Objet.__init__(self, **styles)

    def _distance_inf(self, x, y, d):
        if len(self.xarray) and len(self.yarray):
            u, v = self.__canvas__.coo2pix(self.xarray, self.yarray)
            u -= x
            v -= y
            m = min(u*u + v*v) # u*u est beaucoup plus rapide que u**2 (sic!)
            return m < d**2
        return False

    def _espace_vital(self):
        return (min(self.xarray), max(self.xarray), min(self.yarray), max(self.yarray))

    @property
    def xarray(self):
        if self._Objet__figure_perimee:
            self._creer_figure()
        return self._xarray

    @property
    def yarray(self):
        if self._Objet__figure_perimee:
            self._creer_figure()
        return self._yarray


class Courbe(Courbe_generique):
    u"""Courbe d'une fonction.

    L'expression doit être donnée en fonction de 'x'.
    Exemple : '2x^2-1/x+1'
    """
    _prefixe_nom = "C"
    __fonction = fonction = Argument("Fonction")

    def __init__(self, fonction, **styles):
        self.__fonction = fonction = Ref(fonction)
        Courbe_generique.__init__(self, **styles)

    def _creer_figure(self):
##        self.__canvas__.graph.supprimer(self._representation)
        self._representation = []
        fenetre = self.__canvas__.fenetre
        pas = self.__canvas__.pas()
        self._xarray = ()
        self._yarray = ()
        ancien_intervalle = None
#        derniere_valeur = None
#        derniere_fonction = None
#        ancien_x = None
#        ancien_y = None
        for fonction, union, e_cach in izip(self.__fonction._Fonction__fonctions,
                                                       self.__fonction._Fonction__unions,
                                                       self.__fonction.style('extremites_cachees')):
            for intervalle in union.intervalles:
                x = intervalle.asarray(fenetre[0], fenetre[1], pas)[0]
                if len(x):
#TODO: cas où len(x) == 1 (et donc, x[1] n'existe pas)
                    y = fonction(x)

                    x0 = x[0]
                    xN = x[-1]
                    y0 = y[0]
                    yN = y[-1]

                    # Bug de wxAgg pour des valeurs trop importantes, ou pour NaN
                    x, y = self.supprimer_valeurs_extremes(x, y, fonction)

                    self._representation.append(self.rendu.ligne(x, y,
                        couleur = self.style("couleur"),
                        linestyle = self.style("style"),
                        linewidth = self.style("epaisseur"),
                        zorder = self.style("niveau"),
                        ))
                    # _xarray et _yarray ne servent pas pour la représentation graphique,
                    # mais pour ._distance_inf() uniquement
                    self._xarray = append(self._xarray,  x)
                    self._yarray = append(self._yarray,  y)

                    inf = intervalle.inf
                    if fenetre[0] < inf < fenetre[1]:
                        if ancien_intervalle is None:
                            self._creer_debut_morceau(x, y, intervalle, e_cach)
                        else:
                            print intervalle, y[0], abs(y[0] - ancien_y[-1]), abs(x[0] - ancien_x[-1]), contexte['tolerance'] , pas
                            fusion = abs(x0 - ancien_xN) < contexte['tolerance'] \
                                    and (abs(y0 - ancien_yN) < contexte['tolerance']  or (isnan(y0) and isnan(ancien_yN)))
                            if fusion:
                                #Fusion
                                print 'Fusion', y0
                                if isnan(y0):
                                    print u'Fusion avancée'
                                    for i in xrange(10, 70, 10):
                                        try:
                                            val1 = ancienne_fonction(ancien_xN - 8**(-i))
                                            val2 = ancienne_fonction(x0 + 8**(-i))
                                            if abs(val1 - val2) < contexte['tolerance']:
                                                self._append_point(x0, val1, plein = False)
                                                break
                                        except (ZeroDivisionError, ValueError):
                                            print_error()
                                            fusion = False
                                            break
                                    else:
                                        fusion = False
                                elif not(ancien_intervalle.sup_inclus or intervalle.inf_inclus):
                                    print 'Fusion classique'
                                    self._append_point(x[0], y[0], plein = False)

                            if not fusion:
                                self._creer_fin_morceau(ancien_x, ancien_y, ancien_intervalle, e_cach)
                                self._creer_debut_morceau(x, y, intervalle, e_cach)

                    ancien_x = x
                    ancien_y = y
                    ancien_xN = xN
                    ancien_yN = yN
                    ancien_intervalle = intervalle
                    ancienne_fonction = fonction
        if ancien_intervalle is not None and fenetre[0] < ancien_intervalle.sup < fenetre[1]:
            self._creer_fin_morceau(ancien_x, ancien_y, ancien_intervalle, e_cach)

    def _creer_debut_morceau(self, x, y, intervalle, e_cach):
        if len(y) == 0:
            return
        elif len(y) == 1:
            if not inf_or_nan(y[0]):
                self._append_point(x[0], y[0])
            return
        if x[0] in e_cach:
            return
        if not(inf_or_nan(y[0]) or inf_or_nan(y[1])):
            if intervalle.inf_inclus:
                self._append_point(x[0], y[0])
            else:
                vec = x[1] - x[0],  y[1] - y[0]
                self._append_arc(x[0], y[0], vec)
# TODO: cas où len(y) < 3
        elif isnan(y[0]) and not (isnan(y[1]) or isnan(y[2])) :
              if not intervalle.inf_inclus:
                    vec = x[2] - x[1],  y[2] - y[1]
                    self._append_arc(x[1], y[1], vec)

    def _creer_fin_morceau(self, x, y, intervalle, e_cach):
        if len(y) <= 1:
            return
        if x[-1] in e_cach:
            return
        if not(inf_or_nan(y[-1]) or inf_or_nan(y[-2])):
            if intervalle.sup_inclus:
                self._append_point(x[-1], y[-1])
            else:
                vec = x[-2] - x[-1],  y[-2] - y[-1]
                self._append_arc(x[-1], y[-1], vec)
# TODO: cas où len(y) < 3
        elif isnan(y[-1]) and not (isnan(y[-2]) or isnan(y[-3])) :
              if not intervalle.inf_inclus:
                    vec = x[-3] - x[-2],  y[-3] - y[-2]
                    self._append_arc(x[-2], y[-2], vec)


    def _append_arc(self, x0, y0, vec):
        if self.style("extremites"):
            self._representation.append(self.rendu.arc(x0, y0, vec, color=self.style("couleur"), linewidth=self.style("epaisseur")))

    def _append_point(self, x0, y0, plein = True):
        if self.style("extremites"):
            self._representation.append(self.rendu.point(x0, y0, plein=plein, color=self.style("couleur"), markeredgewidth=self.style("epaisseur")))


    def _supprimer_valeurs_extremes(self, x, y, fonction, i, j):
        u"""Lorsque les valeurs aux bornes sont indéterminées (NaN), infinies (+/-Inf)
        ou très éloignées de zéro (2e200), on cherche à les convertir en une valeur
        raisonnable pour la fenêtre d'affichage.

        La principale difficulté est de déterminer **numériquement** la limite probable.

        On commence par regarder la valeur calculée par numpy à la borne considérée :

        * Si la valeur est +/-Inf, il faut étudier son signe.
          En effet, numpy ne peut généralement par faire la différence entre des calculs
          du type 1/0+ et 1/0- (ex: 1/(x-3) en 3+ et 3-).
          L'idée est la suivante : si les valeurs diminuent en se rapprochant de la borne,
          alors la limite est -Inf. De même, si elles augmentent, la limite est +Inf.
          On retourne alors une valeur en dehors de la fenêtre d'affichage, qui simule l'infini.

        * Si le résultat est nombre très éloigné de zéro, on le tronque tout en restant en
          dehors de la fenêtre d'affichage, de manière à simuler l'infini.
          En effet, le traceur de matplotlib réagit mal aux valeurs "extrêmes".

        * Enfin si le résultat est de type NaN, on s'éloigne légèrement (puis de plus en plus vite)
          de la borne, et on reitère, dans une limite de 20 itérations.
        """
        x0 = x[i]; y0 = y[i]
        x1 = x[j]; y1 = y[j]
        k = 2**arange(-20., 0.)
        entre = k*(x1 - x0) + x0 # (1 - k)*x0 + k*x1
        xk = chain([x0], entre, [x1])
        yk = chain([y0], fonction(entre), [y1])
        y_finis = [] # dernières valeurs finies
        infini = False
        xi_infini = None

        for xi, yi in izip(xk, yk):
            if infini:
                if not inf_or_nan(yi):
                    y_finis.append(yi)
                    if len(y_finis) == 2:
                        x0 = xi_infini
                        y0 = self._rogner_valeur(sign(y_finis[0] - y_finis[1])*inf)
                        break
            else:
                if isinf(yi):
                    infini = True
                    xi_infini = xi
                elif not isnan(yi):
                    x0 = xi
                    y0 = self._rogner_valeur(yi)
                    break
        x[i] = x0
        y[i] = y0
        return x, y


    def _rogner_valeur(self, y0):
        u"Remplace -inf et +inf par des valeurs numériques dépassant la fenêtre."
        if isnan(y0):
            return y0
        xmin, xmax, ymin, ymax = self.__feuille__.fenetre
        decalage = 100*(ymax - ymin)
        if isinf(y0):
            return (ymin - decalage) if (y0 < 0) else (ymax + decalage)
        # Bug de wxAgg pour des valeurs trop importantes
        return max(min(y0, ymax + decalage), ymin - decalage)
        # assert (ymin - decalage < y0 < ymax + decalage)


    def supprimer_valeurs_extremes(self, x, y, fonction):
            x, y = self._supprimer_valeurs_extremes(x, y, fonction, 0, 1)
            x, y = self._supprimer_valeurs_extremes(x, y, fonction, -1, -2)
            return x, y


    def _espace_vital(self):
        xmin = self.__fonction._Fonction__unions[0].intervalles[0].inf
        xmax = self.__fonction._Fonction__unions[-1].intervalles[-1].sup
        if xmin == -oo:
            xmin = None
        if xmax == oo:
            xmax = None
        return (xmin, xmax, min(self.yarray), max(self.yarray))


    def _distance_inf(self, x, y, d):
        P = x, y
        xm = self.__canvas__.pix2coo(x - d, y)[0]
        xM = self.__canvas__.pix2coo(x + d, y)[0]
        xarray = self.xarray
        filtre = (xm < xarray) & (xarray < xM)
        xa, ya = self.__canvas__.coo2pix(xarray[filtre], self.yarray[filtre])
        A = None
        for x, y in izip(xa, ya):
            B = A
            A = x, y
            if distance_segment(P, A, B, d):
                return True
        return False


    @staticmethod
    def _convertir(objet):
        u"Convertit un objet en fonction."
        return NotImplemented

    def _update(self, objet):
        if not isinstance(objet, Courbe):
            objet = self._convertir(objet)
        if isinstance(objet, Courbe):
            self.fonction = objet.fonction
        else:
            raise TypeError, "L'objet n'est pas une courbe."
