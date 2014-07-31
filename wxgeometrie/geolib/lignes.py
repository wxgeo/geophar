# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                   Objets                    #
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

import re
from random import uniform
from math import pi, atan2, cos, sin, hypot, floor, ceil

from numpy import inf

from .objet import Objet, Objet_avec_equation, Argument, ArgumentNonModifiable, \
                    Ref, contexte, RE_NOM_DE_POINT, G
from .angles import Secteur_angulaire
from .points import Point, Point_generique, Centre, Point_translation, Milieu
from .routines import nice_display, distance, carre_distance, formatage, \
                      vect, produit_scalaire, norme, distance_segment, \
                      arrondir_1_25_5, sign
from .vecteurs import Vecteur_unitaire, Vecteur, Vecteur_libre, Vecteur_generique
from .labels import Label_droite, Label_demidroite, Label_segment
from .transformations import Translation

from .. import param
from ..pylib import eval_restricted, fullrange

from sympy import Rational
##########################################################################################

## LIGNES






class Ligne_generique(Objet_avec_equation):
    u"""Une ligne générique.

    Usage interne : la classe mère pour les droites, segments, demi-droites."""

    _affichage_depend_de_la_fenetre = True
    _marqueurs = "()"

    point1 = __point1 = Argument("Point_generique")
    point2 = __point2 = Argument("Point_generique")

    def __init__(self, point1, point2, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        Objet.__init__(self, **styles)
        #~ self._initialiser(point1 = Point_generique, point2 = Point_generique)


    def _longueur(self):
        return norme(self.__point2.x - self.__point1.x, self.__point2.y - self.__point1.y)


    def _espace_vital(self):
        x1, y1 = self.__point1.coordonnees
        x2, y2 = self.__point2.coordonnees
        return (min(x1, x2), max(x1, x2), min(y1, y2), max(y1, y2))


    def _get_equation(self):
        u"Retourne un triplet (a, b, c), tel que ax + by + c = 0 soit une équation de droite de la ligne."
        xA, yA = self.__point1.coordonnees
        xB, yB = self.__point2.coordonnees
        a, b, c = yA - yB, xB - xA, xA*yB - yA*xB
        while -1 < a < 1 and -1 < b < 1:
            a *= 10
            b *= 10
            c *= 10
        return (a, b, c)

    @property
    def equation_reduite(self):
        u"""Retourne (a, b) si la droite a une équation de la forme y=ax+b ; et (c,) si la droite a une équation de la forme x=c.

        Ceci permet de comparer facilement deux droites, ce qui n'est pas le cas avec la propriété .équation (puisqu'une droite a une infinité d'équations) : si d1._equation_reduite() ~ d2._equation_reduite, d1 et d2 sont (à peu près) confondues.
        """
        eq = self.equation
        if eq is None:
            return
        a, b, c = eq
        if abs(b) > contexte['tolerance']:
            return (-a/b, -c/b)
        else:
            return (-c/a, )

    def _parallele(self, ligne):
        u"Indique si la ligne est parallèle à une autre ligne."
        if not isinstance(ligne, Ligne_generique):
            raise TypeError, "L'objet doit etre une ligne."
        a, b, c = self.equation
        a0, b0, c0 = ligne.equation
        return abs(a*b0 - b*a0) < contexte['tolerance']

    def _perpendiculaire(self, ligne):
        u"Indique si la ligne est perpendiculaire à une autre ligne."
        if not isinstance(ligne, Ligne_generique):
            raise TypeError, "L'objet doit etre une ligne."
        a, b, c = self.equation
        a0, b0, c0 = ligne.equation
        return abs(a*a0 + b*b0) < contexte['tolerance']

    def __iter__(self):
        return iter((self.__point1, self.__point2))


    def _creer_nom_latex(self):
        u"""Crée le nom formaté en LaTeX. Ex: M1 -> $M_1$."""
        Objet._creer_nom_latex(self)
        nom = self.nom_latex[1:-1]
        if re.match("(" + RE_NOM_DE_POINT + "){2}",  nom):
            self.nom_latex = "$" + self._marqueurs[0] + nom + self._marqueurs[1] + "$"
        else:
            nom = self.latex_police_cursive(nom)
            self.nom_latex = "$" + nom + "$"

    def xy(self, x = None, y = None):
        u"""Retourne les coordonnées du point de la droite d'abscisse ou d'ordonnée donnée.

        x ou y doivent être définis, mais bien sûr pas les deux.

        Nota:
        Si x est donné pour une droite verticale, un point d'abscisse infinie
        est retourné. À l'inverse, si y est donné pour une droite horizontale,
        un point d'ordonnée infinie est retourné.
        """
        x1, y1 = self.__point1.coordonnees
        x2, y2 = self.__point2.coordonnees

        if y is None and x is not None:
            a = self.pente
            return (x, a*(x - x1) + y1)
        elif x is None and y is not None:
            a = self.copente
            return (a*(y - y1) + x1, y)
        raise TypeError, 'x ou y doivent etre definis.'

    @property
    def pente(self):
        x1, y1 = self.__point1.coordonnees
        x2, y2 = self.__point2.coordonnees
        return (y2 - y1)/(x2 - x1) if (x2 - x1) else inf

    @property
    def copente(self):
        x1, y1 = self.__point1.coordonnees
        x2, y2 = self.__point2.coordonnees
        return (x2 - x1)/(y2 - y1) if (y2 - y1) else inf

    def _points_extremes(self):
        u"""Donne les points d'intersection de la droite avec les bords de la fenêtre.

        Retourne une liste de deux points au maximum.
        """
        # Attention, il faut impérativement récupérer la fenêtre **sur le canevas**,
        # dans le cas d'un repère orthonormé.
        xmin, xmax, ymin, ymax = self.canvas.fenetre
        eps = contexte['tolerance']
        dx = eps*(xmax - xmin)
        dy = eps*(ymax - ymin)
        # points contient les intersections de la droite avec les bords de la fenêtre.
        points = []
        Mxmin = self.xy(x=xmin)
        if ymin - dy <= Mxmin[1] <= ymax + dy:
            points.append(Mxmin)
        Mxmax = self.xy(x=xmax)
        if ymin - dy <= Mxmax[1] <= ymax + dy:
            points.append(Mxmax)
        Mymin = self.xy(y=ymin)
        if xmin - dx <= Mymin[0] <= xmax + dx:
            points.append(Mymin)
        Mymax = self.xy(y=ymax)
        if xmin - dx <= Mymax[0] <= xmax + dx:
            points.append(Mymax)
        # En principe, points ne contient que deux éléments.
        # Il peut éventuellement en contenir 3 ou 4, dans le cas limite où la droite
        # coupe la fenêtre dans un coin. Dans ce cas, on peut trouver
        # deux points d'intersection (quasi) confondus.
        # Il faut alors bien s'assurer de ne pas retourner 2 points confondus.
        if len(points) == 4:
            return points[:2] # Mxmin et Mxmax ne peuvent être confondus.
        elif len(points) == 3:
            if points[0] == Mxmin and points[1] == Mxmax:
                return points[:2] # Mxmin et Mxmax ne peuvent être confondus.
            return points[1:] # Mymin et Mymax non plus.
        else:
            assert len(points) <= 2
            return points

    def angle_affichage(self):
        u"Angle, à l'écran, de la ligne par rapport l'horizontale, en radians."
        x1, y1 = self.__point1.coordonnees
        x2, y2 = self.__point2.coordonnees
        dx, dy = self.feuille.dcoo2pix(x2 - x1, y2 - y1)
        return atan2(-dy, dx)



class Segment(Ligne_generique):
    u"""Un segment.

    Un segment défini par deux points"""

    _affichage_depend_de_la_fenetre = True # à cause du codage //, X, etc.
    _style_defaut = param.segments
    _prefixe_nom = "s"
    _marqueurs = "[]"

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        Ligne_generique.__init__(self, point1 = point1, point2 = point2, **styles)
        self.etiquette = Label_segment(self)


    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.ligne(), self.rendu.codage()]
        x1, y1 = self.__point1.coordonnees
        x2, y2 = self.__point2.coordonnees
        couleur = self.style("couleur")
        epaisseur = self.style("epaisseur")
        niveau = self.style("niveau")
        style = self.style("style")

        for elt_graphique in self._representation:
            elt_graphique.set_visible(True)

        plot, codage = self._representation
        plot.set_data(((x1, x2), (y1, y2)))
        plot.set(color=couleur, linestyle=style, linewidth=epaisseur)
        plot.zorder = niveau

        # Codages utilisés pour indiquer les segments de même longueur
        if not self.style("codage"):
            codage.set_visible(False)
        else:
            codage.set(visible=True, style=self.style('codage'),
                       position=(.5*(x1 + x2), .5*(y1 + y2)),
                       direction=(x2 - x1, y2 - y1),
                       taille=param.codage["taille"], angle=param.codage["angle"],
                       color=couleur, linewidth=epaisseur,
                       zorder=niveau + 0.01,
                      )


    def image_par(self, transformation):
        return Segment(self.__point1.image_par(transformation), self.__point2.image_par(transformation))


    def _distance_inf(self, x, y, d):
        return distance_segment((x, y), self._pixel(self.__point1), self._pixel(self.__point2), d)


    def _contains(self, M):
        #if not isinstance(M, Point_generique):
        #    return False
        A = self.__point1
        B = self.__point2
        xu, yu = vect(A, B)
        xv, yv = vect(A, M)
        if abs(xu*yv - xv*yu) > contexte['tolerance']:
            return False
        if abs(xu)  > abs(yu):
            k = xv/xu
        elif yu:
            k = yv/yu
        else:  # A == B
            return M == A
        return 0 <= k <= 1

    @property
    def longueur(self):
        u"""Longueur du segment.

        Alias de _longueur, disponible pour indiquer que l'objet a vraiment une longueur
        au sens mathématique du terme (pas comme une droite !)"""
        return self._longueur()

    @property
    def extremites(self):
        return self.__point1, self.__point2

    @property
    def info(self):
        return self.nom_complet + u' de longueur ' + nice_display(self.longueur)

    @staticmethod
    def _convertir(objet):
        if hasattr(objet,  "__iter__"):
            return Segment(*objet)
        raise TypeError, "'" + str(type(objet)) + "' object is not iterable"



