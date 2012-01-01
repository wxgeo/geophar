# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

##--------------------------------------#######
#                   Points                    #
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

from random import uniform, normalvariate
from math import cos, sin, pi

from numpy import ndarray

from sympy import cos as scos, sin as ssin

from .objet import Objet_avec_coordonnees, Ref, Argument, Objet, Arguments, \
                   contexte, Objet_avec_coordonnees_modifiables, issympy
from .routines import angle_vectoriel, vect, carre_distance, produit_scalaire, \
                      distance

from .. import param


################################################################################


## POINTS



class Point_generique(Objet_avec_coordonnees):
    u"""Un point générique.

    Usage interne : la classe mère pour tous les types de points (libres, barycentres, intersection...)."""

    _style_defaut = param.points
    _prefixe_nom = "M"
    _enregistrer_sur_la_feuille_par_defaut = True

    def __init__(self, **styles):
        #~ self.__args = GestionnaireArguments()
        Objet_avec_coordonnees.__init__(self, **styles)
        from .labels import Label_point
        self.etiquette = Label_point(self)


    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.ligne()]
        x, y = self.coordonnees
        plot = self._representation[0]
        plot.set_data([x], [y])
        couleur = self.style("couleur")
        plot.set_markeredgecolor(couleur)
        plot.set_markerfacecolor(couleur)
        plot.set_marker(self.style("style"))
        plot.set_markersize(self.style("taille"))
        plot.set_markeredgewidth(self.style("epaisseur"))
        plot.zorder = self.style("niveau")


    def _espace_vital(self):
        x, y = self.coordonnees
        return (x, x, y, y)

    def _get_coordonnees(self):
        return NotImplemented    # sera implemente differemment pour chaque type de point

    @property
    def abscisse(self):
        return self.coordonnees[0]

    @property
    def ordonnee(self):
        return self.coordonnees[1]

    @property
    def affixe(self):
        coordonnees = self.coordonnees
        return coordonnees[0] + coordonnees[1]*1j

    x = abscisse
    y = ordonnee
    z = affixe

#    def _image(self, transformation):
#        if isinstance(transformation, Rotation):
#            return Point_rotation(self, transformation)
#        elif isinstance(transformation, Homothetie):
#            return Point_homothetie(self, transformation)
#        elif isinstance(transformation, Translation):
#            return Point_translation(self, transformation)
#        elif isinstance(transformation, Rotation):
#            return Point_rotation(self, transformation)

    def image_par(self, transformation):
        from .transformations import Translation, Homothetie, Reflexion, Rotation
        if isinstance(transformation, Rotation):
            return Point_rotation(self, transformation)
        elif isinstance(transformation, Translation):
            return Point_translation(self, transformation)
        elif isinstance(transformation, Homothetie):
            return Point_homothetie(self, transformation)
        elif isinstance(transformation, Reflexion):
            return Point_reflexion(self, transformation)
        raise NotImplementedError


    def __sub__(self, y):
        return self + (-y)


    def __add__(self, y):
        from .vecteurs import Vecteur_generique
        if isinstance(y, Vecteur_generique):
            return Point_final(self, [y])
        raise TypeError, "vecteur attendu"

    # A>B est un alias de Vecteur(A,B) - attention aux parentheses pour 2*(A>B) !
    # A ne pas utiliser en interne (code peu lisible)
    def __gt__(self, point2):
        from .vecteurs import Vecteur
        return Vecteur(self, point2)


    def _distance_inf(self, x, y, d):
        x0, y0 = self._pixel()
        return (x - x0)**2 + (y - y0)**2 < d**2


    def __eq__(self, y):
        if self.existe:
            if  isinstance(y, Point_generique) and y.existe:
                return abs(self.x - y.x) < contexte['tolerance'] and abs(self.y - y.y) < contexte['tolerance']
            elif isinstance(y, (list, tuple, ndarray)) and len(y) == 2:
                return abs(self.x - y[0]) < contexte['tolerance'] and abs(self.y - y[1]) < contexte['tolerance']
        return False

    def __ne__(self, y):
        return not (self == y)


    def relier_axe_x(self):
        if self.__feuille__ is not None:
            from .lignes import Segment
            with self.__canvas__.geler_affichage(actualiser = True):
                M = Point("%s.x" %self.nom, 0, fixe = True)
                M.label("${%s.x}$" %self.nom, formule = True)
                s = Segment(self, M, style = ":")
                self.__feuille__.objets.add(M)
                self.__feuille__.objets.add(s)

    def relier_axe_y(self):
        if self.__feuille__ is not None:
            from .lignes import Segment
            with self.__canvas__.geler_affichage(actualiser = True):
                M = Point(0, "%s.y" %self.nom, fixe = True)
                M.label("${%s.y}$" %self.nom, formule = True)
                s = Segment(self, M, style = ":")
                self.__feuille__.objets.add(M)
                self.__feuille__.objets.add(s)


    def relier_axes(self):
        if self.__feuille__ is not None:
            with self.__canvas__.geler_affichage(actualiser = True):
                self.relier_axe_x()
                self.relier_axe_y()


    @staticmethod
    def _convertir(objet):
        if hasattr(objet, "__iter__"):
            return Point(*objet)
        raise TypeError, "'" + str(type(objet)) + "' object is not iterable"




