# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                   Cercles                   #
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

from random import uniform
from math import sin, cos, pi, hypot, sqrt
from cmath import phase, rect

from numpy import arange, cos as ncos, sin as nsin

from sympy import pi as PI

from .angles import Angle_vectoriel
from .labels import Label_cercle, Label_arc_cercle
from .lignes import Segment
from .objet import Objet, Objet_avec_equation, Ref, Argument, issympy, contexte, \
                   pi_, FILL_STYLES, TYPES_REELS, G
from .points import Point, Milieu, Centre, Point_generique, Point_equidistant, Glisseur_cercle
from .routines import nice_display, angle_vectoriel, distance, formatage, trigshift, \
                      carre_distance_point_ellipse, vect
from .variables import Mul, Rayon
from .vecteurs import Vecteur
from .. import param
from ..pylib import fullrange



##########################################################################################




# Cercles


class Cercle_Arc_generique(Objet_avec_equation):
    u"""La classe mère de tous les cercles et arcs de cercles."""

    _affichage_depend_de_la_fenetre = True
    _enregistrer_sur_la_feuille_par_defaut = True
    # à cause du codage des longueurs (arcs), et du nombre de points variable des cercles

    centre = __centre = Argument("Point_generique")

    def __init__(self, centre, **styles):
        self.__centre = centre = Ref(centre)
        Objet.__init__(self, **styles)

    def _get_equation(self):
        u"""Retourne un triplet (a,b,c) tel que x**2 + y**2 + ax + by + c = 0
        soit une équation du cercle."""
        xO, yO = self.__centre.coordonnees
        r = self.rayon
        return (-2*xO, -2*yO, xO**2 + yO**2 - r**2)


    @property
    def rayon(self):
        raise NotImplementedError

    @property
    def diametre(self):
        return 2*self.rayon

    def _distance_inf(self, x, y, d): # à surclasser pour les arcs
        x0, y0 = self._pixel(self.__centre)
        rx, ry = self.__canvas__.dcoo2pix(self.rayon, self.rayon)
        rx = abs(rx) ; ry = abs(ry)
        if x0 - rx - d < x < x0 + rx + d and y0 - ry - d < y < y0 + ry + d:
            return carre_distance_point_ellipse((x0, y0), rx, ry, (x, y), epsilon = .000001) < d**2
        return False





class Arc_generique(Cercle_Arc_generique):
    u"""La classe mère de tous les arcs de cercles."""

    _style_defaut = param.arcs
    _prefixe_nom = "a"
    _affichage_depend_de_la_fenetre = True # codage

    centre = __centre = Argument("Point_generique")
    point = __point = Argument("Point_generique")

    def __init__(self, centre, point, **styles):
        self.__centre = centre = Ref(centre)
        self.__point = point = Ref(point)
        Cercle_Arc_generique.__init__(self, centre, **styles)
        self.etiquette = Label_arc_cercle(self)



