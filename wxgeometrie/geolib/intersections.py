# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                   Objets                    #
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


from .lignes import Ligne_generique, Droite_generique, Tangente
from .cercles import Cercle_generique, Arc_generique
from .objet import Ref, Argument, contexte, Objet
from .routines import vect, angle_vectoriel, produit_scalaire, racines
from .points import Point_generique

##########################################################################################

# Intersections

def Intersection(objet1, objet2, **styles):
    def case(type1, type2):
        return (isinstance(objet1, type1) and isinstance(objet2, type2))\
                    or (isinstance(objet2, type1) and isinstance(objet1, type2))
    if case(Ligne_generique, Ligne_generique):
        return Intersection_droites(objet1, objet2, **styles)
    elif case(Ligne_generique, (Cercle_generique, Arc_generique)):
        return Intersection_droite_cercle(objet1, objet2, **styles)
    elif case((Cercle_generique, Arc_generique), (Cercle_generique, Arc_generique)):
        return Intersection_cercles(objet1, objet2, **styles)
    else:
        raise TypeError, "Intersection d'objets non supportes."



class Intersection_generique(Point_generique):
    u"""Une intersection générique.

    La classe mère des différents types d'intersections"""

    objet1 = __objet1 = Argument("Objet")
    objet2 = __objet2 = Argument("Objet")

    def __init__(self, objet1, objet2, **styles):
        self.__objet1 = objet1 = Ref(objet1)
        self.__objet2 = objet2 = Ref(objet2)
        Point_generique.__init__(self, **styles)


    def _intersections(self):
        return tuple(point for point in \
                     self._cache.get('intersections_possibles', self._intersections_possibles)\
                     if self._tester_solution(point))

    @property
    def intersections(self):
        u"""Liste de coordonnées correspondant aux points d'intersections possibles.

        Le premier couple correspond aux coordonnées du point lui-même.
        Attention, tous ces points ne sont pas forcément des points d'intersection.
        En effet, pour calculer ces intersections, on assimile les segments à des
        droites, et les arcs à des cercles.
        Il faut ensuite tester les solutions potentielles avec ._tester_solution().
        """
        return self._cache.get('intersections', self._intersections)

    @staticmethod
    def _tester_solution(solution, *ensembles):
        u"""Effectue des tests pour valider une solution potentielle.

        Plus précisément, on vérifie que la solution appartient aux ensembles
        indiqués, mais seulement pour certains types d'ensemble:
        - segments et demi-droites,
        - arcs de cercle.
        Ils ne sont pas pratiqués pour les droites et les cercles.

        L'idée est la suivante :
        pour chercher l'intersection d'un segment et d'un arc de cercle,
        on cherche l'intersection entre la droite et le cercle qui les contiennent,
        et on teste les solutions trouvées pour voir si elles appartiennent bien
        au segment et à l'arc de cercle, à l'aide de cette méthode.
        """
        def appartient(sol, ens):
            if isinstance(sol, (Cercle_generique, Droite_generique)):
                # aucun test n'est pratiqué
                return True
            return sol in ens
        return all(appartient(solution, ensemble) for ensemble in ensembles)


    def _get_coordonnees(self):
        u"Ne pas appeler directement (erreurs possibles)."
        return self._cache.get('intersections_possibles', self._intersections_possibles)[0]


    def _conditions_existence(self):
        intersections = self._cache.get('intersections_possibles', self._intersections_possibles)
        if intersections:
            return self._tester_solution(intersections[0], self.__objet1, self.__objet2)
        return False



class Intersection_droites(Intersection_generique):
    u"""Une intersection de droites.

    L'intersection de 2 droites, segments, demi-droites..."""

    droite1 = __droite1 = Argument("Ligne_generique")
    droite2 = __droite2 = Argument("Ligne_generique")

    def __init__(self, droite1, droite2, **styles):
        self.__droite1 = droite1 = Ref(droite1)
        self.__droite2 = droite2 = Ref(droite2)
        Intersection_generique.__init__(self, objet1 = droite1, objet2 = droite2, **styles)

    def _intersections_possibles(self):
        u"""Liste de coordonnées correspondant aux points d'intersections possibles.

        Le premier couple correspond aux coordonnées du point lui-même.
        Attention, tous ces points ne sont pas forcément des points d'intersection.
        En effet, pour calculer ces intersections, on assimile les segments à des
        droites, et les arcs à des cercles.
        Il faut ensuite tester les solutions potentielles avec ._tester_solution().
        """
        a, b, c = self.__droite1.equation
        d, e, f = self.__droite2.equation
        determinant = a*e - b*d
        if abs(determinant) <= contexte['tolerance']:
            return ()
        x = self.__x = (f*b - c*e)/determinant
        y = self.__y = (d*c - a*f)/determinant
        return (x, y), # liste (tuple) de couples