class Point(Objet_avec_coordonnees_modifiables, Point_generique):
    u"""Un point libre.

    >>> from wxgeometrie.geolib import Point
    >>> A = Point(7, 3)
    >>> print A
    Point(x = 7, y = 3)
    """

    _style_defaut = param.points_deplacables

    abscisse = x = __x = Argument("Variable_generique", defaut = lambda: normalvariate(0, 10))
    ordonnee = y = __y = Argument("Variable_generique", defaut = lambda: normalvariate(0, 10))

    def __new__(cls, *args, **kw):
        if len(args) == 1:
            from .cercles import Arc_generique, Cercle_generique
            from .lignes import Segment, Droite_generique, Demidroite
            if isinstance(args[0], Droite_generique):
                newclass = Glisseur_droite
            elif isinstance(args[0], Segment):
                newclass = Glisseur_segment
            elif isinstance(args[0], Demidroite):
                newclass = Glisseur_demidroite
            elif isinstance(args[0], Cercle_generique):
                newclass = Glisseur_cercle
            elif isinstance(args[0], Arc_generique):
                newclass = Glisseur_arc_cercle
            else:
                return object.__new__(cls)
        else:
            return object.__new__(cls)
        glisseur = newclass.__new__(newclass, *args, **kw)
        glisseur.__init__(*args, **kw)
        return glisseur

    def __init__(self, x = None, y = None, **styles):
        x, y, styles = self._recuperer_x_y(x, y, styles)
        self.__x = x = Ref(x)
        self.__y = y = Ref(y)
        Objet_avec_coordonnees_modifiables.__init__(self, x, y, **styles)
        Point_generique.__init__(self, **styles)



    def _set_feuille(self):
        xmin, xmax, ymin, ymax = self.__feuille__.fenetre
        if "_Point__x" in self._valeurs_par_defaut:
            self.__x = uniform(xmin, xmax)
#                self._valeurs_par_defaut.discard("_Point__x")
        if "_Point__y" in self._valeurs_par_defaut:
            self.__y = uniform(ymin, ymax)
#                self._valeurs_par_defaut.discard("_Point__y")
        Objet._set_feuille(self)




    def _update(self, objet):
        if not isinstance(objet, Point):
            objet = self._convertir(objet)
        if isinstance(objet, Point):
            self.coordonnees = objet.coordonnees
        else:
            raise TypeError, "L'objet n'est pas un point."







class Point_pondere(Objet):
    u"""Un point pondéré.

    Usage interne : les points pondérés sont utilisés dans la définition des barycentres."""

    point = __point = Argument("Point_generique", defaut = Point)
    coefficient = __coefficient = Argument("Variable_generique", defaut = 1)

    @staticmethod
    def _convertir(objet):
        if isinstance(objet, Point_generique):
            return Point_pondere(objet)
        elif hasattr(objet, "__iter__"):
            return Point_pondere(*objet)
        raise TypeError, "'" + str(type(objet)) + "' object is not iterable"

    def __init__(self, point = None, coefficient = None, **styles):
##        if coefficient is None:
##            coefficient = 1
        self.__point = point = Ref(point)
        self.__coefficient = coefficient = Ref(coefficient)
        Objet.__init__(self, **styles)

    def __iter__(self):
        return iter((self.__point, self.__coefficient))


class Barycentre(Point_generique):
    u"""Un barycentre.

    Un barycentre de n points."""

    points_ponderes = __points_ponderes = Arguments("Point_pondere")
    _prefixe_nom = "G"

    def __init__(self, *points_ponderes, **styles):
        if styles.get("points_ponderes", None):
            points_ponderes = styles.pop("points_ponderes")
        self.__points_ponderes = __points_ponderes = tuple(Ref(obj) for obj in points_ponderes)
        Point_generique.__init__(self, **styles)


    def _get_coordonnees(self):
        u"Coordonnées du barycentre en fonction de celles des points."
        total = self._cache.get('somme_coeff', self.__somme_coeffs)
        return sum(coeff*point.x for point, coeff in self.__points_ponderes)/total, \
                    sum(coeff*point.y for point, coeff in self.__points_ponderes)/total


    def _conditions_existence(self):
        # on le stocke pour eviter de le calculer 2 fois.
        total = self._cache.get('somme_coeff', self.__somme_coeffs)
        return abs(total) > contexte['tolerance']


    def __somme_coeffs(self):
        return sum(point_pondere._Point_pondere__coefficient.valeur for point_pondere in self.__points_ponderes)