##    @property
##    def centre(self):
##        return self.__centre

    @property
    def rayon(self):
        try:
            return distance(self.__centre, self.__point)
        except TypeError:
            return 0



    @property
    def equation_formatee(self):
        u"Equation sous forme lisible par l'utilisateur."
        eq = self.equation
        if eq is None:
            return u"L'objet n'est pas défini."
        a, b, c = (nice_display(coeff) for coeff in eq)
        # on ne garde que quelques chiffres après la virgule pour l'affichage
        xmin, xmax, ymin, ymax = (nice_display(extremum) for extremum in self._espace_vital())
        return formatage(u"x² + y² + %s x + %s y + %s = 0 avec %s<x<%s et %s<y<%s" %(a, b, c, xmin, xmax, ymin, ymax))

    #~ def _distance_inf(self, x, y, d):
        #~ x0, y0 = self._pixel(self.__centre)
        #~ a, b = self._intervalle()
        #~ t = arange(a, b, .003)
        #~ rx, ry = self.__canvas__.dcoo2pix(self.rayon, self.rayon)
        #~ u = x - x0 - rx*ncos(t)
        #~ v = y - y0 - ry*nsin(t)
        #~ m = min(u*u + v*v) # u*u est beaucoup plus rapide que u**2 (sic!)
        #~ return m < d**2


    def _distance_inf(self, x, y, d):
        # On travaille avec les coordonnées de la feuille
        a, b = self._intervalle()
        z0 = self.__centre.z
        xM, yM = self.__canvas__.pix2coo(x, y)
        zM = xM + 1j*yM
        if abs(zM - z0) > 10*contexte['tolerance']:
            phi = phase(zM - z0)
            if not (a <= trigshift(phi, a) <= b):
                # on est au niveau de "l'ouverture" de l'arc
                # NB: le code n'est pas parfait ; en particulier, si le repère n'est pas orthonormal,
                # et que l'ellipse qui porte le cercle est *très* allongée,
                # le calcul de distance est passablement faux à *l'intérieur* de l'ellipse
                zA = z0 + rect(self.rayon, a)
                zB = z0 + rect(self.rayon, b)
                # On travaille maintenant avec les coordonnées en pixel
                _xA, _yA = self.__canvas__.coo2pix(zA.real, zA.imag)
                _xB, _yB = self.__canvas__.coo2pix(zB.real, zB.imag)
                return min((_xA - x)**2 + (_yA - y)**2, (_xB - x)**2 + (_yB - y)**2) < d**2
        return Cercle_Arc_generique._distance_inf(self, x, y, d)


    def _intervalle(self):
        u"Renvoie deux nombres a < b. L'arc est l'ensemble des points (r*cos(t), r*sin(t)) pour t apartenant à [a, b]."
        raise NotImplementedError

    def _sens(self):
        return 1

    def _longueur(self):
        a, b = self._intervalle()
        return (b - a)*self.rayon

    @property
    def longueur(self):
        try:
            return self._longueur()
        except TypeError:
            return 0

    @property
    def extremites(self):
        u"Extrémités de l'arc."
        raise NotImplementedError

    @property
    def info(self):
        return self.nom_complet + u' de longueur ' + nice_display(self.longueur)


    def _t(self):
        u, v = self._intervalle()
        x, y = self.__centre.coordonnees
        xmin, xmax, ymin, ymax = self.__feuille__.fenetre
        w = 3*(xmax - xmin)
        h = 3*(ymax - ymin)
        if xmin - w < x < xmax + w and ymin - h < y < ymax + h:
            return [fullrange(u, v, self.__canvas__.pas())]
        else:
            # Optimisation dans le cas où le centre est très loin de la fenêtre.
            A = xmin + 1j*ymin
            B = xmax + 1j*ymin
            C = xmax + 1j*ymax
            D = xmin + 1j*ymax
            O = x + 1j*y
            a = phase(A - O)
            b = phase(B - O)
            c = phase(C - O)
            d = phase(D - O)
            if x >= xmax and ymin <= y <= ymax:
                assert (a <= 0 and b <= 0 and c >= 0 and d >= 0)
                a += 2*pi
                b += 2*pi
            # On récupère la portion du cercle à afficher :
            a, b = min(a, b, c, d), max(a, b, c, d)
            # Maintenant, il faut trouver l'intersection entre cette portion de cercle, et l'arc.
            # On s'arrange pour que a appartienne à l'intervalle [u; u + 2pi[ :
            k = trigshift(a, u) - a
            a += k
            b += k
            # L'intersection est constituée d'un ou deux morceaux
            intersection = []
            if a < v:
                c = min(b, v)
                print a, c
                intersection.append(fullrange(a, c, self.__canvas__.pas()))
            u += 2*pi
            v += 2*pi
            if b > u:
                c = min(b, v)
                intersection.append(fullrange(u, c, self.__canvas__.pas()))
            return intersection



    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.ligne(), self.rendu.ligne(), self.rendu.codage()]
            # 2 lignes pour afficher l'arc lui-même

        for plot in self._representation[1:]:
            plot.set_visible(False)

        x, y = self._Arc_generique__centre.coordonnees
        r = self.rayon
        niveau, couleur, style, epaisseur = self.style(('niveau', 'couleur', 'style', 'epaisseur'))

        for i, t in enumerate(self._t()):
            plot = self._representation[i]
            plot.set_data(x + r*ncos(t), y + r*nsin(t))
            plot.set(color=couleur, linestyle=style, linewidth=epaisseur, zorder=niveau, visible=True)

        # Gestion du codage des arcs de cercle (utilisé pour indiquer les arcs de cercles de même longeur)
        if self.style("codage"):
            a, b = self._intervalle()
            c = .5*(a + b)
            x0 = x + r*cos(c)
            y0 = y + r*sin(c)
            self._representation[2].set(visible=True, style=self.style('codage'),
                       position=(x0, y0),
                       direction=(y0 - y, x - x0), # vecteur orthogonal au rayon
                       taille=param.codage["taille"], angle=param.codage["angle"],
                       color=couleur, linewidth=epaisseur,
                       zorder=niveau + 0.01,
                      )


    def _espace_vital(self):
        x0, y0 = self.__centre.coordonnees
        a, b = self._intervalle()
        t = arange(a, b, .003)
        r = self.rayon
        u = x0 + r*ncos(t)
        v = y0 + r*nsin(t)
        return min(u), max(u), min(v), max(v)


    def _contains(self, M):
        O = self.__centre
        a, b = self._intervalle()
        vec = vect(O, M)
        if hypot(*vec) < contexte['tolerance']: # M et O sont (quasi) confondus
            return self.rayon < contexte['tolerance'] # alors M appartient (quasiment) à l'arc ssi l'arc est de rayon (quasi) nul
        else:
            c = angle_vectoriel(G.vecteur_unite, vec)
            if c < a:
                c += 2*pi
    #        print "Test tolerance arc cercle",  abs(distance(O, M) - self.rayon),  a < c < b
            return abs(distance(O, M) - self.rayon) < contexte['tolerance'] and a - contexte['tolerance'] < c < b + contexte['tolerance']