class Demidroite(Ligne_generique):
    u"""Une demi-droite.

    Une demi-droite définie par son origine et un deuxième point"""

    _style_defaut = param.droites
    _prefixe_nom = "d"
    _marqueurs = "[)"

    origine = __origine = Argument("Point_generique", defaut = Point)
    point = __point = Argument("Point_generique", defaut = Point)

    def __init__(self, origine = None, point = None, **styles):
        self.__origine = origine = Ref(origine)
        self.__point = point = Ref(point)
        Ligne_generique.__init__(self, point1 = origine, point2 = point, **styles)
        self.etiquette = Label_demidroite(self)

    def image_par(self, transformation):
        return Demidroite(self.__point1.image_par(transformation), self.__point2.image_par(transformation))

    def _conditions_existence(self):
        return carre_distance(self.__origine, self.__point) > contexte['tolerance']**2
        # EDIT: les conditions d'existence en amont sont désormais bien définies (ou devraient l'être !!)
        # return [self.point1.coo is not None and self.point2.coo is not None and sum(abs(self.point1.coo - self.point2.coo)) > contexte['tolerance']]
        # si les conditions d'existence en amont sont mal definies, il se peut que les coordonnees d'un point valent None





    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.ligne()]

        x, y = self.__origine.coordonnees
        x0, y0 = self.__point.coordonnees
        points = self._points_extremes()
        if len(points) < 2:
            # La droite sous-jacente ne coupe pas la fenêtre (ou seulement en un point)
            return
        (x1, y1), (x2, y2) = points
        plot = self._representation[0]

        if produit_scalaire((x1 - x, y1 - y), (x0 - x, y0 - y)) > produit_scalaire((x2 - x, y2 - y), (x0 - x, y0 - y)):
            plot.set_data((x1, x), (y1, y))
        else:
            plot.set_data((x, x2), (y, y2))
        plot.set(color = self.style("couleur"), linestyle = self.style("style"),
                 linewidth = self.style("epaisseur"), zorder = self.style("niveau"))


    def _distance_inf(self, x, y, d):
        # cf. "distance_point_segment.odt" dans "doc/developpeurs/maths/"
        xA, yA = self._pixel(self.__origine)
        xB, yB = self._pixel(self.__point)
        x1 = min(xA, xB); x2 = max(xA, xB)
        y1 = min(yA, yB); y2 = max(yA, yB)
        if (xA == x1 and x > x1 - d or xA == x2 and x < x2 + d) \
                and (yA == y1 and y > y1 - d or yA == y2 and y < y2 + d):
            return ((yA - yB)*(x - xA)+(xB - xA)*(y - yA))**2/((xB - xA)**2+(yB - yA)**2) < d**2
        else:
            return False


    def _contains(self, M):
        #if not isinstance(M, Point_generique):
        #    return False
        A = self.__origine
        B = self.__point
        xu, yu = vect(A, B)
        xv, yv = vect(A, M)
        if abs(xu*yv - xv*yu) > contexte['tolerance']:
            return False
        if abs(xu) > abs(yu): # (AB) est plutôt horizontale
            k = xv/xu
        elif yu: # (AB) est plutôt verticale
            k = yv/yu
        else:  # A == B
            return M == A
        return 0 <= k


    @property
    def equation_formatee(self):
        u"Equation sous forme lisible par l'utilisateur."
        eq = self.equation
        if eq is None:
            return u"L'objet n'est pas défini."
        # on ne garde que quelques chiffres après la virgule
        a, b, c = (nice_display(coeff) for coeff in eq)
        eps = contexte['tolerance']
        if abs(a) < abs(b): # droite plutôt horizontale
            if (self.__point.ordonnee - self.__origine.ordonnee) > eps:
                ajout = "y > " + nice_display(self.__origine.ordonnee)
            elif (self.__point.ordonnee - self.__origine.ordonnee) < eps:
                ajout = "y < " + nice_display(self.__origine.ordonnee)
            else:
                return u"Précision insuffisante."
        else: # droite plutôt verticale
            if (self.__point.abscisse - self.__origine.abscisse) > eps:
                ajout = "x > " + nice_display(self.__origine.abscisse)
            elif (self.__point.abscisse - self.__origine.abscisse) < eps:
                ajout = "x < " + nice_display(self.__origine.abscisse)
            else:
                return u"Précision insuffisante."
        return formatage("%s x + %s y + %s = 0 et %s" %(a, b, c, ajout))


    @staticmethod
    def _convertir(objet):
        if hasattr(objet,  "__iter__"):
            return Demidroite(*objet)
        raise TypeError, "'" + str(type(objet)) + "' object is not iterable"