class Milieu(Barycentre):
    u"""Un milieu.

    Le milieu de 2 points"""

    _prefixe_nom = "I"

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, **styles):
        from .lignes import Segment
        if isinstance(point1, Segment):
            point2 = point1._Segment__point2
            point1 = point1._Segment__point1
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        Barycentre.__init__(self, Point_pondere(point1, 1), Point_pondere(point2, 1), **styles)




class Point_final(Point_generique):
    u"""Un point défini par une relation vectorielle.

    Point défini par une relation vectorielle.
                              ->      ->     ->
    Exemple : point N tel que AN = -3 AB + 2 BC
    N = Point_final(A, [A>B, B>C], [-3,2])"""

    depart = __depart = Argument("Point_generique", defaut = Point)
    vecteurs = __vecteurs = Arguments("Vecteur_generique")
    coeffs = coefficients = __coefficients = Arguments("Variable_generique")

    def __init__(self, depart = None, vecteurs = (), coefficients = None, **styles):
        if coefficients == None:
            coefficients = tuple(1 for vecteur in vecteurs)
        self.__depart = depart = Ref(depart)
        self.__vecteurs = vecteurs = tuple(Ref(obj) for obj in vecteurs)
        self.__coefficients = coefficients = tuple(Ref(obj) for obj in coefficients)
        Point_generique.__init__(self, **styles)


    def _get_coordonnees(self):
        return self.__depart.x + sum(coeff*vecteur.x for coeff, vecteur in zip(self.__coefficients, self.__vecteurs)), \
                    self.__depart.y + sum(coeff*vecteur.y for coeff, vecteur in zip(self.__coefficients, self.__vecteurs))



##    def _get_coordonnees(self, exact = True):
##        x = self.__depart.x if exact else self.__depart.x.valeur_approchee
##        y = self.__depart.y if exact else self.__depart.y.valeur_approchee
##        for i in xrange(len(self.__coefficients)):
##            coeff = self.__coefficients[i] if exact else self.__coefficients[i].valeur_approchee
##            x += vecteur.x if exact else vecteur.x.valeur_approchee
##
##        if exact:
##            return self.__depart.x + sum(coeff*vecteur.x for coeff, vecteur in zip(self.__coefficients, self.__vecteurs)), \
##                        self.__depart.y + sum(coeff*vecteur.y for coeff, vecteur in zip(self.__coefficients, self.__vecteurs))
##        return self.__depart.x.valeur_approchee + sum(coeff.valeur_approchee*vecteur.x.valeur_approchee \
##                                    for coeff, vecteur in zip(self.__coefficients, self.__vecteurs)), \
##                    self.__depart.y.valeur_approchee + sum(coeff.valeur_approchee*vecteur.y.valeur_approchee \
##                                    for coeff, vecteur in zip(self.__coefficients, self.__vecteurs))





class Point_translation(Point_generique):
    u"""Une image d'un point par translation."""

    point = __point = Argument("Point_generique")
    translation = __translation = Argument("Translation")

    def __init__(self, point, translation, **styles):
        self.__point = point = Ref(point)
        self.__translation = translation = Ref(translation)
        Point_generique.__init__(self, **styles)

    def _get_coordonnees(self):
        return self.__point.x + self.__translation._Translation__vecteur.x, self.__point.y + self.__translation._Translation__vecteur.y




class Point_rotation(Point_generique):
    u"""Une image d'un point par rotation.

    Point construit à partir d'un autre via une rotation d'angle et de centre donné."""

    point = __point = Argument("Point_generique")
    rotation = __rotation = Argument("Rotation")

    def __init__(self, point, rotation, **styles):
        self.__point = point = Ref(point)
        self.__rotation = rotation = Ref(rotation)
        Point_generique.__init__(self, **styles)



    def _get_coordonnees(self):
        x0, y0 = self.__rotation.centre.coordonnees
        xA, yA = self.__point.coordonnees
        a = self.__rotation.radian
        if contexte['exact'] and issympy(a, x0, y0, xA, yA):
            sina = ssin(a) ; cosa = scos(a)
        else:
            sina = sin(a) ; cosa = cos(a)
        return (-sina*(yA - y0) + x0 + cosa*(xA - x0), y0 + cosa*(yA - y0) + sina*(xA - x0))


#    def _get_coordonnees2(self): # un poil plus lent
#        x0, y0 = self.__rotation.centre.coordonnees
#        xA, yA = self.__point.coordonnees
#        z = ((xA - x0) + (yA - y0)*1j)*cexp(1j*self.__rotation.radian) + x0 + y0*1j
#        return z.real, z.imag