class Arc_cercle(Arc_generique):
    u"""Un arc de cercle.

    Un arc de cercle orienté, défini par son centre et ses extremités(*), dans le sens direct.

    (*) note : le troisième point n'appartient pas forcément à l'arc de cercle, mais sert à en délimiter l'angle au centre."""


    centre = __centre = Argument("Point_generique", defaut = Point)
    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)

    def __init__(self, centre = None, point1 = None, point2 = None, **styles):
        self.__centre = centre = Ref(centre)
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        Arc_generique.__init__(self, centre,  point1, **styles)
        self._angle1 = Angle_vectoriel(G.vecteur_unite, Vecteur(centre, point1))
        self._angle2 = Angle_vectoriel(G.vecteur_unite, Vecteur(centre, point2))

    def image_par(self, transformation):
        return Arc_cercle(self.__centre.image_par(transformation), self.__point1.image_par(transformation), self.__point2.image_par(transformation))

    def _intervalle(self):
        a = self._angle1.valeur
        b = self._angle2.valeur
        if b < a:
            b += 2*(PI if issympy(b) else pi)
        return a, b

    @property
    def extremites(self):
        return self.__point1, self.__point2







class Arc_points(Arc_generique):
    u"""Un arc défini par 3 points.

    Un arc de cercle, défini par ses extrémités, et un autre point."""


    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    point3 = __point3 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, point3 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__point3 = point3 = Ref(point3)
        Arc_generique.__init__(self, Point_equidistant(point1, point2, point3), point1, **styles)
        centre = self._Arc_generique__centre
        self._angle1 = Angle_vectoriel(G.vecteur_unite, Vecteur(centre, point1))
        self._angle2 = Angle_vectoriel(G.vecteur_unite, Vecteur(centre, point2))
        self._angle3 = Angle_vectoriel(G.vecteur_unite, Vecteur(centre, point3))


    def image_par(self, transformation):
        return Arc_points(self.__point1.image_par(transformation), self.__point2.image_par(transformation), self.__point3.image_par(transformation))

    def _intervalle(self):
        # mesure des angles dans ]-pi;pi]
        a = self._angle1.valeur
        b = self._angle2.valeur
        c = self._angle3.valeur
        if b < a:
            b += 2*(PI if issympy(b) else pi)
        if c < a:
            c += 2*(PI if issympy(c) else pi)
        if b < c:
            return a, c
        return c, a + 2*(PI if issympy(a) else pi)

    def _sens(self):
        u"Sens de parcours de l'arc : direct (1) ou indirect (-1)"
        # mesure des angles dans ]-pi;pi]
        a = float(self._angle1)
        b = float(self._angle2)
        c = float(self._angle3)
        if b < a:
            b += 2*pi
        if c < a:
            c += 2*pi
        if b < c:
            return 1
        return -1


    def _conditions_existence(self):
        return self._Arc_generique__centre.existe

    @property
    def extremites(self):
        return self.__point1, self.__point3