class Droite_generique(Ligne_generique):
    u"""Une droite générique.

    Usage interne : la classe mère pour toutes les droites."""

    _style_defaut = param.droites
    _prefixe_nom = "d"

    parallele = Ligne_generique._parallele
    perpendiculaire = Ligne_generique._perpendiculaire

    point1 = __point1 = Argument("Point_generique")
    point2 = __point2 = Argument("Point_generique")

    def __init__(self, point1, point2, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        Ligne_generique.__init__(self, point1 = point1, point2 = point2, **styles)
        self.etiquette = Label_droite(self)

    def image_par(self, transformation):
        return Droite(self.__point1.image_par(transformation), self.__point2.image_par(transformation))

    def _conditions_existence(self):
        return carre_distance(self.__point1, self.__point2) > contexte['tolerance']**2


    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.ligne()]
        points = self._points_extremes()
        if len(points) < 2:
            # La droite ne coupe pas la fenêtre (ou seulement en un point)
            return
        (x1, y1), (x2, y2) = points
        plot = self._representation[0]
        plot.set_data((x1, x2), (y1, y2))
        plot.set(color = self.style("couleur"), linestyle = self.style("style"),
                 linewidth = self.style("epaisseur"), zorder = self.style("niveau"))


    def _distance_inf(self, x, y, d):
        # cf. "distance_point_segment.odt" dans "doc/developpeurs/maths/"
        xA, yA = self._pixel(self.__point1)
        xB, yB = self._pixel(self.__point2)
        return ((yA-yB)*(x-xA)+(xB-xA)*(y-yA))**2/((xB-xA)**2+(yB-yA)**2) < d**2



    def _contains(self, M):
        #if not isinstance(M, Point_generique):
        #    return False
        A = self.__point1
        B = self.__point2
        xu, yu = vect(A, B)
        xv, yv = vect(A, M)
        return abs(xu*yv-xv*yu) < contexte['tolerance']

    @property
    def equation_formatee(self):
        u"Equation sous forme lisible par l'utilisateur."
        eq = self.equation
        if eq is None:
            return u"L'objet n'est pas défini."
        # On ne garde que quelques chiffres après la virgule pour l'affichage.
        a, b, c = (nice_display(coeff) for coeff in eq)
        return formatage("%s x + %s y + %s = 0" %(a, b, c))

    @property
    def info(self):
        return self.nom_complet + u" d'équation " + self.equation_formatee

    def __eq__(self,  y):
        if self.existe and isinstance(y, Droite_generique) and y.existe:
            eq1 = self.equation_reduite
            eq2 = y.equation_reduite
            if len(eq1) == len(eq2) == 1:
                return abs(eq1[0] - eq2[0]) < contexte['tolerance']
            elif len(eq1) == len(eq2) == 2:
                return abs(eq1[0] - eq2[0]) < contexte['tolerance'] and abs(eq1[1] - eq2[1]) < contexte['tolerance']
        return False

    def __ne__(self, y):
        return not self == y


    @staticmethod
    def _convertir(objet):
        if hasattr(objet,  "__iter__"):
            return Droite(*objet)
        raise TypeError, "'" + str(type(objet)) + "' object is not iterable"