class Point_homothetie(Point_generique):
    u"""Une image d'un point par homothétie.

    Point construit à partir d'un autre via une homothétie de rapport et de centre donné."""

    point = __point = Argument("Point_generique")
    homothetie = __homothetie = Argument("Homothetie")

    def __init__(self, point, homothetie, **styles):
        self.__point = point = Ref(point)
        self.__homothetie = homothetie = Ref(homothetie)
        Point_generique.__init__(self, **styles)

    def _get_coordonnees(self):
        x0, y0 = self.__homothetie.centre.coordonnees
        xA, yA = self.__point.coordonnees
        k = self.__homothetie._Homothetie__rapport
        return x0 + k*(xA - x0), y0 + k*(yA - y0)






class Point_reflexion(Point_generique):
    u"""Une image d'un point par réflexion.

    Point construit à partir d'un autre via une symétrie d'axe donné."""

    point = __point = Argument("Point_generique")
    reflexion = __reflexion = Argument("Reflexion")

    def __init__(self, point, reflexion, **styles):
        self.__point = point = Ref(point)
        self.__reflexion = reflexion = Ref(reflexion)
        Point_generique.__init__(self, **styles)


    def _get_coordonnees(self):
        x0, y0 = self.__reflexion._Reflexion__droite._Ligne_generique__point1.coordonnees
        x1, y1 = self.__reflexion._Reflexion__droite._Ligne_generique__point2.coordonnees
        x, y = self.__point
        z = x1 - x0 + (y1 - y0)*1j
        M = (x - x0 + (y0 - y)*1j)*z/z.conjugate() + x0 + y0*1j
        if contexte['exact'] and issympy(M):
            return M.expand(complex=True).as_real_imag()
        return M.real, M.imag










class Projete_generique(Point_generique):
    u"""Un projeté générique.

    Classe mère des différents types de projetés orthogonaux (sur droite, sur cercle ou sur segment)."""

    def __init__(self, point, objet, **styles):
        #~ self._initialiser(point = Point_generique, objet = Objet)
        Point_generique.__init__(self, **styles)


    @property
    def distance(self):
        return distance(self, self.__point)







class Projete_droite(Projete_generique):
    u"""Un projeté orthogonal sur une droite.

    Projeté orthogonal d'un point sur une droite."""

    point = __point = Argument("Point_generique")
    droite = __droite = Argument("Droite_generique")

    def __init__(self, point, droite, **styles):
        self.__point = point = Ref(point)
        self.__droite = droite = Ref(droite)
        Projete_generique.__init__(self, point = point, objet = droite, **styles)

    def _get_coordonnees(self):
        xA, yA = self.__droite._Droite_generique__point1.coordonnees
        xB, yB = self.__droite._Droite_generique__point2.coordonnees
        x, y = self.__point.coordonnees
        xu = xB - xA #  u = vecteur A>B
        yu = yB - yA
        xu2 = xu*xu
        yu2 = yu*yu
        AB = xu2 + yu2
        if AB > contexte['tolerance']:
            return (yu2*xA + xu2*x + xu*yu*(y - yA))/AB, (xu2*yA + yu2*y + xu*yu*(x - xA))/AB
        else:
            return xA, yA






class Projete_cercle(Projete_generique):
    u"""Un projeté orthogonal sur un cercle.

    Projeté orthogonal d'un point sur un cercle."""

    point = __point = Argument("Point_generique")
    cercle = __cercle = Argument("Cercle_generique")

    def __init__(self, point, cercle, **styles):
        self.__point = point = Ref(point)
        self.__cercle = cercle = Ref(cercle)
        Projete_generique.__init__(self, point = point, objet = cercle, **styles)

    def _conditions_existence(self):
        # cas de non existence : si le point est au centre du cercle
        return carre_distance(self.__cercle.centre, self.__point) > contexte['tolerance']**2


    def _get_coordonnees(self):
        k = angle_vectoriel((1, 0), vect(self.__cercle.centre, self.__point))
        x0, y0 = self.__cercle.centre.coordonnees
        r = self.__cercle.rayon
        if contexte['exact'] and issympy(r, x0, y0):
            return x0 + r*scos(k), y0 + r*ssin(k)
        else:
            return x0 + r*cos(k), y0 + r*sin(k)








class Projete_arc_cercle(Projete_generique):
    u"""Un projeté orthogonal sur un arc de cercle.

    Projeté orthogonal d'un point sur un arc de cercle."""

    point = __point = Argument("Point_generique")
    arc = __arc = Argument("Arc_generique")

    def __init__(self, point, arc, **styles):
        self.__point = point = Ref(point)
        self.__arc = arc = Ref(arc)
        Projete_generique.__init__(self, point = point, objet = arc, **styles)

    def _conditions_existence(self):
        # cas de non existence : si le point est au centre du cercle
        return carre_distance(self.__arc.centre.coordonnees, self.__point) > contexte['tolerance']**2


    def _get_coordonnees(self):
        M = self.__point
        arc = self.__arc
        O = arc.centre;
        a, b = arc._intervalle()
        c = angle_vectoriel((1, 0), vect(O, M))
        while c < a:
            c += 2*pi
        # La mesure d'angle c est donc dans l'intervalle [a; a+2*pi[
        if c > b: # c n'appartient pas à [a;b] (donc M est en dehors de l'arc de cercle)
            if c - b > 2*pi + a - c: # c est plus proche de a+2*pi
                c = a
            else:   # c est plus proche de b
                c = b
        if b - a < contexte['tolerance']:
            return arc.point1.coordonnees

        k = (b - c)/(b - a)
        t = a*k + b*(1 - k)
        x0, y0 = arc.centre.coordonnees
        r = arc.rayon
        if contexte['exact'] and issympy(r, x0, y0):
            return x0 +r*scos(t), y0 + r*ssin(t)
        else:
            return x0 +r*cos(t), y0 + r*sin(t)