class Arc_oriente(Arc_points):
    u"""Un arc de cercle orienté.

    Un arc de cercle orienté, défini par ses extrémités, et un autre point."""

    _style_defaut = param.arcs_orientes

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    point3 = __point3 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, point3 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__point3 = point3 = Ref(point3)
        # on ne peut pas utiliser le mot-clef "defaut", car le style par défaut est déjà défini (param.arcs)
        Arc_points.__init__(self, point1, point2, point3, **styles)

    def image_par(self, transformation):
        return Arc_oriente(self.__point1.image_par(transformation), self.__point2.image_par(transformation), self.__point3.image_par(transformation))

    @property
    def sens(self):
        if self._sens() is 1:
            return "direct"
        return "indirect"

    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.fleche_courbe()]
        fleche = self._representation[0]

        fleche.set(centre=self._Arc_generique__centre.coordonnees, rayon=self.rayon,
                   intervalle = self._intervalle(), position=self.style("position"),
                   double=self.style("double_fleche"), taille=self.style("taille"),
                   angle=self.style("angle"), zorder=self.style("niveau"),
                   color=self.style("couleur"), linewidth = self.style("epaisseur"),
                   linestyle = self.style("style"), sens=self._sens(),
                   )




class Demicercle(Arc_cercle):
    u"""Un demi-cercle.

    Un demi-cercle orienté, défini par ses extrémités, dans le sens direct."""


    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        Arc_cercle.__init__(self, Milieu(point1, point2), point1, point2, **styles)





class Cercle_generique(Cercle_Arc_generique):
    u"""Un cercle générique.

    Usage interne : la classe mère pour tous les types de cercles."""

    _style_defaut = param.cercles
    _prefixe_nom = "c"

    centre = __centre = Argument("Point_generique")

    def __init__(self, centre, **styles):
        self.__centre = centre = Ref(centre)
        Cercle_Arc_generique.__init__(self, centre, **styles)
        self.etiquette = Label_cercle(self)


    def _t(self):
        x, y = self.__centre.coordonnees
        xmin, xmax, ymin, ymax = self.__feuille__.fenetre
        w = 3*(xmax - xmin)
        h = 3*(ymax - ymin)
        if xmin - w < x < xmax + w and ymin - h < y < ymax + h:
            return fullrange(0, 2*pi, self.__canvas__.pas())
        else:
            # Optimisation dans le cas où le centre est très loin de la fenêtre.
            A = xmin + 1j*ymin
            B = xmax + 1j*ymin
            C = xmax + 1j*ymax
            D = xmin + 1j*ymax
            O = x + 1j*y
            a = phase(A - O)
            b = phase(B - O)
            c = phase(C - O)
            d = phase(D - O)
            if x >= xmax and ymin <= y <= ymax:
                assert (a <= 0 and b <= 0 and c >= 0 and d >= 0)
                a += 2*pi
                b += 2*pi
            return arange(min(a, b, c, d), max(a, b, c, d), self.__canvas__.pas())


    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.ligne()]

        plot = self._representation[0]
        x, y = self.__centre.coordonnees
        r = self.rayon
        t = self._t()
        plot.set_data(x + r*ncos(t), y + r*nsin(t))
        plot.set(color=self.style("couleur"), linestyle = self.style("style"),
                 linewidth=self.style("epaisseur"))
        plot.zorder = self.style("niveau")


    def _longueur(self):
        rayon = self.rayon
        return 2*rayon*pi_()

    perimetre = property(_longueur)


    def _contains(self, M):
        O = self.__centre
        return abs(distance(O, M) - self.rayon) < contexte['tolerance']


    def _espace_vital(self):
        x, y = self.__centre.coordonnees
        r = self.rayon
        return (x - r, x + r, y - r, y + r)


    @property
    def equation_formatee(self):
        u"Equation sous forme lisible par l'utilisateur."
        eq = self.equation
        if eq is None:
            return u"L'objet n'est pas défini."
        a, b, c = (nice_display(coeff) for coeff in eq)
        # on ne garde que quelques chiffres après la virgule pour l'affichage
        return formatage(u"x² + y² + %s x + %s y + %s = 0" %(a, b, c))


    def _creer_nom_latex(self):
        u"""Crée le nom formaté en LaTeX. Ex: M1 -> $M_1$."""
        Objet._creer_nom_latex(self)
        nom = self.latex_police_cursive(self.nom_latex[1:-1])
        self.nom_latex = "$" + nom + "$"

    @property
    def info(self):
        return self.nom_complet + u' de rayon ' + nice_display(self.rayon)