class Droite(Droite_generique):
    u"""Une droite.

    Une droite définie par deux points"""


    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)

    def __new__(cls, *args, **kw):
        if len(args) == 1  and isinstance(args[0], basestring):
            newclass = Droite_equation
        elif len(args) == 2  and isinstance(args[1], Vecteur_generique):
            newclass = Droite_vectorielle
        else:
            return object.__new__(cls)
        droite = newclass.__new__(newclass, *args, **kw)
        droite.__init__(*args, **kw)
        return droite

    def __init__(self, point1 = None, point2 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        Droite_generique.__init__(self, point1 = point1, point2 = point2, **styles)



class Point_droite(Point_generique):
    u"""Un des deux points servant à construire une droite d'équation donnée.

    Usage interne.
    Ceci sert pour les droites qui ne sont pas définies à l'aide de points, mais directement à l'aide d'une équation.
    Comme l'implémentation actuelle des droites exige que la droite soit définie par 2 points,
    on génère deux points de la droite à partir de son équation."""

    droite = __droite = Argument("Droite_generique")
    premier = __premier = ArgumentNonModifiable("bool")

    def __init__(self, droite, premier, **styles):
        self.__droite = droite = Ref(droite)
        self.__premier = premier
        Point_generique.__init__(self, **styles)

    def _get_coordonnees(self):
        a, b, c = self.__droite.equation
        if b:
            if self.__premier:
                return 0, -c/b
            else:
                return 1, -a/b - c/b
        else:
            if self.__premier:
                return -c/a, 0
            else:
                return -c/a, 1



class Droite_vectorielle(Droite_generique):
    u"""Une droite dirigée par un vecteur.

    Une droite définie par un point et un vecteur directeur."""

    point = __point = Argument("Point_generique", defaut=Point)
    vecteur = __vecteur = Argument("Vecteur_generique", defaut=Vecteur_libre)

    def __init__(self, point = None, vecteur = None, **styles):
        self.__point = point = Ref(point)
        self.__vecteur = vecteur = Ref(vecteur)
        Objet.__init__(self) # pour pouvoir utiliser 'Point_droite(self, True)', l'objet doit déjà être initialisé
        Droite_generique.__init__(self, Point_droite(self, True), Point_droite(self, False), **styles)

    def _get_equation(self):
        a, b = self.__vecteur.coordonnees
        x, y = self.__point.coordonnees
        return -b, a, b*x - a*y

    def _conditions_existence(self):
        return self.__vecteur.x**2 + self.__vecteur.x**2 > contexte['tolerance']**2




class Parallele(Droite_generique):
    u"""Une parallèle.

    La parallèle à une droite passant par un point."""

    droite = __droite = Argument("Droite_generique")
    point = __point = Argument("Point_generique", defaut = Point)

    def __init__(self, droite, point = None, **styles):
        self.__droite = droite = Ref(droite)
        self.__point = point = Ref(point)
        Objet.__init__(self) # pour pouvoir utiliser 'Point_droite(self, True)', l'objet doit déjà être initialisé
        Droite_generique.__init__(self, Point_droite(self, True), Point_droite(self, False), **styles)

    def _get_equation(self):
        a, b, c = self.__droite.equation
        x, y = self.__point.coordonnees
        return a, b, -a*x-b*y

    def _conditions_existence(self):
        return True




##class Droite_rotation(Droite): # À REDÉFINIR
##    u"""Une image d'une droite par rotation.
##
##    Une droite obtenue par rotation d'une autre droite, ou d'un bipoint, ou..."""
##
##    droite = __droite = Argument("Droite")
##    rotation = __rotation = Argument("Rotation")
##
##    def __init__(self, droite, rotation, **styles):
##        self.__droite = droite = Ref(droite)
##        self.__rotation = rotation = Ref(rotation)
##        warning("A redefinir, voir commentaires dans le code.")
##        Droite.__init__(self, point1 = Point_rotation(droite._Droite__point1, rotation), point2 = Point_rotation(droite._Droite__point2, rotation), **styles)
##    # BUG : droite._Droite__point1 ne va pas, car si l'argument droite est modifié, la modification ne va pas se répercuter sur les arguments de Point_rotation
##
##    def  _get_coordonnees(self):
##         raise NotImplementedError
##


class Perpendiculaire(Droite_generique):
    u"""Une perpendiculaire.

    Une droite perpendiculaire à une autre passant par un point."""

    droite = __droite = Argument("Ligne_generique")
    point = __point = Argument("Point_generique", defaut = Point)

    def __init__(self, droite, point = None, **styles):
        self.__droite = droite = Ref(droite)
        self.__point = point = Ref(point)
        Objet.__init__(self) # pour pouvoir utiliser 'Point_droite(self, True)', l'objet doit déjà être initialisé
        Droite_generique.__init__(self, Point_droite(self, True), Point_droite(self, False), **styles)

    def _get_equation(self):
        a, b, c = self.__droite.equation
        x, y = self.__point.coordonnees
        return -b, a, b*x - a*y

    def _conditions_existence(self):
        return True


class Mediatrice(Perpendiculaire):
    u"""Une médiatrice.

    La médiatrice d'un segment (ou d'un bipoint, ...)

    >>> from wxgeometrie.geolib import Point, Mediatrice, Segment
    >>> A=Point(1,2); B=Point(3,4)
    >>> s=Segment(A,B)
    >>> Mediatrice(A, B) == Mediatrice(s)
    True
    """

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, **styles):
        if isinstance(point1, Segment):
            point2 = point1._Segment__point2
            point1 = point1._Segment__point1
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        Perpendiculaire.__init__(self, Droite(point1, point2), Milieu(point1, point2), **styles)


    def _conditions_existence(self):
        return carre_distance(self.__point1, self.__point2) > contexte['tolerance']**2