class Projete_segment(Projete_generique):
    u"""Un projeté orthogonal sur un segment.

    Projeté orthogonal d'un point sur un segment."""

    point = __point = Argument("Point_generique")
    segment = __segment = Argument("Segment")

    def __init__(self, point, segment, **styles):
        self.__point = point = Ref(point)
        self.__segment = segment = Ref(segment)
        Projete_generique.__init__(self, point = point, objet = segment, **styles)



    def _get_coordonnees(self):
        xA, yA = A = self.__segment._Segment__point1
        xB, yB = B = self.__segment._Segment__point2
        x, y = self.__point.coordonnees
        AB2 = carre_distance(A, B)
        if AB2 > contexte['tolerance']:
            k = produit_scalaire(vect((x, y), A), vect(B, A))/AB2
            k = min(max(k, 0), 1) # on se restreint au segment
            return (1-k)*xA + k*xB, (1 - k)*yA + k*yB
        else: # A et B sont confondus
            return xA, yA







class Projete_demidroite(Projete_generique):
    u"""Un projeté orthogonal sur une demi-droite.

    Projeté orthogonal d'un point sur une demi-droite."""

    point = __point = Argument("Point_generique")
    demidroite = __demidroite = Argument("Demidroite")

    def __init__(self, point, demidroite, **styles):
        self.__point = point = Ref(point)
        self.__demidroite = demidroite = Ref(demidroite)
        Projete_generique.__init__(self, point = point, objet = demidroite, **styles)


    def _get_coordonnees(self):
        xA, yA = A = self.__demidroite._Ligne_generique__point1
        xB, yB = B = self.__demidroite._Ligne_generique__point2
        x, y = self.__point.coordonnees
        AB2 = carre_distance(A, B)
        if AB2 > contexte['tolerance']:
            k = produit_scalaire(vect((x,y), A), vect(B, A))/AB2
            k = max(k, 0) # on se restreint à la demi-droite
            return (1-k)*xA+k*xB, (1-k)*yA+k*yB
        else: # A et B sont confondus
            return xA, yA






class Centre_polygone_generique(Point_generique):
    u"""Un centre d'un triangle.

    Classe mère des différents centres d'un triangle."""


    def __init__(self, polygone, **styles):
        #~ self._initialiser(polygone = Polygone)
        Point_generique.__init__(self, **styles)






class Centre_gravite(Centre_polygone_generique):
    u"""Un centre de gravité.

    Centre de gravité d'un polygone (l'intersection des médianes dans le cas d'un triangle)."""

    _prefixe_nom = "G"

    polygone = __polygone = Argument("Polygone_generique")

    def __init__(self, polygone, **styles):
        self.__polygone = polygone = Ref(polygone)
        Centre_polygone_generique.__init__(self, polygone, **styles)

    def _conditions_existence(self):
        return self.__polygone.centre_gravite.existe

    def _get_coordonnees(self):
        return self.__polygone.centre_gravite.coordonnees






class Orthocentre(Centre_polygone_generique):
    u"""Un orthocentre.

    Orthocentre d'un triangle (intersection des hauteurs)."""

    _prefixe_nom = "H"

    triangle = __triangle = Argument("Triangle")

    def __init__(self, triangle, **styles):
        self.__triangle = triangle = Ref(triangle)
        Centre_polygone_generique.__init__(self, triangle, **styles)

    def _conditions_existence(self):
        return self.__triangle.orthocentre.existe

    def _get_coordonnees(self):
        return self.__triangle.orthocentre.coordonnees





class Centre_cercle_circonscrit(Centre_polygone_generique):
    u"""Un centre du cercle circonscrit.

    Centre du cercle circonscrit d'un triangle (intersection des médiatrices)."""

    _prefixe_nom = "O"

    triangle = __triangle = Argument("Triangle")

    def __init__(self, triangle, **styles):
        self.__triangle = triangle = Ref(triangle)
        Centre_polygone_generique.__init__(self, triangle, **styles)

    def _conditions_existence(self):
        return self.__triangle.centre_cercle_circonscrit.existe

    def _get_coordonnees(self):
        return self.__triangle.centre_cercle_circonscrit.coordonnees