class Cercle_rayon(Cercle_generique):
    u"""Un cercle de rayon fixé.

    Un cercle défini par son centre et son rayon."""


    centre = __centre = Argument("Point_generique", defaut = Point)
    rayon = __rayon = Argument("Variable_generique", defaut = 1)

    def __init__(self, centre = None, rayon = None, **styles):
        self.__centre = centre = Ref(centre)
        self.__rayon = rayon = Ref(rayon)
        Cercle_generique.__init__(self, centre, **styles)

    def image_par(self, transformation):
        from transformations import Homothetie, Rotation, Translation, Reflexion
        if isinstance(transformation, Homothetie):
            return Cercle_rayon(self.__centre.image_par(transformation), Mul(Rayon(self), transformation.rapport))
        elif isinstance(transformation, (Rotation, Translation, Reflexion)):
            return Cercle_rayon(self.__centre.image_par(transformation), Rayon(self))
        raise NotImplementedError
        #return Cercle(self.__centre.image_par(transformation), Glisseur_cercle(self).image_par(transformation))

    def _conditions_existence(self):
        return self.__rayon >= 0

    def _set_feuille(self):
        if "_Cercle__rayon" in self._valeurs_par_defaut:
            xmin, xmax, ymin, ymax = self.__feuille__.fenetre
            self.__rayon = .5*uniform(0, min(abs(xmin - xmax), abs(ymin - ymax)))
#            self._valeurs_par_defaut.discard("_Cercle__rayon")
        if "_Cercle__centre" in self._valeurs_par_defaut:
            xmin, xmax, ymin, ymax = self.__feuille__.fenetre
            r = self.__rayon
            self.__centre.coordonnees = uniform(xmin + r, xmax - r), uniform(ymin + r, ymax - r)
#            self._valeurs_par_defaut.discard("_Cercle__centre")
        Objet._set_feuille(self)



class Cercle(Cercle_generique):
    u"""Un cercle.

    Un cercle défini par son centre et un point du cercle."""

    centre = __centre = Argument("Point_generique", defaut = Point)
    point = __point = Argument("Point_generique", defaut = Point)

    def __new__(cls, *args, **kw):
        if len(args) == 1 and isinstance(args[0], basestring):
            newclass = Cercle_equation
        elif len(args) == 1 and isinstance(args[0], Segment):
            newclass = Cercle_diametre
        elif len(args) == 2 and (isinstance(args[1], TYPES_REELS)
                                or isinstance(args[1], basestring)):
            newclass = Cercle_rayon
        elif len(args) == 3 and isinstance(args[0], Point_generique) \
                                      and isinstance(args[1], Point_generique) \
                                      and isinstance(args[2], Point_generique):
            newclass = Cercle_points
        else:
            return object.__new__(cls)
        objet = newclass.__new__(newclass, *args, **kw)
        objet.__init__(*args, **kw)
        return objet

    def __init__(self, centre = None, point = None, **styles):
        self.__centre = centre = Ref(centre)
        self.__point = point = Ref(point)
        Cercle_generique.__init__(self, centre, **styles)

    @property
    def rayon(self):
        return distance(self.__centre, self.__point)


    def image_par(self, transformation):
        return Cercle(self.__centre.image_par(transformation), self.__point.image_par(transformation))




class Cercle_diametre(Cercle_generique):
    u"""Un cercle défini par un diamètre.

    Un cercle défini par un diamètre [AB]."""

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, **styles):
        if isinstance(point1, Segment) and point2 is None:
            point2 = point1.point2
            point1 = point1.point1
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        Cercle_generique.__init__(self, Milieu(point1, point2), **styles)

    @property
    def rayon(self):
        return distance(self._Cercle_generique__centre, self.__point1)

    def image_par(self, transformation):
        return Cercle_diametre(self.__point1.image_par(transformation), self.__point2.image_par(transformation))