class Droite_equation(Droite_generique):
    u"""Une droite définie par une équation.

    Une droite d'équation donnée sous forme d'un triplet (a, b, c). (ax + by + c = 0)"""

    a = __a = Argument("Variable_generique")
    b = __b = Argument("Variable_generique")
    c = __c = Argument("Variable_generique")

    @staticmethod
    def __coeff(match_object):
        if match_object is None:
            return 0
        chaine = match_object.group()
        if chaine == "-":
            return -1
        elif chaine == "+" or not chaine:
            return 1
        elif chaine[-1] == "*":
            chaine = chaine[:-1]
        return eval_restricted(chaine)

    @classmethod
    def __extraire_coeffs(cls, chaine):
        a = cls.__coeff(re.search("[-+]*[^-+xy]*(?=x)", chaine))
        b = cls.__coeff(re.search("[-+]*[^-+xy]*(?=y)", chaine))
        c = cls.__coeff(re.search("[-+]*[^-+xy]+(?=$|[-+])", chaine))
        return a, b, c

    def __init__(self, a = 1,  b = -1,  c = 0, **styles):
        if isinstance(a, basestring):
            membre_gauche, membre_droite = a.replace(" ", "").split("=")
            a, b, c = self.__extraire_coeffs(membre_gauche)
            a_, b_, c_ = self.__extraire_coeffs(membre_droite)
            a -= a_
            b -= b_
            c -= c_
        self.__a = a = Ref(a)
        self.__b = b = Ref(b)
        self.__c = c = Ref(c)
        Objet.__init__(self) # pour pouvoir utiliser 'Point_droite(self, True)', l'objet doit déjà être initialisé
        Droite_generique.__init__(self, point1 = Point_droite(self, True),
                                  point2 = Point_droite(self, False), **styles)
#        self.equation = self.__a,  self.__b, self.__c


##    def verifier_coeffs(self, a,  b,  c):
##        if a == b == 0:
##            self.erreur(u"les deux premiers coefficients sont nuls.")

    def _conditions_existence(self):
        return not self.__a == self.__b == 0

#    def _get_equation(self):
#        # Retourne un triplet (a, b, c), tel que ax + by + c = 0 soit une equation de droite de la ligne.
#        # On peut aussi modifier l'equation de la droite.
#        xA, yA = self.__point1.coordonnees
#        xB, yB = self.__point2.coordonnees
#        return (yA - yB, xB - xA, xA*yB - yA*xB)

    def _set_equation(self, a = None,  b = -1,  c = 0):
        if a is not None:
#            self.verifier_coeffs(a, b, c)
            self.__a = a
            self.__b = b
            self.__c = c

    def _get_equation(self):
        return self.__a, self.__b, self.__c

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





class Bissectrice(Droite_vectorielle):
    u"""Une bissectrice.

    La bissectrice d'un angle défini par 3 points.
    On peut, au choix, entrer un angle ou 3 points comme argument."""

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    point3 = __point3 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, point3 = None, **styles):
        if isinstance(point1, Secteur_angulaire): # Au lieu de 3 points, on peut entrer un angle.
            point2 = point1._Secteur_angulaire__point
            point1 = Point_translation(point2, Translation(point1._Secteur_angulaire__vecteur1))
            point3 = Point_translation(point2, Translation(point1._Secteur_angulaire__vecteur2))
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__point3 = point3 = Ref(point3)

        v = Vecteur_unitaire(Vecteur(point2, point1)) + Vecteur_unitaire(Vecteur(point2, point3))
        Droite_vectorielle.__init__(self, point2, v, **styles)

    def _conditions_existence(self):
        return carre_distance(self.__point1, self.__point2) > contexte['tolerance']**2 and \
                    carre_distance(self.__point2, self.__point3) > contexte['tolerance']**2




class Point_tangence(Point_generique):
    u"""Un point de tangence.

    Le point de tangence d'un cercle et d'une droite tangente au cercle passant par un point donné.
    Usage interne."""

    cercle = __cercle = Argument("Cercle_generique")
    point = __point = Argument("Point_generique")

    def __init__(self, cercle, point, angle_positif = None, **styles):
        self.__cercle = cercle = Ref(cercle)
        self.__point = point = Ref(point)
        self.__angle_positif = angle_positif = Ref(angle_positif)
        self.__intersection = G.Intersection_cercles(cercle, G.Cercle_diametre(Centre(cercle), point), angle_positif)
        Point_generique.__init__(self, **styles)

    def _get_coordonnees(self):
        # on a deux cas :
        # si le point est sur le cercle, on prend le point
        # si le point n'est pas sur le cercle, on construit une intersection de cercles
        if self.__point in self.__cercle:
            return self.__point.coordonnees
        return self.__intersection.coordonnees

    def _conditions_existence(self):
        return self.__intersection.existe or self.__point in self.__cercle



class Tangente(Perpendiculaire):    # À REDÉFINIR ?
    u"""Une tangente.

    Une des deux tangentes à un cercle passant par un point extérieur au cercle.
    Le dernier paramètre (True/False) sert à distinguer les deux tangentes.
    (Voir la classe Intersection_cercles pour plus d'infos)."""

    cercle = __cercle = Argument("Cercle_generique", defaut='Cercle')
    point = __point = Argument("Point_generique", defaut = Point)
    angle_positif = __angle_positif = Argument("bool", defaut = True)

    def __init__(self, cercle = None, point = None, angle_positif = None, **styles):
        self.__cercle = cercle = Ref(cercle)
        self.__point = point = Ref(point)
        self.__angle_positif = angle_positif = Ref(angle_positif)
        self.point_tangence = self.__point_tangence = Point_tangence(cercle, point, angle_positif)
        Perpendiculaire.__init__(self, Droite(Centre(cercle), self.__point_tangence), self.__point_tangence, **styles)


    def _conditions_existence(self):
        return self.__point_tangence.existe


    def _set_feuille(self):
        # si l'on crée 2 fois de suite un tangente de mêmes cercle et point,
        # alors on doit obtenir les deux tangentes différentes possibles.
        if "_Tangente__angle_positif" in self._valeurs_par_defaut:
            for objet in self.feuille.objets.lister(type = Tangente):
                if objet._Tangente__cercle is self.__cercle and objet._Tangente__point is self.__point:
                    # on crée l'autre tangente
                    self.__angle_positif = not objet._Tangente__angle_positif
                    break
        if "_Tangente__point" in self._valeurs_par_defaut:
            if distance(self.__cercle.centre, self.__point) < self.__cercle.rayon:
                r = self.__cercle.rayon*uniform(1, 2)
                a = uniform(0, 2*pi)
                self.__point.coordonnees = self.__cercle.centre.x + r*cos(a), self.__cercle.centre.y + r*sin(a)
        Objet._set_feuille(self)