class Intersection_droite_cercle(Intersection_generique): # ATTENTION, il y a des modifications à faire avant de surclasser !
    u"""Une intersection d'une droite et d'un cercle.

    Un des deux points M et N d'intersection d'une droite et d'un cercle.
    Supposons qu'on le note M, et que la droite soit (AB).
    L'argument premier_point (optionnel) sert à différencier les deux points d'intersection.
    Il sert à indiquer si M se trouve "près" de A (1er point de (AB)) ou de B (2ème point).
    (Plus précisément, si premier_point == True, MA + NB est minimal).
    """

    droite = __droite = Argument("Ligne_generique")
    cercle = __cercle = Argument("Cercle_generique, Arc_generique")
    premier_point = __premier_point = Argument("bool", defaut = True)

    def __init__(self, droite, cercle, premier_point = None, **styles):
        # l'intersection de la droite et du cercle (si elle existe) est deux points (éventuellement confondus).
        # lorsque l'utilisateur créé deux fois deux suite un point d'intersection, ce ne doit pas être le même.
        if isinstance(cercle, Ligne_generique):
            droite, cercle = cercle, droite
        self.__droite = droite = Ref(droite)
        self.__cercle = cercle = Ref(cercle)
        self.__premier_point = premier_point = Ref(premier_point)
        Intersection_generique.__init__(self, objet1 = droite, objet2 = cercle, **styles)

    def _set_feuille(self):
        if "_Intersection_droite_cercle__premier_point" in self._valeurs_par_defaut:
            for objet in self.__feuille__.objets.lister(type = Intersection_droite_cercle):
                if objet._Intersection_droite_cercle__droite is self.__droite and objet._Intersection_droite_cercle__cercle is self.__cercle:
                    # une intersection existe déjà, on va construire l'autre
                    self.__premier_point = not objet._Intersection_droite_cercle__premier_point
                    return
        Objet._set_feuille(self)


    def _intersections_possibles(self):
        u"""Liste de coordonnées correspondant aux points d'intersections possibles.

        Le premier couple correspond aux coordonnées du point lui-même.
        Attention, tous ces points ne sont pas forcément des points d'intersection.
        En effet, pour calculer ces intersections, on assimile les segments à des
        droites, et les arcs à des cercles.
        Il faut ensuite tester les solutions potentielles avec ._tester_solution().
        """
        points_intersection = []

        # Cas de l'intersection d'une tangente à un cercle avec "son" cercle :
        # TODO: détecter la tangence de manière générale
        if isinstance(self.__droite, Tangente) and self.__droite.cercle is self.__cercle:
            points_intersection = [self.__droite.point_tangence.coordonnees]
        else:
            a, b, c = self.__droite.equation
            d, e, f = self.__cercle.equation

            if abs(b) > contexte['tolerance']: # La droite n'est pas verticale
                m = -a/b; n = -c/b # equation de la droite : y = mx + n
                sols = racines(m**2 + 1, 2*n*m + d + e*m, n**2 + e*n + f, exact=contexte['exact'])
                points_intersection = [(x, m*x + n) for x in sols]

            elif abs(a) > contexte['tolerance']: # La droite est verticale
                x = -c/a
                sols = racines(1, e, x**2 + d*x + f, exact=contexte['exact'])
                points_intersection = [(x, y) for y in sols]

            # Le dernier cas correspond à une droite d'équation ayant
            # des coefficients presque nuls => précision insuffisante.

        if len(points_intersection) == 2:
            # La partie la plus complexe consiste à distinguer
            # les deux points d'intersection à l'aide du "point proche".
            # Pour comprendre ce qui s'y passe, il est conseillé de faire un dessin !
            if self.__premier_point:
                A = self.__droite.point1
                B = self.__droite.point2
            else:
                A = self.__droite.point2
                B = self.__droite.point1
            u = vect(A, B)
            M, N = points_intersection
            if produit_scalaire(u, vect(A, M)) > produit_scalaire(u, vect(A, N)):
                points_intersection.reverse()

        return points_intersection