class Centre_cercle_inscrit(Centre_polygone_generique):
    u"""Un centre du cercle inscrit.

    Centre du cercle inscrit d'un triangle (intersection des bissectrices)."""

    _prefixe_nom = "I"

    triangle = __triangle = Argument("Triangle")

    def __init__(self, triangle, **styles):
        self.__triangle = triangle = Ref(triangle)
        Centre_polygone_generique.__init__(self, triangle, **styles)

    def _conditions_existence(self):
        return self.__triangle.centre_cercle_inscrit.existe

    def _get_coordonnees(self):
        return self.__triangle.centre_cercle_inscrit.coordonnees





class Centre(Point_generique):
    u"""Un centre de cercle."""

    _prefixe_nom = "O"

    cercle = __cercle = Argument("Cercle_generique")

    def __init__(self, cercle, **styles):
        self.__cercle = cercle = Ref(cercle)
        Point_generique.__init__(self, **styles)

#    def _conditions_existence(self):
#        return [self.__cercle.existe]

    def _get_coordonnees(self):
        a, b, c = self.__cercle.equation
        return (-a/2, -b/2)





class Point_equidistant(Point_generique):
    u"""Point équidistant de 3 points.

    Utilisé surtout pour un usage interne, le calcul des coordonnées est plus rapide qu'en passant par les médiatrices."""

    point1 = __point1 = Argument("Point_generique")
    point2 = __point2 = Argument("Point_generique")
    point3 = __point3 = Argument("Point_generique")

    def __init__(self, point1, point2, point3, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__point3 = point3 = Ref(point3)
        Point_generique.__init__(self, **styles)

    def _conditions_existence(self):
        det2, xA, yA, xB, yB, xC, yC = self._cache.get('det2', self.__det2)
        return abs(det2) > contexte['tolerance'] \
                or abs(xB - xC) + abs(yB - yC) < contexte['tolerance'] \
                or abs(xA - xC) + abs(yA - yC) < contexte['tolerance'] \
                or abs(xB - xA) + abs(yB - yA) < contexte['tolerance']

    def _get_coordonnees(self):
        det2, xA, yA, xB, yB, xC, yC = self._cache.get('det2', self.__det2)
        if abs(det2) > contexte['tolerance']:
            a = xB - xA
            b = yB - yA
            c = xC - xB
            d = yC - yB
            p1 = a*d; p2 = b*c
            return  (p1*(xA+xB) - p2*(xB+xC) - b*d*(yC-yA))/det2, \
                    (a*c*(xC-xA) - p2*(yA+yB) + p1*(yB+yC))/det2
        elif abs(xB - xC) + abs(yB - yC) < contexte['tolerance']:
            return (.5*(xA+xB), .5*(yA+yB))
        elif abs(xA - xC) + abs(yA - yC) < contexte['tolerance']:
            return (.5*(xA+xB), .5*(yA+yB))
        elif abs(xB - xA) + abs(yB - yA) < contexte['tolerance']:
            return (.5*(xA+xC), .5*(yA+yC))

    def __det2(self):
        xA, yA = self.__point1.coordonnees
        xB, yB = self.__point2.coordonnees
        xC, yC = self.__point3.coordonnees
        return 2*((xB - xA)*(yC - yB) - (yB - yA)*(xC - xB)), xA, yA, xB, yB, xC, yC






##########################################################################################

# Glisseurs





class Glisseur_generique(Point_generique):
    u"""Un glisseur générique.

    Classe mère des différents types de glisseurs"""

    _style_defaut = param.points_deplacables

    objet = __objet = Argument("Objet")
    k = __k = Argument("Variable_generique")

    def __init__(self, objet, k, **styles):
        self.__objet = objet = Ref(objet)
        self.__k = k = Ref(k)
        Point_generique.__init__(self, **styles)

    def _initialiser_k(self, k):
        if isinstance(k, (list, tuple)):
            k = self._conversion_coordonnees_parametre(*k)
        return k

    def _set_coordonnees(self, x = None, y = None):
        if x is not None:
            self.k = self._conversion_coordonnees_parametre(x, y)


class Glisseur_vecteur(Glisseur_generique):
    u"""Un glisseur sur vecteur."""

    vecteur = __vecteur = Argument("Vecteur")
    parametre = k = __k = Argument("Variable_generique", None, lambda obj, value: max(min(value, 1), 0))

    def __init__(self, vecteur, k = None, **styles):
        if k is None:
            k = uniform(0, 1)
        self.__vecteur = vecteur = Ref(vecteur)
        self.__k = k = Ref(self._initialiser_k(k))
        Glisseur_generique.__init__(self, vecteur, k, **styles)

    def _get_coordonnees(self):
        x1, y1 = self.__vecteur._Vecteur__point1.coordonnees
        x2, y2 = self.__vecteur._Vecteur__point2.coordonnees
        k = self.__k
        return (1 - k)*x1 + k*x2, (1 - k)*y1 + k*y2

    def _conversion_coordonnees_parametre(self, x, y):
        A = self.__vecteur._Vecteur__point1; B = self.__vecteur._Vecteur__point2
        return produit_scalaire(vect((x,y), A), vect(B, A))/carre_distance(A, B)



class Glisseur_ligne_generique(Glisseur_generique):
    u"""Un glisseur générique sur ligne.

    Classe mère des différents types de glisseurs sur ligne (ie. droite, segment, demi-droite)"""

    ligne = __ligne = Argument("Ligne_generique")
    k = __k = Argument("Variable_generique")

    def __init__(self, ligne, k, **styles):
        self.__ligne = ligne = Ref(ligne)
        self.__k = k = Ref(k)
        Glisseur_generique.__init__(self, ligne, k, **styles)

    def _get_coordonnees(self):
        x1, y1 = self.__ligne._Ligne_generique__point1.coordonnees
        x2, y2 = self.__ligne._Ligne_generique__point2.coordonnees
        k = self.__k
        return (1 - k)*x1 + k*x2, (1 - k)*y1 + k*y2





class Glisseur_droite(Glisseur_ligne_generique):
    u"""Un point sur une droite.

    Point pouvant 'glisser' sur une droite. k est un coefficient barycentrique.
    Si A et B sont les deux points de référence de la droite, k le coefficient,
    les coordonnées du glisseur M seront determinées par la formule M = kA + (1-k)B."""

    droite = __droite = Argument("Droite_generique")
    parametre = k = __k = Argument("Variable_generique")

    def __init__(self, droite, k = None, **styles):
        if k is None:
            k = normalvariate(0.5, 0.5)
        self.__droite = droite = Ref(droite)
        self.__k = k = Ref(self._initialiser_k(k))
        Glisseur_ligne_generique.__init__(self, ligne = droite, k = k, **styles)



    def _conversion_coordonnees_parametre(self, x, y):
        A = self.__droite._Ligne_generique__point1; B = self.__droite._Ligne_generique__point2
        return produit_scalaire(vect((x,y), A), vect(B, A))/carre_distance(A, B)







class Glisseur_segment(Glisseur_ligne_generique):
    u"""Un point sur un segment.

    Point pouvant 'glisser' sur un segment. k est un coefficient barycentrique.
    Si A et B sont les deux points de référence de la droite, k le coefficient,
    les coordonnées du glisseur M seront determinées par la formule M = kA + (1-k)B."""

    segment = __segment = Argument("Segment")
    parametre = k = __k = Argument("Variable_generique", None, lambda obj, value: max(min(value, 1), 0))
    # la valeur du parametre doit rester comprise entre 0 et 1 (segment)

    def __init__(self, segment, k = None, **styles):
        if k is None:
            k = uniform(0, 1)
        self.__segment = segment = Ref(segment)
        self.__k = k = Ref(self._initialiser_k(k))
        Glisseur_ligne_generique.__init__(self, ligne = segment, k = k, **styles)


    def _conversion_coordonnees_parametre(self, x, y):
        A = self.__segment._Ligne_generique__point1; B = self.__segment._Ligne_generique__point2
        return produit_scalaire(vect((x,y), A), vect(B, A))/carre_distance(A, B)





class Glisseur_demidroite(Glisseur_ligne_generique):
    u"""Un point sur une demi-droite.

    Point pouvant 'glisser' sur un segment. k est un coefficient barycentrique.
    Si A et B sont les deux points de référence de la droite, k le coefficient,
    les coordonnées du glisseur M seront determinées par la formule M = kA + (1-k)B."""

    demidroite = __demidroite = Argument("Demidroite")
    parametre = k = __k = Argument("Variable_generique", None, lambda obj, value: max(value, 0))

    def __init__(self, demidroite, k = None, **styles):
        if k is None:
            k = abs(normalvariate(0.5, 0.5))
        self.__demidroite = demidroite = Ref(demidroite)
        self.__k = k = Ref(self._initialiser_k(k))
        Glisseur_ligne_generique.__init__(self, ligne = demidroite, k = k, **styles)


    def _conversion_coordonnees_parametre(self, x, y):
        A = self.__demidroite._Ligne_generique__point1; B = self.__demidroite._Ligne_generique__point2
        return produit_scalaire(vect((x,y), A), vect(B, A))/carre_distance(A, B)




class Glisseur_cercle(Glisseur_generique):
    u"""Un point sur un cercle.

    Point pouvant 'glisser' sur un cercle. k est un angle.
    Si O et r sont les centres et rayons du cercle, k l'angle,
    les coordonnées du glisseur M seront déterminées par la formule M = O + r*(cos(k), sin(k))."""

    cercle = __cercle = Argument("Cercle_generique")
    parametre = k = __k = Argument("Variable_generique")

    def __init__(self, cercle, k = None, **styles):
        if k is None:
            k = uniform(0, 2*pi)
        self.__cercle = cercle = Ref(cercle)
        self.__k = k = Ref(self._initialiser_k(k))
        Glisseur_generique.__init__(self, objet = cercle, k = k, **styles)


    def _get_coordonnees(self):
        cercle = self.__cercle
        k = self.__k
        x0, y0 = cercle.centre.coordonnees
        r = cercle.rayon
        if contexte['exact'] and issympy(r, x0, y0):
            return x0 + r*scos(k), y0 + r*ssin(k)
        else:
            return x0 + r*cos(k), y0 + r*sin(k)


    def _conversion_coordonnees_parametre(self, x, y):
        O = self.__cercle.centre
        M = (x, y)
        if O != M:
            return angle_vectoriel((1, 0), vect(O, M))
        else:
            return  0








class Glisseur_arc_cercle(Glisseur_generique):
    u"""Un point sur un arc de cercle.

    Point pouvant 'glisser' sur un cercle. k est un angle.
    Si O et r sont les centres et rayons de l'arc, k un coefficient compris entre 0 et 1,
    et a et b les mesures d'angle marquant le début et la fin de l'arc,
    les coordonnées du glisseur M seront déterminées par la formule M = O + r*(cos(ka+(1-k)b), sin(ka+(1-k)b)),
    si l'arc est de sens direct, et M = O + r*(cos(kb+(1-k)a), sin(kb+(1-k)a)) sinon."""

    arc = __arc = Argument("Arc_generique")
    parametre = k = __k = Argument("Variable_generique")

    def __init__(self, arc, k = None, **styles):
        if k is None:
            k = uniform(0, 1)
        self.__arc = arc = Ref(arc)
        self.__k = k = Ref(self._initialiser_k(k))
        Glisseur_generique.__init__(self, objet = arc, k = k, **styles)


    def _get_coordonnees(self):
        arc = self.__arc
        a, b = arc._intervalle()
        k = self.__k
        if arc._sens() == 1:
            t = a*k + b*(1 - k)
        else:
            t = b*k + a*(1 - k)
        x0, y0 = arc.centre.coordonnees
        r = arc.rayon
        if contexte['exact'] and issympy(r, x0, y0):
            return x0 + r*scos(t), y0 + r*ssin(t)
        else:
            return x0 + r*cos(t), y0 + r*sin(t)

    def _conversion_coordonnees_parametre(self, x, y):
        M = (x, y)
        O = self.__arc.centre;
        if O != M:
            a, b = self.__arc._intervalle()
            c = angle_vectoriel((1, 0), vect(O, M))
            while c < a:
                c += 2*pi
            # La mesure d'angle c est donc dans l'intervalle [a; a+2*pi[
            if c > b: # c n'appartient pas à [a;b] (donc M est en dehors de l'arc de cercle)
                if c - b > 2*pi + a - c: # c est plus proche de a+2*pi
                    c = a
                else:   # c est plus proche de b
                    c = b
            if b - a:
                if self.__arc._sens() == 1:
                    return (b - c)/(b - a)
                else:
                    return (c - a)/(b - a)
            else:
                return 0.5
        else:
            return 0



class Nuage_generique(Objet):
    u"""Un nuage de points generique.

    Usage interne : la classe mère de tous les nuages de points."""

    _prefixe_nom = "n"

    def _distance_inf(self, x, y, d):
        return any(pt._distance_inf(x, y, d) for pt in self.points)

    @property
    def points(self):
        raise NotImplementedError

    def style(self, nom_style = None, **kwargs):
        if kwargs:
            for point in self.__points:
                point.style(**kwargs)
        else:
            Objet.style(self, nom_style, **kwargs)



class Nuage(Nuage_generique):
    u"""Un nuage de points.

    Le nuage est défini par la donnée de ses points.
    """

    __points = points = Arguments('Point_generique')

    #TODO: il n'est pas possible actuellement de modifier la taille du nuage de points
    # après création. C'est une limitation de la classe Arguments().

    def __init__(self, *points, **styles):
        if styles.get('points', None):
            points = styles.pop("points")
        self.__points = points = tuple(Ref(obj) for obj in points)
        Nuage_generique.__init__(self, **styles)



class NuageFonction(Nuage_generique):
    u"""Un nuage de points de coordonnées (x; f(x)).

    Le nuage est défini par la donnée de la fonction f,
    et d'une liste d'abscisses.
    """

    __fonction = fonction = Argument('Fonction')
    __abscisses = abscisses = Arguments('Variable_generique')

    def __init__(self, fonction, *abscisses, **styles):
        if styles.get('abscisses', None):
            points = styles.pop('abscisses')
        self.__points = points = tuple(Ref(obj) for obj in points)
        Nuage_generique.__init__(self, **styles)