class Demiplan(Objet_avec_equation):
    u"""Un demi-plan.

    Le demi-plan délimité par la droite d et contenant le point M."""

    _affichage_depend_de_la_fenetre = True
    _marqueurs = "()"
    _style_defaut = param.polygones
    _prefixe_nom = "P"

    droite = __droite = Argument('Ligne_generique', defaut = Droite)
    point = __point = Argument('Point_generique', defaut = Point)
    droite_incluse = __droite_incluse = Argument(bool, defaut = True)

    def __init__(self, droite = None, point = None, droite_incluse = None, **styles):
        self.__droite = droite = Ref(droite)
        self.__point = point = Ref(point)
        self.__droite_incluse = droite_incluse = Ref(droite_incluse)
        Objet_avec_equation.__init__(self, **styles)


    def _get_equation(self):
        return self.__droite.equation


    @property
    def equation_formatee(self):
        u"Equation sous forme lisible par l'utilisateur."
        eq = self.equation
        if eq is None:
            return u"Le demi-plan n'est pas défini."
        test = self._signe()
        if test < 0:
            symbole = '<'
        elif test > 0:
            symbole = '>'
        else:
            return u"Le demi-plan n'est pas défini."
        a, b, c = (nice_display(coeff) for coeff in eq)
        # on ne garde que quelques chiffres après la virgule pour l'affichage
        if self.__droite_incluse:
            symbole += '='
        return formatage("%s x + %s y + %s %s 0" %(a, b, c, symbole))

    def _signe(self, xy = None):
        x, y = (xy if xy else self.__point.xy)
        a, b, c = self.equation
        return cmp(a*x + b*y + c, 0)

    def _contains(self, M):
        signe = self._signe(M)
        return  signe == self._signe() or (self.__droite_incluse and abs(signe) < contexte['tolerance'])

    def _conditions_existence(self):
        return self.__point not in self.__droite


    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.ligne(), self.rendu.polygone()]
        plot, fill = self._representation
        # Intersection de la droite frontière avec le cadre de la fenêtre :
        points = self.__droite._points_extremes()
        couleur, niveau = self.style(('couleur', 'niveau'))
        xmin, xmax, ymin, ymax = self.canvas.fenetre
        # Liste des coins de la fenêtre en tournant dans le sens direct.
        coins = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
        sommets = [coin for coin in coins if (coin in self)]

        if len(points) == 2:
            # La droite frontière partage la fenêtre en 2
            (x1, y1), (x2, y2) = points
            plot.set_data((x1, x2), (y1, y2))
            plot.set(color = couleur, linestyle = self.style("style"),
                     linewidth = self.style("epaisseur"), zorder = niveau + 0.01)
            sommets.extend([(x1, y1), (x2, y2)])
            x0, y0 = (x1 + x2)/2, (y1 + y2)/2
            sommets.sort(key = lambda xy: atan2(xy[0] - x0, xy[1] - y0))

        elif len(sommets) > 1:
            # La droite délimitant le demi-plan ne coupe pas la fenêtre (ou seulement en un coin).
            # Dans ce cas, si au moins 2 sommets sont dans le 1/2 plan, tous y sont.
            assert len(sommets) == 4

        else:
            fill.set(visible=False)
            return

        fill.set_xy(sommets + [sommets[0]])
        fill.set(edgecolor=couleur, facecolor=couleur, alpha=self.style('alpha'),
                 zorder=niveau, visible=True, hatch=self.style('hachures'))


    def _distance_inf(self, x, y, d):
        return self.feuille.pix2coo(x, y) in self