class Intersection_cercles(Intersection_generique): # ATTENTION, il y a des modifications à faire avant de surclasser !
    u"""Une intersection de cercles.

    Un des deux points M et N d'intersection des deux cercles.
    L'argument angle_positif permet de distinguer les deux points.
    Si on note A et B les centres respectifs des 2 cercles, l'angle orienté (AB>, AM>) doit être de signe constant.
    """

    cercle1 = __cercle1 = Argument("Cercle_generique, Arc_generique")
    cercle2 = __cercle2 = Argument("Cercle_generique, Arc_generique")
    angle_positif = __angle_positif = Argument("bool", defaut = True)

    def __init__(self, cercle1, cercle2, angle_positif = None, **styles):
        self.__cercle1 = cercle1 = Ref(cercle1)
        self.__cercle2 = cercle2 = Ref(cercle2)
        self.__angle_positif = angle_positif = Ref(angle_positif)
        Intersection_generique.__init__(self, objet1 = cercle1, objet2 = cercle2, **styles)


    def _set_feuille_(self):
        # L'intersection de deux cercles (si elle existe) est deux points
        # (éventuellement confondus).
        # Lorsque l'utilisateur crée deux fois de suite un point d'intersection,
        # ce ne doit pas être le même qui est créé deux fois de suite.
        if "_Intersection_cercles__angle_positif" in self._valeurs_par_defaut:
            for objet in self.__feuille__.objets.lister(type = Intersection_cercles):
                if objet._Intersection_cercles__cercle1 is self.__cercle1 and objet._Intersection_cercles__cercle2 is self.__cercle2:
                    # pour ne pas créer le même point.
                    self.__angle_positif = not objet._Intersection_cercles__angle_positif
        Objet._set_feuille(self)


    def _intersections_possibles(self):
        u"""Liste de coordonnées correspondant aux points d'intersections possibles.

        Le premier couple correspond aux coordonnées du point lui-même.
        Attention, tous ces points ne sont pas forcément des points d'intersection.
        En effet, pour calculer ces intersections, on assimile les segments à des
        droites, et les arcs à des cercles.
        Il faut ensuite tester les solutions potentielles avec ._tester_solution().
        """
        points_intersection = []
        a, b, c = self.cercle1.equation
        d, e, f = self.cercle2.equation

        if (a, b, c) != (d, e, f):
            # On soustrait membre à membre les 2 équations de cercle ;
            # on obtient ainsi une équation de droite :
            # (a-d)x + (b-e)y + (c-f) = 0
            # On se ramène donc au cas de l'intersection d'un cercle et d'une droite
            a, b, c = a - d, b - e, c - f

            if abs(b) > contexte['tolerance']: # La droite n'est pas verticale
                m = -a/b; n = -c/b # equation de la droite : y = mx + n
                sols = racines(m**2 + 1, 2*n*m + d + e*m, n**2 + e*n + f, exact=contexte['exact'])
                points_intersection = [(x, m*x+n) for x in sols]

            elif abs(a) > contexte['tolerance']: # La droite est verticale
                x = -c/a
                sols = racines(1, e, x**2 + d*x + f, exact=contexte['exact'])
                points_intersection = [(x, y) for y in sols]

            # Dernier cas possible : la droite n'existe pas (cercles concentriques).
            # Pas d'intersection (ou alors, c'est tout le cercle -> non géré).

        if len(points_intersection) == 2:
            # Là encore, la partie la plus complexe consiste à distinguer
            # les deux points d'intersection, à l'aide cette fois du signe de l'angle.
            # Pour comprendre ce qui s'y passe, il est conseillé de faire un dessin !
            A = self.__cercle1.centre.coordonnees
            B = self.__cercle2.centre.coordonnees
            M, N = points_intersection
            a = angle_vectoriel(vect(A, B), vect(A, M))

            if (a < 0 and self.__angle_positif) or (a > 0 and not self.__angle_positif):
                points_intersection.reverse()

        return points_intersection
