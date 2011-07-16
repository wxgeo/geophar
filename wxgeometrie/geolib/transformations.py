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

from math import pi

from .objet import Ref, Argument, contexte, Objet, G
from .points import Point_generique, Point, Point_rotation, Point_translation,\
                    Point_homothetie, Point_reflexion
from .angles import Angle_generique, Angle_libre
from .vecteurs import Vecteur_generique, Vecteur_libre





##########################################################################################

# Divers






##class Transformation_generique(Objet):
##    u"""Une transformation.
##
##    La classe mère de toutes les transformations (usage interne)."""
##    def __init__(self, **styles):
##        Objet.__init__(self, **styles)
##
##    def __call__(self, objet):
##        if isinstance(objet, Ref):
##            if isinstance(objet.__objet__, Point_generique):
##                # pour garder la référence
##                return self._Point_image(objet, self)
##            else:
##                # dans les autres cas, ce serait assez compliqué de garder la référence...
##                # TODO: garder (si c'est faisable) la référence dans les autres cas (au moins pour les variables)
##                # cela éviterait un certain nombre de bugs (par ex., si on modifie le rayon d'un cercle défini par une variable, le rayon du cercle image n'est pas modifié !)
##                return self.__call__(objet.__objet__)
##        elif isinstance(objet, Point_generique):
##            return self._Point_image(objet, self)
##        elif isinstance(objet, Polygone_generique):
##            # PATCH: problème avec les polygones ayant des sommets déplacables (le sommet image serait déplaçable)
##            return Polygone(*(self(point) for point in objet._Polygone_generique__points))
##        elif isinstance(objet, Objet) and not isinstance(objet, (Objet_numerique, Transformation_generique)):
##            return objet.__class__(**dict((key,  self(value)) for key, value in objet._iter_arguments))
##        else:
##            return objet




class Transformation_generique(Objet):
    u"""Une transformation.

    La classe mère de toutes les transformations (usage interne)."""
    def __init__(self, **styles):
        Objet.__init__(self, **styles)

    def __call__(self, objet):
        if isinstance(objet, Ref):
            if isinstance(objet.objet, Point_generique):
                # pour garder la référence
                return self._Point_image(objet, self)
            else:
                # dans les autres cas, ce serait assez compliqué de garder la référence...
                #TODO: Dans l'idéal, il faudrait garder (si c'est faisable) la référence dans les autres cas (au moins pour les variables)
                # cela éviterait un certain nombre de bugs (par ex., si on modifie le rayon d'un cercle défini par une variable, le rayon du cercle image n'est pas modifié !)
                return self.__call__(objet.objet)
        if hasattr(objet, "image_par"):
            return objet.image_par(self)
        raise NotImplementedError,  "L'image de %s par %s n'est pas definie." %(objet.nom_complet, self.nom_complet)



class Rotation(Transformation_generique):
    u"""Une rotation.

    Une rotation définie par son centre, et un angle en radian (r), grad (g) ou degré (d).
    L'unité par défaut est le radian."""

    _Point_image = Point_rotation

    centre = __centre = Argument("Point_generique", defaut='Point(0, 0)')
    angle = __angle = Argument("Angle_generique")

    def __init__(self, centre = None, angle = pi/6, unite = None, **styles):
        if unite is None:
            unite = contexte['unite_angle']
        if not isinstance(angle, Angle_generique):
            angle = Angle_libre(angle, unite = unite)
        self.__centre = centre = Ref(centre)
        self.__angle = angle = Ref(angle)
        Transformation_generique.__init__(self, **styles)


    @property
    def radian(self):
        return self.__angle.radian

    rad = radian

    @property
    def degre(self):
        return self.__angle.degre

    deg = degre

    @property
    def grad(self):
        return self.__angle.grad

##    conversion = {"r": 1., "g": pi/200., "d": pi/180.}
##
##    @staticmethod
##    def choix_unite(unite):
##        u"Gestion des alias."
##        if unite is None:
##            return "r"
##        if unite == u"°" or unite.startswith("d"):
##            return "d"
##        if unite.startswith("g"):
##            return "g"
##        return "r"


    def __call__(self, objet):
        if objet is self.__centre:
            return objet
        return Transformation_generique.__call__(self, objet)







class Translation(Transformation_generique):
    u"""Une translation.

    Une translation définie par un vecteur."""

    _Point_image = Point_translation

    vecteur = __vecteur = Argument("Vecteur_generique", defaut=Vecteur_libre)

    def __init__(self, vecteur = None, **styles):
        self.__vecteur = vecteur = Ref(vecteur)
        Transformation_generique.__init__(self, **styles)

    @staticmethod
    def _convertir(objet):
        if isinstance(objet, Vecteur_generique):
            return Translation(objet)
        raise TypeError, "%s must be of type 'Vecteur_generique'." %objet




class Reflexion(Transformation_generique):
    u"""Une symétrie axiale.

    Une symétrie axiale (réflexion) définie par une droite."""

    _Point_image = Point_reflexion

    droite = __droite = Argument("Ligne_generique", defaut='Droite')

    def __init__(self, droite = None, **styles):
        self.__droite = droite = Ref(droite)
        Transformation_generique.__init__(self, **styles)

    def __call__(self, objet):
        if objet is self.__droite:
            return objet
        return Transformation_generique.__call__(self, objet)




class Homothetie(Transformation_generique):
    u"""Une homothétie.

    Une homothétie définie par son centre et son rapport."""

    _Point_image = Point_homothetie

    centre = __centre = Argument("Point_generique", defaut='Point(0, 0)')
    rapport = __rapport = Argument("Variable_generique")

    def __init__(self, centre = None, rapport = 2, **styles):
        self.__centre = centre = Ref(centre)
        self.__rapport = rapport = Ref(rapport)
        Transformation_generique.__init__(self, **styles)

    def __call__(self, objet):
        if objet is self.__centre:
            return objet
        return Transformation_generique.__call__(self, objet)





class Symetrie_centrale(Homothetie):
    u"""Une symétrie centrale.

    Une symétrie centrale définie par un point."""

    centre = __centre = Argument("Point_generique", defaut='Point(0, 0)')

    def __init__(self, centre = None, **styles):
        self.__centre = centre = Ref(centre)
        Homothetie.__init__(self, centre, -1, **styles)