class Axe(Droite):
    u"""Un axe orienté.

    Un axe orienté servant au repérage.
    Cette classe sert essentiellement à construire les axes (Ox) et (Oy).

    Styles spécifiques:
    - `graduations` (bool): afficher ou non les graduations
    - `pas` (int|None):
        * entier `n` (non nul): `n` fois l'écart entre les deux points repères
          de l'axe.
        * `None` ou `0`: adapte automatiquement la taille
          de la graduation à la fenêtre (défaut)
    - `pas_num` (int): entier positif `n`:
        * si `n` est nul, n'affiche aucun nombre sur l'axe ;
        * sinon, affiche un nombre toutes les `n` graduations
          (en partant de l'origine de l'axe).
          En particulier, si `pas_num=1`, toutes les graduations
          auront un nombre.
    - `repeter` (bool): répéter ou non la numérotation sur les axes.
    - `hauteur` (int): hauteur d'une graduation (en pixels).
    - `placement_num` (-1|1): position de la numérotation par rapport à l'axe.
    """

    _style_defaut = param.axes
    _prefixe_nom = "a"
    point1 = __point1 = Argument("Point_generique", defaut=Point)
    point2 = __point2 = Argument("Point_generique", defaut=Point)

    def __init__(self, point1=None, point2=None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        Droite.__init__(self, point1, point2, **styles)


    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.fleche(), self.rendu.lignes()]
        else:
            # On supprime les textes correspondant aux graduations, qui seront
            # recréés.
            self._representation = self._representation[:2]

        #  L'axe lui-même
        #  ==============
        fleche = self._representation[0]
        linewidth = self.style('epaisseur')
        color = self.style('couleur')
        zorder = self.style("niveau")
        taille = self.style("taille")

        # Points d'intersection avec le bord de la fenêtre
        points = self._points_extremes()
        if len(points) < 2:
            # L'axe ne coupe pas la fenêtre (ou seulement en un point)
            return
        (x1, y1), (x2, y2) = points

        O = self.__point1
        I = self.__point2
        xO, yO = O.xy
        xI, yI = I.xy

        # On s'assure que l'axe soit bien orienté
        if abs(xI - xO) > contexte['tolerance']:
            if (x2 - x1)*(xI - xO) < 0:
                x2, x1, y2, y1 = x1, x2, y1, y2
        else:
            if (y2 - y1)*(yI - yO) < 0:
                x2, x1, y2, y1 = x1, x2, y1, y2
        fleche.set(xy0=(x1, y1), xy1=(x2, y2), linewidth=linewidth,
                   angle=self.style("angle"), taille=taille,
                   double=self.style("double_fleche"),
                    color=color, linestyle=self.style("style"),
                   zorder=zorder,
                   )

        #  Les graduations
        #  ===============
        lignes = self._representation[1]

        if not self.style("graduations"):
            lignes.set(visible=False)
            return

        pas = self.style("pas")
        if not pas:
            # On détermine automatiquement le pas
            pxO, pyO = self.__point1._pixel()
            pxI, pyI = self.__point2._pixel()
            norme = hypot(pxI - pxO, pyI - pyO)
            # Le pas est déterminé automatiquement
            # L'écart entre deux graduations doit être d'environ 20 pixels.
            # Notons OI la longueur entre les deux points du repère, et
            # k le coefficient appliqué à OI pour obtenir l'écart entre deux
            # graduations.
            # Pour que la lecture reste simple, k doit être de la forme p*10^n,
            # avec p dans {1, 2, 5}
            if norme < contexte['tolerance']:
                # OI est quasiment nul, pas de graduation.
                return
            pas = arrondir_1_25_5(contexte['graduation']/norme)
            ##print("pas::" + str(pas))

        # Vecteur directeur de la droite
        xu, yu = vect(O, I)
        xu *= pas
        yu *= pas

        # Il faut commencer par trouver une graduation qui soit située
        # dans la fenêtre d'affichage (s'il y en a).
        # On récupère les points visibles extremes de l'axe.
        xmin, xmax = sorted((x1, x2))
        ymin, ymax = sorted((y1, y2))

        # On distingue le cas des droites plutôt verticale, et celui des droites
        # plutôt horizontales (pour éviter des divisions par zéro ou presque zéro).
        if abs(yu) < abs(xu):
            # Droite plutôt horizontale
            assert xu
            # On va graduer **de gauche à droite**.
            n = (xmin - xO)/xu
            # On récupère la graduation située juste après xmin.
            n = (ceil(n) if xu > 0 else floor(n)) #(floor(n) if (xO + floor(n)*xu) > xmin else ceil(n))
            # Et on gradue tant qu'on reste dans la fenetre.
            x = xO + n*xu
            y = yO + n*yu
            assert x > xmin
            # Il faut graduer dans le bon sens (on part de xmin, donc x doit
            # augmenter à chaque étape).
            sens = sign(xu)

        else:
            # Droite plutôt verticale
            assert yu
            # On va graduer **de bas en haut**.
            n = (ymin - yO)/yu
            # Même chose que précédemment, en inversant les rôles de x et de y.
            n = (ceil(n) if yu > 0 else floor(n)) #(floor(n) if (yO + floor(n)*yu) < ymax else ceil(n))
            x = xO + n*xu
            y = yO + n*yu
            assert y > ymin
            sens = sign(yu)


        # On calcule le vecteur servant à générer les graduations.
        # Ce vecteur doit être normal au vecteur directeur... pour l'affichage !
        # Autrement dit, le repère n'étant pas forcément orthonormé, il faut
        # travailler **en pixels**.
        # La norme (en pixels également) est fixée par le style `hauteur`.
        pxu, pyu = self.feuille.dcoo2pix(xu, yu)
        pnorm = hypot(pxu, pyu)
        k = .5*self.style('hauteur')/pnorm
        # Vecteur normal à (pxu, pyu) :
        pxv, pyv = k*pyu, -k*pxu
        # On retourne au système de coordonnées.
        xv, yv = self.feuille.dpix2coo(pxv, pyv)

        segments = []
        ##print ':::', xO, n, xu, xO+n*xu
        ##print '(1) debug::axes::(n, xu, yu, x, y, xO, yO)', n, xu, yu, x, y, xO, yO

        # Et on génère les graduations !
        while xmin <= x <= xmax and ymin <= y <= ymax:
            if hypot(*self.feuille.dcoo2pix(x2 - x, y2 - y)) > 1.5*taille:
                # Ne pas superposer une graduation à la pointe de la flêche
                segments.append([(x - xv, y - yv), (x + xv, y + yv)])
            x += sens*xu
            y += sens*yu

        lignes.set(segments=segments, visible=True, color=color, lw=linewidth,
                   zorder=zorder)

        # La légende en dessous des graduations
        # =====================================

        pas_num = self.style('pas_num')

        if not pas_num:
            return

        # Si `pas_num != 1`, on ne met pas de nombre à chaque graduation.
        # Il faut donc recalculer la graduation de départ.
        # `n` (numéro de la graduation de départ) doit être un multiple
        # de l'entier `pas_num` (qui indique combien il y a de graduations entre
        # 2 nombres successifs).
        ##print 'debug::axes::(n, pas_num, xu, yu)', n, pas_num, xu, yu
        ##print ':::sens,xO,n,xu,xO+n*xu', sens, xO, n, xu, xO+n*xu
        n += sens*(n%pas_num)
        x = xO + n*xu
        y = yO + n*yu
        ##print '(2) debug::axes::(n, xu, yu, x, y, xO, yO)', n, xu, yu, x, y, xO, yO

        pvnorm = hypot(pxv, pyv)
        taille_txt = self.etiquette.style('taille')
        couleur_txt = self.etiquette.style('couleur')
        # On s'écarte de 2 pixels par rapport à l'extrémité de la graduation,
        # ainsi que de la moitié de la hauteur du texte.
        # On choisit également le placement avec `self.style('placement_num')`
        # (qui vaut -1 ou 1).
        coeff = self.style('placement_num')*(pvnorm + 2 + .5*taille_txt)/pvnorm
        xw, yw = self.feuille.dpix2coo(coeff*pxv, coeff*pyv)

        eps = contexte['tolerance']
        indice = 0
        indice_O = None
        valeurs = [] # contiendra les triplets (x, y, n)
        while xmin <= x <= xmax and ymin <= y <= ymax:
            if hypot(*self.feuille.dcoo2pix(x2 - x, y2 - y)) > 1.5*taille:
                valeurs.append((x, y, n))
                if abs(x - xO) < eps:
                    indice_O = indice
                indice += 1
            n += sens*pas_num
            x += sens*pas_num*xu
            y += sens*pas_num*yu

        if not self.style('repeter'):
            # Si seulement deux valeurs s'affichent, il est préférable
            # que ce soit 0 et la valeur suivante, à condition que 0
            # soit dans la fenêtre d'affichage.
            if indice_O is not None:
                if indice_O == len(valeurs) - 1:
                    valeurs = valeurs[indice_O - 1:]
                else:
                    valeurs = valeurs[indice_O:indice_O + 2]
            else:
                valeurs = valeurs[:2]


        for x, y, n in valeurs:
            s = nice_display(n*pas)
            if s[0] == '-':
                s = '$%s$' % s
            txt = self.rendu.texte(x + xw, y + yw, s,
                    va='center', ha='center', size=taille_txt,
                    color = couleur_txt)
            self._representation.append(txt)