class Cercle_points(Cercle_generique):
    u"""Un cercle défini par 3 points.

    Un cercle défini par la donnée de 3 points du cercle."""

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    point3 = __point3 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, point3 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__point3 = point3 = Ref(point3)
        Cercle_generique.__init__(self, Point_equidistant(point1, point2, point3), **styles)

    @property
    def rayon(self):
        try:
            return distance(self._Cercle_generique__centre, self.__point1)
        except TypeError:
            return 0

    def _conditions_existence(self):
        return self._Cercle_generique__centre.existe

    def image_par(self, transformation):
        return Cercle_points(self.__point1.image_par(transformation), self.__point2.image_par(transformation), self.__point3.image_par(transformation))






class Cercle_equation(Cercle_generique):
    u"""Un cercle défini par une équation.

    Un cercle d'équation donnée sous forme d'un triplet (a, b, c). (x**2 + y**2 + ax + by + c = 0)"""

    a = __a = Argument("Variable_generique")
    b = __b = Argument("Variable_generique")
    c = __c = Argument("Variable_generique")

    def __init__(self, a = 0, b = 0, c = -1, **styles):
        self.__a = a = Ref(a)
        self.__b = b = Ref(b)
        self.__c = c = Ref(c)
        Objet.__init__(self) # pour pouvoir utiliser 'Centre(self)', l'objet doit déjà être initialisé
        Cercle_generique.__init__(self, Centre(self), **styles)



    @property
    def rayon(self):
        return sqrt((self.__a**2 + self.__b**2)/4 - self.__c)


    def _get_equation(self):
        u"Retourne un triplet (a, b, c), tel que x**2 + y**2 + ax + by + c = 0 soit une équation du cercle."
        return self.__a, self.__b, self.__c

    def _set_equation(self, a = None, b = 0, c = -1):
        if a is not None:
            self.__a = a
            self.__b = b
            self.__c = c

    def _conditions_existence(self):
        return self.__a**2 + self.__b**2 - 4*self.__c >= 0

##    def a(self, valeur = None):
##        return self.__a(valeur)
##
##    a = property(a,  a)
##
##    def b(self, valeur = None):
##        return self.__b(valeur)
##
##    b = property(b,  b)
##
##    def c(self, valeur = None):
##        return self.__c(valeur)
##
##    c = property(c,  c)

    def image_par(self, transformation):
        return Cercle_rayon(Centre(self).image_par(transformation), Glisseur_cercle(self).image_par(transformation))




class Disque(Cercle_generique):
    u"""Un disque.

    Un disque défini par le cercle le délimitant."""

    _style_defaut = param.polygones
    _prefixe_nom = "d"

    cercle = __cercle = Argument("Cercle_generique", defaut = Cercle)

    def __init__(self, cercle = None, **styles):
        self.__cercle = cercle = Ref(cercle)
        Cercle_generique.__init__(self, Centre(cercle), **styles)

    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.polygone()]

        fill = self._representation[0]
        x, y = self._Cercle_generique__centre.coordonnees
        r = self.rayon
        t = fullrange(0, 2*pi , self.__canvas__.pas())
        fill.xy = zip(x + r*ncos(t), y + r*nsin(t))
        fill._alpha = self.style("alpha")
        fill._color = self.style("couleur")
        fill._linestyle = FILL_STYLES.get(self.style("style"), "solid")
        fill._linewidth = self.style("epaisseur")
        fill.zorder = self.style("niveau")


    @property
    def rayon(self):
        return self.__cercle.rayon

    def _distance_inf(self, x, y, d):
        x, y = self.__canvas__.pix2coo(x, y)
        return distance(self._Cercle_generique__centre, (x, y)) <= self.rayon

    def _contains(self, M):
        return distance(self._Cercle_generique__centre, M) - self.rayon <= contexte['tolerance']

    @property
    def aire(self):
        return self.rayon**2*pi_()

    @property
    def info(self):
        return self.nom_complet + u" d'aire " + nice_display(self.aire)


    @property
    def equation_formatee(self):
        u"Equation sous forme lisible par l'utilisateur."
        eq = self.equation
        if eq is None:
            return u"L'objet n'est pas défini."
        a, b, c = (nice_display(coeff) for coeff in eq)  # on ne garde que quelques chiffres après la virgule pour l'affichage
        return formatage(u"x² + y² + %s x + %s y + %s <= 0" %(a, b, c))

    def image_par(self, transformation):
        return Disque(self.__cercle.image_par(transformation))