##########################################################################################
## EN TRAVAUX :


class Repere(Objet):
    u"""Un repère du plan.

    Un repère du plan défini par deux axes de même origine."""

    _style_defaut = param.axes
    _prefixe_nom = "rep"
    axe1 = __axe1 = Argument(Axe)
    axe2 = __axe2 = Argument(Axe)

    def __init__(self, axe1=None, axe2=None, **styles):
        self.__axe1 = axe1 = Ref(axe1)
        self.__axe2 = axe2 = Ref(axe2)
        Objet.__init__(self, **styles)

    def style(self, nom_style=None, **kw):
        if kw:
            self.__axe1.style(**kw)
            self.__axe2.style(**kw)
        return self.style(nom_style)



##class Graduations(Objet):
    ##u"""Un ensemble de graduations sur un axe.
##
    ##Gère l'ensemble des graduations d'un axe.
    ##En principe, il n'y a pas besoin de le créer manuellement."""
##
    ##_style_defaut = param.graduations
    ##_prefixe_nom = "grad"
    ##axe1 = __axe1 = Argument(Axe)
##
    ##def __init__(self, axe):
        ##self.__axe = axe = Ref(axe)




##
##
##class Tangente_courbe_interpolation(Droite_equation):
    ##u"""Une tangente à une courbe de type interpolation polynomiale par morceau.
##
    ##Le coefficient directeur est estimé par approximation numérique avec taux de variation
    ##sur un pas  self.__canvas__.pas().
##
    ##:type courbe: Interpolation_polynomiale_par_morceaux
    ##:param courbe: la courbe sur laquelle va se placer la tangente
    ##:type x: float
    ##:param x: position du point de tangence en abscisse; doit être entre xmin et xmax.
##
    ##exemple::
##
    ##>>> A = Point(-1,-2)
    ##>>> B = Point(2,1)
    ##>>> C = Point(8,-3)
    ##>>> d = Interpolation_polynomiale_par_morceaux(A,B,C, derivees=[-1,0.5,2])
    ##>>> t2 = Tangente_courbe_interpolation(d, x= -2 )
##
    ##"""
##
    ##courbe = __courbe = Argument('Interpolation_polynomiale_par_morceaux')
    ##x = __x = Argument('float,int')
##
    ##def __init__(self, courbe, x = None):
        ##self.__courbe = Ref(courbe)
        ##self.__x = Ref(x)
        ##P = Point(x, courbe.fonction(x))
        ##v = courbe.fonction.derivative(x, 1)
        ##Droite_equation.__init__(self, a= -v, b= 1, c= -P.y + v*P.x.contenu )
##
    ##def _get_equation(self):
        ##y,v = self.courbe.fonction.derivatives(self.x, 2) #f(x), f'(x)
        ##self._set_equation(a = -v, b = 1, c = -y + v * self.x)
        ##return Droite_equation._get_equation(self)


class Tangente_glisseur_interpolation(Droite_equation):
    u"""Une tangente à une courbe de type interpolation polynomiale par morceau, et qui glisse.

    Le coefficient directeur est estimé par approximation numérique avec taux de variation
    sur un pas  self.__canvas__.pas().

    :type courbe: Interpolation_polynomiale_par_morceaux
    :param courbe: la courbe sur laquelle va se placer la tangente
    :type P: Glisseur_courbe
    :param P: Point de type glisseur sur la courbe.

    exemple::

    >>> from wxgeometrie import Point, Interpolation_polynomiale_par_morceaux
    >>> from wxgeometrie import Glisseur_courbe, Tangente_glisseur_interpolation
    >>> A = Point(-1,-2)
    >>> B = Point(2,1)
    >>> C = Point(8,-3)
    >>> d = Interpolation_polynomiale_par_morceaux(A,B,C, derivees=[-1,0.5,2])
    >>> P = Glisseur_courbe(d)
    >>> d1 = Tangente_glisseur_interpolation(d, P)

    """

    courbe = __courbe = Argument('Interpolation_polynomiale_par_morceaux')
    glisseur = __glisseur = Argument('Glisseur_courbe')

    def __init__(self, courbe, glisseur=None):
        self.__courbe = courbe = Ref(courbe)
        self.__glisseur = P = Ref(glisseur)
        Droite_equation.__init__(self)


    def _get_equation(self):
        v = self.courbe.fonction.derivative(self.glisseur.x.contenu, 1)
        self._set_equation(a = -v, b = 1, c = -self.glisseur.y + v*self.glisseur.x.contenu)
        return Droite_equation._get_equation(self)
