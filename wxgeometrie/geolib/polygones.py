# -*- coding: utf-8 -*-

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
from random import uniform, normalvariate, randint
from math import pi, cos, sin
from cmath import log as clog, exp as cexp

from sympy import arg as sarg, exp as sexp, I

from .intersections import Intersection_droites
from .labels import Label_polygone
from .lignes import Segment, Perpendiculaire, Bissectrice, Droite
from .objet import Arguments, Argument, ArgumentNonModifiable, Ref, Objet, \
                   contexte, issympy, FILL_STYLES, RE_NOM_OBJET, TYPES_ENTIERS
from .points import Point_generique, Point, Point_equidistant, Point_pondere, \
                    Barycentre
from .transformations import Rotation
from .routines import point_dans_polygone, distance, radian

from ..pylib import is_in, print_error
from .. import param




class Cote(Segment):
    """Un coté.

    Un coté d'un polygone, reliant le point numero 'n' au point numero 'n + 1'.
    Note: n commence à 0.
    L'objet est créé automatiquement lors de la création du polygone.
    De plus, si l'objet est supprimé, le polygone est automatiquement supprimé."""

    _style_defaut = param.cotes
    _prefixe_nom = "c"

    polygone = __polygone = ArgumentNonModifiable("Polygone_generique")
    n = __n = ArgumentNonModifiable("int")

    def __new__(cls, polygone, n, **styles):
        try:
            # Si le côté existe déjà, on retourne simplement le côté existant.
            # Ceci évite de créer en double le même côté, lorsque la feuille
            # est sauvegardée puis rechargée. En effet, lors du chargement de la
            # feuille, des côtés vont être créés automatiquement à la création
            # du polygone, puis de nouveau lorsque `c0 = Cote(p, 0, ...)` va
            # être exécuté.
            return polygone.cotes[n]
            # Attention, Cote.__init__() va être appelé de nouveau !
        except (AttributeError, IndexError):
            cote = object.__new__(cls)
            return cote

    def __init__(self, polygone, n, **styles):
        if not self._initialise:
            self.__polygone = polygone
            self.__n = n
            sommets = polygone._Polygone_generique__sommets
            Segment.__init__(self, sommets[n], sommets[(n + 1)%len(sommets)], **styles)
        else:
            self.style(**styles)

    def _modifier_hierarchie(self, valeur = None):
        # Voir commentaires pour Sommet._modifier_hierarchie
        N = len(self.__polygone._Polygone_generique__points)
        Objet._modifier_hierarchie(self, self.__polygone._hierarchie + (self.__n + N + 2)/(2*N + 2))

    def supprimer(self):
        """Supprime le polygone auquel appartient le côté.

        ..note::
            Il n'y a aucun intérêt à supprimer uniquement le côté
            (d'autant qu'un côté supprimé ne peut pas facilement être
            rétabli), et si un côté est supprimé sans le polygone, on a parfois
            l'impression d'un bug (impossible de placer un point sur le côté par
            exemple)."""
        self.__polygone.supprimer()


# Pourquoi une classe Sommet ?
# - afin de clarifier l'affichage de geolib (par ex, pour un parallélogramme,
#   le titre "Sommet S1" est plus explicite que "Barycentre S1",
#   qui reflète des détails d'implémentation).
# - pour des questions de dépendance : le sommet S1 dépend du parallélogramme, alors
#   que le barycentre qui est utilisé pour la construction ne dépend que des
#   3 autres points du parallélogramme.



class Sommet(Point_generique):
    """Un sommet.

    Le nième sommet d'un polygone.

    .. note:: n commence à 0.

    L'objet est créé automatiquement lors de la création du polygone.
    De plus, si l'objet est supprimé, le polygone est automatiquement supprimé."""

    _prefixe_nom = "S"

    # Un sommet peut-être lié à un point, c'est-à-dire avoir toujours les mêmes coordonnées que ce point
    _point_lie = None

    polygone = __polygone = ArgumentNonModifiable("Polygone_generique")
    n = __n = ArgumentNonModifiable("int")

    def __new__(cls, polygone, n, **styles):
        try:
            # Si le sommet existe déjà, on retourne simplement le sommet existant.
            # Ceci évite de créer en double le même sommet, lorsque la feuille
            # est sauvegardée puis rechargée. En effet, lors du chargement de la
            # feuille, des sommets vont être créés automatiquement à la création
            # du polygone, puis de nouveau lorsque `S0 = Sommet(p, 0, ...)` va
            # être exécuté.
            return polygone.sommets[n]
            # Attention, Sommet.__init__() va être appelé de nouveau !
        except (AttributeError, IndexError):
            sommet = object.__new__(cls)
            return sommet

    def __init__(self, polygone, n, **styles):
        if not self._initialise:
            self.__polygone = polygone
            self.__n = n
            Point_generique.__init__(self, **styles)
        else:
            self.style(**styles)

    def _get_coordonnees(self):
        return self.__polygone._Polygone_generique__points[self.__n].coordonnees

    def _set_coordonnees(self, x, y):
        if self._point_lie is not None:
            self._point_lie._set_coordonnees(x, y)

    def _modifier_hierarchie(self, valeur = None):
        # Pour les sauvegardes par exemple, il est préférable que les sommets, puis les cotés,
        # apparaissent juste après la construction du polygone ; ils doivent occuper des places consécutives dans la hiérarchie.
        # Par exemple, si le polygone a 4 sommets, et si sa place dans la hierarchie est 18, ses trois sommets
        # auront  comme valeur hierarchique, dans l'ordre, 18.1, 18.2, 18.3 et 18.4,
        # et ses cotés auront pour valeur hiérarchique 18.6, 18.7, 18.8, 18.9.
        poly = self.__polygone
        N = len(poly._Polygone_generique__points)
        Objet._modifier_hierarchie(self, poly._hierarchie + (self.__n + 1)/(2*N + 2))

    def _lier_sommet(self, point):
        """Lie le sommet à un point, en le rendant déplaçable."""
        self._point_lie = point
        self.style(couleur = "m")

    def _deplacable(self, *args, **kw):
        return self._point_lie is not None

    _deplacable = _modifiable = property(_deplacable, _deplacable)

    def supprimer(self):
        """Supprime le polygone auquel appartient le sommet.

        .. note::
            Il n'y a aucun intérêt à supprimer uniquement le sommet
            (d'autant qu'un sommet supprimé ne peut pas facilement être
            rétabli)."""
        self.__polygone.supprimer()



class Polygone_generique(Objet):
    """Un polygone générique.

    Classe mère de tous les polygones."""

    _style_defaut = param.polygones
    _prefixe_nom = "p"

    points = __points = Arguments("Point_generique")

    def __init__(self, *points, **styles):
        n = len(points)
        self.__points = points = tuple(Ref(obj) for obj in points)
        self.__centre = Barycentre(*(Point_pondere(point, 1) for point in points))
        Objet.__init__(self, **styles)
        self.etiquette = Label_polygone(self)
        self.__sommets = tuple(Sommet(self, i) for i in range(n))
        self.__cotes = tuple(Cote(self, i) for i in range(n))


    def _affecter_coordonnees_par_defaut(self, points):
        """Affecte aux points des coordonnées par défaut.

       Les coordonnées aléatoires sont générées manière à ce que le polygone
       ait peu de chance d'être croisé, et occupe une bonne partie de la fenêtre d'affichage."""
        xmin, xmax, ymin, ymax = self.feuille.fenetre
        x0 = (xmin + xmax)/2
        y0 = (ymin + ymax)/2
        rx = (xmax - xmin)/2
        ry = (ymax - ymin)/2
        r = min(rx, ry)
        liste_k = [uniform(0.5*r, 1*r) for pt in points]
        # Par défaut, pour éviter les polygones croisés, on construit les sommets successifs
        # en rayonnant dans le sens direct à partir du centre de la fenêtre.
        # Nota: si toutes les valeurs de liste_t étaient regroupées sur un intervalle
        # d'amplitude < pi, il se pourrait que le polygone soit malgré tout croisé, d'où l'algorithme suivant :
        if len(points) == 3:
            liste_t = [uniform(0, pi/3),
                            uniform(2*pi/3, pi),
                            uniform(4*pi/3, 5*pi/3)]
        else:
            liste_t = [uniform(0, pi/2),
                            uniform(pi/2, pi),
                            uniform(pi, 3*pi/2),
                            uniform(3*pi/2, 2*pi)]
            liste_t += [uniform(0, 2*pi) for i in range(len(points) - 4)]
        for (k, t, pt) in zip(liste_k, liste_t, points):
            pt._Point__x = x0 + k*cos(t)
            pt._Point__y = y0 + k*sin(t)


    def on_register(self):
        """Enregistre les côtés et les sommets du polygone dans la feuille lors
        de l'enregistrement du polygone."""
        # On enregistre tous les côtés dans la feuille.
        for cote in self.__cotes:
            self.feuille.objets.add(cote)

        # on enregistre ensuite les sommets.
        # On essaie de nommer intelligemment les sommets.
        # Par exemple, si un rectangle s'appelle ABCD, les points libres
        # s'appelleront si possible A et B, et les deux autres sommets
        # s'appelleront C et D.
        sommets = []
        noms_args, args = zip(*self._iter_arguments)
        for sommet, point in zip(self.__sommets, self.__points):
            sommets.append(point if is_in(point, args) else sommet)

        n = len(sommets)

        noms = re.findall(RE_NOM_OBJET, self._nom)
        if ''.join(noms) == self._nom and len(noms) == n:
            for sommet, nom in zip(sommets, noms):
                if sommet._nom and sommet._nom != nom:
                    noms = n*['']
                    break
        else:
            noms = n*['']

        add = self.feuille.objets.add
        for sommet, nom in zip(sommets, noms):
            if not sommet._nom:
                add(sommet, nom_suggere=nom)

        if self._valeurs_par_defaut:
            # Par défaut, on essaie d'éviter un polygone croisé, à l'aide
            # de la méthode `._affecter_coordonnees_par_defaut()`.
            if len(args) == n:
                if all(isinstance(arg, Point) for arg in args):
                    self._affecter_coordonnees_par_defaut(args)
            self._valeurs_par_defaut = []


    @property
    def centre(self):
        return self.__centre

    centre_gravite = centre

    @property
    def sommets(self):
        return self.__sommets

    @property
    def cotes(self):
        return self.__cotes


    @property
    def equilateral(self):
        longueurs_cotes = tuple(cote.longueur for cote in self.__cotes)
        return max(longueurs_cotes) - min(longueurs_cotes) < contexte['tolerance']

    @property
    def regulier(self):
        G = self.__centre # centre de gravité
        distance_centre = tuple(distance(G, sommet) for sommet in self.__points)
        return self.equilateral and self.convexe and max(distance_centre) - min(distance_centre) < contexte['tolerance']

    @property
    def inscrit(self):
        "Le polygone est-il inscrit dans un cercle ?"
        raise NotImplementedError

    @property
    def convexe(self):
        def sens_angle(A, B, C):
            return (C.x - B.x)*(A.y - B.y) - (A.x - B.x)*(C.y - B.y) > 0
        sens_initial = None
        i = -2
        j = -1
        for k in range(len(self.__points)):
            A = self.__points[i]
            B = self.__points[j]
            C = self.__points[k]
            sens = sens_angle(A, B, C)
            if sens_initial == None:
                sens_initial = sens
            if sens != sens_initial:
                return False
            i = j
            j = k
        return True


    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.polygone(), self.rendu.ligne(zorder = 1)]

        fill = self._representation[0]
        plot = self._representation[1]
        niveau = self.style("niveau")
        hachures = self.style("hachures")
        alpha = self.style("alpha")
        couleur = self.style("couleur")
        style = self.style("style")
        epaisseur = self.style("epaisseur")
        points = self.__points + (self.__points[0],)
        xy = [pt.coordonnees for pt in points]
        x, y = zip(*xy)
        fill.xy = xy
        plot.set_data(x, y)
        fill.set(alpha=alpha, hatch=hachures, edgecolor=couleur, facecolor=couleur, linewidth=epaisseur)
        plot.set(color=couleur, linestyle=style, linewidth=epaisseur)
        fill.set_linestyle(FILL_STYLES.get(self.style("style"), "solid"))
        fill.zorder = niveau - 0.01
        plot.zorder = niveau


    def image_par(self, transformation):
        return Polygone(*(point.image_par(transformation) for point in self.__points))


    def _distance_inf(self, x, y, d):
        xy = [self._pixel(pt) for pt in self.__points]
        return point_dans_polygone((x,y), xy)

    def _contains(self, M):
        for cote in self.cotes:
            if M in cote:
                return True
        return point_dans_polygone(tuple(M), [pt.coordonnees for pt in self.__points])

    @property
    def aire(self):
        """D'après David Chandler, Area of a general polygon.
        http://www.davidchandler.com/AreaOfAGeneralPolygon.pdf"""

        if self.existe:
            points = self.__points
            xy = [pt.coordonnees for pt in (points + (points[0],))]
            s1 = s2 = 0
            for i in range(len(points)):
                s1 += xy[i][0]*xy[i+1][1]
                s2 += xy[i][1]*xy[i+1][0]
            return abs(s1 - s2)/2
        return None

    @property
    def info(self):
        return self.nom_complet + " d'aire " + str(self.aire)

    @property
    def perimetre(self):
        return sum(cote.longueur for cote in self.__cotes)

    def _espace_vital(self):
        points = self.__points
        x1 = min(pt.abscisse for pt in points)
        x2 = max(pt.abscisse for pt in points)
        y1 = min(pt.ordonnee for pt in points)
        y2 = max(pt.ordonnee for pt in points)
        return (x1, x2, y1, y2)





class Polygone(Polygone_generique):
    """Un polygone.

    Un polygone défini par ses sommets."""

    _points_crees_automatiquement = False

    def __new__(cls, *points, **styles):
        if styles.get("points", None):
            points = styles.pop("points")
        n = len(points)
        if not n:
            n = styles.pop("n", 3+abs(int(normalvariate(0,4))))
        if n == 1:
            if isinstance(points[0], (list, tuple)):
                points = tuple(points[0])
                n = len(points)
            elif isinstance(points[0], TYPES_ENTIERS):
                n = points[0]
                points = ()
        # Attention, pas de 'elif' ici, 'n' a pu changer de valeur !
        if n == 2:
            newclass = Segment
        elif n == 3:
            newclass = Triangle
        elif n == 4:
            newclass = Quadrilatere
        elif n == 5 :
            newclass = Pentagone
        elif n == 6 :
            newclass = Hexagone
        elif n == 7 :
            newclass = Heptagone
        elif n == 8 :
            newclass = Octogone
        else:
            return object.__new__(cls)
        objet = newclass.__new__(newclass, *points, **styles)
        objet.__init__(*points, **styles)
        return objet


    points = __points = Arguments("Point_generique")


    def __init__(self, *points, **styles):
        self._points_crees_automatiquement = False
        if styles.get("points", None):
            points = styles.pop("points")
        if not points:
            points = (styles.pop("n", 3 + abs(int(normalvariate(0,4)))), )
        if len(points) == 1:
            if isinstance(points[0], (list, tuple)):
                points = tuple(points[0])
            elif isinstance(points[0], TYPES_ENTIERS):
                points = tuple(Point() for i in range(points[0]))
                self._points_crees_automatiquement = True
        self.__points = points = tuple(Ref(obj) for obj in points)
        Polygone_generique.__init__(self, *points, **styles)


    def on_register(self):
        if self._points_crees_automatiquement:
            args = self.__points
            self._affecter_coordonnees_par_defaut(args)
            # Nommage intelligent des sommets par défaut
            noms = re.findall(RE_NOM_OBJET, self._nom)
            if "".join(noms) != self._nom or len(args) != len(noms):
                noms = len(args)*['']
            for arg, nom in zip(args, noms):
                self.feuille.objets.add(arg, nom_suggere=nom)


class Triangle(Polygone_generique):
    """Un triangle."""

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    point3 = __point3 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, point3 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__point3 = point3 = Ref(point3)
        Polygone_generique.__init__(self, point1, point2, point3, **styles)
        d1 = Perpendiculaire(Droite(point1, point2), point3)
        d2 = Perpendiculaire(Droite(point2, point3), point1)
        self.orthocentre = Intersection_droites(d1, d2)
        self.centre_cercle_circonscrit = Point_equidistant(point1, point2, point3)
        d1 = Bissectrice(point1, point2, point3)
        d2 = Bissectrice(point3, point1, point2)
        self.centre_cercle_inscrit = Intersection_droites(d1, d2)

    @property
    def rectangle(self):
        a, b, c = sorted(cote.longueur for cote in self._Polygone_generique__cotes)
        return abs(a**2 + b**2 - c**2) < contexte['tolerance']


    @property
    def isocele(self):
        a, b, c = sorted(cote.longueur for cote in self._Polygone_generique__cotes)
        return (b - a) < contexte['tolerance'] or (c - b) < contexte['tolerance']

    @property
    def inscrit(self):
        "Le polygone est-il inscrit dans un cercle ?"
        return True

    @property
    def convexe(self):
        return True

    @property
    def regulier(self):
        return True



class Quadrilatere(Polygone_generique):
    """Un quadrilatère."""

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    point3 = __point3 = Argument("Point_generique", defaut = Point)
    point4 = __point4 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, point3 = None, point4 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__point3 = point3 = Ref(point3)
        self.__point4 = point4 = Ref(point4)
        Polygone_generique.__init__(self, point1, point2, point3, point4, **styles)

    #TODO: compléter ces méthodes et les tester (tests unitaires)
    @property
    def carre(self):
        return self.losange and self.rectangle

    @property
    def losange(self):
        return self.equilateral

    @property
    def rectangle(self):
        A, B, C, D = self._Polygone_generique__sommets
        zAB = B.z - A.z
        zDC = C.z - D.z
        zAD = D.z - A.z
        # Parallélogramme avec un angle droit.
        return abs(zAB - zDC) < contexte['tolerance'] and abs((zAB*zAD.conjugate()).real) < contexte['tolerance']

    @property
    def parallelogramme(self):
        A, B, C, D = self._Polygone_generique__sommets
        zAB = B.z - A.z
        zDC = C.z - D.z
        return abs(zAB - zDC) < contexte['tolerance']

    @property
    def trapeze(self):
        A, B, C, D = self._Polygone_generique__sommets
        zAB = B.z - A.z
        zDC = C.z - D.z
        zAD = D.z - A.z
        zBC = C.z - B.z
        return abs((zAB*zDC.conjugate()).imag) < contexte['tolerance'] or abs((zAD*zBC.conjugate()).imag) < contexte['tolerance']

    @property
    def croise(self):
        raise NotImplementedError


class Pentagone(Polygone_generique):
    """Un pentagone."""

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    point3 = __point3 = Argument("Point_generique", defaut = Point)
    point4 = __point4 = Argument("Point_generique", defaut = Point)
    point5 = __point5 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, point3 = None, point4 = None, point5 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__point3 = point3 = Ref(point3)
        self.__point4 = point4 = Ref(point4)
        self.__point5 = point5 = Ref(point5)
        Polygone_generique.__init__(self, point1, point2, point3, point4, point5, **styles)




class Hexagone(Polygone_generique):
    """Un hexagone."""

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    point3 = __point3 = Argument("Point_generique", defaut = Point)
    point4 = __point4 = Argument("Point_generique", defaut = Point)
    point5 = __point5 = Argument("Point_generique", defaut = Point)
    point6 = __point6 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, point3 = None, point4 = None, point5 = None, point6 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__point3 = point3 = Ref(point3)
        self.__point4 = point4 = Ref(point4)
        self.__point5 = point5 = Ref(point5)
        self.__point6 = point6 = Ref(point6)
        Polygone_generique.__init__(self, point1, point2, point3, point4, point5, point6, **styles)




class Heptagone(Polygone_generique):
    """Un heptagone."""

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    point3 = __point3 = Argument("Point_generique", defaut = Point)
    point4 = __point4 = Argument("Point_generique", defaut = Point)
    point5 = __point5 = Argument("Point_generique", defaut = Point)
    point6 = __point6 = Argument("Point_generique", defaut = Point)
    point7 = __point7 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, point3 = None, point4 = None, point5 = None, point6 = None, point7 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__point3 = point3 = Ref(point3)
        self.__point4 = point4 = Ref(point4)
        self.__point5 = point5 = Ref(point5)
        self.__point6 = point6 = Ref(point6)
        self.__point7 = point7 = Ref(point7)
        Polygone_generique.__init__(self, point1, point2, point3, point4, point5, point6, point7, **styles)




class Octogone(Polygone_generique):
    """Un octogone."""

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    point3 = __point3 = Argument("Point_generique", defaut = Point)
    point4 = __point4 = Argument("Point_generique", defaut = Point)
    point5 = __point5 = Argument("Point_generique", defaut = Point)
    point6 = __point6 = Argument("Point_generique", defaut = Point)
    point7 = __point7 = Argument("Point_generique", defaut = Point)
    point8 = __point8 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, point3 = None, point4 = None, point5 = None, point6 = None, point7 = None, point8 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__point3 = point3 = Ref(point3)
        self.__point4 = point4 = Ref(point4)
        self.__point5 = point5 = Ref(point5)
        self.__point6 = point6 = Ref(point6)
        self.__point7 = point7 = Ref(point7)
        self.__point8 = point8 = Ref(point8)
        Polygone_generique.__init__(self, point1, point2, point3, point4, point5, point6, point7, point8, **styles)




class Parallelogramme(Quadrilatere):
    """Un parallélogramme."""

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    point3 = __point3 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, point3 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__point3 = point3 = Ref(point3)
        Quadrilatere.__init__(self, point1, point2, point3, Barycentre(Point_pondere(point1, 1), Point_pondere(point2, -1), Point_pondere(point3, 1)), **styles)





class Sommet_rectangle(Point_generique):
    """Un sommet d'un rectangle.

    (Usage interne)."""

    _style_defaut = param.points_deplacables

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    rapport = __rapport = Argument("Variable_generique", defaut = lambda:uniform(.4, .8))

    def __init__(self, point1, point2, rapport, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__rapport = rapport = Ref(rapport)
        Point_generique.__init__(self, **styles)

    def _get_coordonnees(self):
        k = self.__rapport
        zA = self.__point1.z
        zB = self.__point2.z
        zBC = (zB - zA)*1j*k
        zC = zB + zBC
        return zC.real, zC.imag

    def _set_coordonnees(self, x, y):
        zA = self.__point1.z
        zB = self.__point2.z
        z = x + 1j*y
        try:
            zAB = zB - zA
            # vecteur normal à A>B (sens direct)
            zn = zAB*1j
            if issympy(zAB):
                p = ((z - zB)*zn.conjugate()).expand(complex=True).as_real_imag()[1]
                self.__rapport = p/((zAB*zAB.conjugate()).expand(complex=True).as_real_imag()[1])
            else:
                # produit scalaire
                p = ((z - zB)*zn.conjugate()).real
                # on divise par |zAB|²
                self.__rapport = p/((zAB*zAB.conjugate()).real)
        except (OverflowError, ZeroDivisionError):
            if param.debug:
                print_error()



class Rectangle(Parallelogramme):
    """Un rectangle."""

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    rapport = __rapport = Argument("Variable_generique", defaut = lambda:uniform(.4, .8) + randint(0, 1))

    def __init__(self, point1 = None, point2 = None, rapport = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__rapport = rapport = Ref(rapport)
        Parallelogramme.__init__(self, point1, point2, Sommet_rectangle(point1, point2, rapport), **styles)
        # Hack infâme, pour lier le 3e sommet à l'objet 'Sommet_triangle_rectangle'
        self._Polygone_generique__sommets[2]._lier_sommet(self._Quadrilatere__point3)


class Losange(Parallelogramme):
    """Un losange."""

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    angle = __angle = Argument("Angle_generique", defaut = lambda:radian(uniform(pi/6, pi/4) + randint(0, 1)*pi/2))

    def __init__(self, point1 = None, point2 = None, angle = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__angle = angle = Ref(angle)
        Parallelogramme.__init__(self, Sommet_triangle_isocele(point1, point2, angle), point1, point2, **styles)
        # Hack infâme, pour lier le 3e sommet à l'objet 'Sommet_triangle_isocele'
        self._Polygone_generique__sommets[0]._lier_sommet(self._Quadrilatere__point1)







class Polygone_regulier_centre(Polygone_generique):
    """Un polygone régulier.

    Un polygone régulier défini par son centre, un sommet, et le nombre de côtés."""

    def __new__(cls, centre = None, sommet = None, n = None, **styles):
        if n is None:
            n = 3 + abs(int(normalvariate(0,4)))
        if n == 3:
            newclass = Triangle_equilateral_centre
        elif n == 4:
            newclass = Carre_centre
        else:
            return object.__new__(cls)
        objet = newclass.__new__(newclass, centre, sommet, **styles)
        objet.__init__(centre, sommet, **styles)
        return objet

    centre = __centre = Argument("Point_generique", defaut = Point)
    sommet = __sommet = Argument("Point_generique", defaut = Point)
    n = __n = ArgumentNonModifiable("int")

    def __init__(self, centre = None, sommet = None, n = None, **styles):
        self.__centre = centre = Ref(centre)
        self.__sommet = sommet = Ref(sommet)
        if n is None:
            n = 3 + abs(int(normalvariate(0,4)))
        # il ne faut pas utiliser de référence (Ref), car n n'est pas modifiable :
        self.__n = n
        points = (Rotation(centre, '2*pi*' + str(i) + '/' + str(n), unite='r')(sommet) for i in range(1, n))
        Polygone_generique.__init__(self, sommet, *points, **styles)







class Triangle_equilateral_centre(Triangle):
    """Un triangle équilatéral.

    Un triangle équilatéral défini par son centre et un sommet."""

    centre = __centre = Argument("Point_generique", defaut = Point)
    sommet = __sommet = Argument("Point_generique", defaut = Point)

    def __init__(self, centre = None, sommet = None, **styles):
        self.__centre = centre = Ref(centre)
        self.__sommet = sommet = Ref(sommet)
        Triangle.__init__(self, sommet, Rotation(centre, '2*pi/3', unite='r')(sommet),
                          Rotation(centre, '4*pi/3', unite='r')(sommet), **styles)






class Carre_centre(Quadrilatere):
    """Un carré.

    Un carré défini par son centre et un sommet."""

    centre = __centre = Argument("Point_generique", defaut = Point)
    sommet = __sommet = Argument("Point_generique", defaut = Point)

    def __init__(self, centre = None, sommet = None, **styles):
        self.__centre = centre = Ref(centre)
        self.__sommet = sommet = Ref(sommet)
        Quadrilatere.__init__(self, sommet, Rotation(centre, 'pi/2', unite='r')(sommet),
                              Rotation(centre, 'pi', unite='r')(sommet),
                              Rotation(centre, '3*pi/2', unite='r')(sommet), **styles)









class Polygone_regulier(Polygone_generique):
    """Un polygone régulier.

    Un polygone régulier défini par deux points consécutif (sens direct)."""

    def __new__(cls, point1 = None, point2 = None, n = None,  **styles):
        if n is None:
            n = 3 + abs(int(normalvariate(0,4)))
        if n == 3:
            return Triangle_equilateral(point1, point2, **styles)
        elif n == 4:
            return Carre(point1, point2, **styles)
        else:
            return object.__new__(cls)

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    n = __n = ArgumentNonModifiable("int")


    def __init__(self, point1 = None, point2 = None, n = 6, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        if n is None:
            n = 3 + abs(int(normalvariate(0,4)))
        # il ne faut pas utiliser de référence (Ref), car n n'est pas modifiable :
        self.__n = n
        angle = '(2-' + str(n) + ')*pi/' + str(n)
        point3 = Rotation(point2, angle, unite='r')(point1)
        # Auparavant, tous les sommets étaient construits ainsi récursivement
        # mais la taille de str(Polygone_regulier.points[i])
        # croissait alors exponentiellement avec i (elle doublait à chaque itération) !
        points = [point1, point2, point3]
        self.__centre = centre = Point_equidistant(point1, point2, point3)
        for i in range(3, n):
            angle = '2*pi*' + str(i) + '/' + str(n)
            points.append(Rotation(centre, angle, unite='r')(point1))
        Polygone_generique.__init__(self, *points, **styles)

    @property
    def centre(self):
        return self.__centre



class Triangle_equilateral(Triangle):
    """Un triangle équilatéral.

    Un triangle équilatéral défini par deux points consécutif (sens direct)."""

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        Triangle.__init__(self, point1, point2, Rotation(point1, 'pi/3', unite='r')(point2), **styles)






class Carre(Quadrilatere):
    """Un carré.

    Un carré défini par deux points consécutif (sens direct)."""

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        point3 = Rotation(point2, '-pi/2', unite='r')(point1)
        Quadrilatere.__init__(self, point1, point2, point3, Rotation(point1, 'pi/2', unite='r')(point2), **styles)



class Sommet_triangle_isocele(Point_generique):
    """Un sommet d'un triangle isocèle.

    Le 3e sommet du triangle isocele (un des sommets de la base).
    (Usage interne)."""

    _style_defaut = param.points_deplacables

    sommet_principal = __sommet_principal = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    angle = __angle = Argument("Angle_generique", defaut = lambda:radian(uniform(pi/6, pi/4) + randint(0, 1)*pi/2))

    def __init__(self, sommet_principal, point2, angle, **styles):
        self.__sommet_principal = sommet_principal = Ref(sommet_principal)
        self.__point2 = point2 = Ref(point2)
        self.__angle = angle = Ref(angle)
        Point_generique.__init__(self, **styles)

    def _get_coordonnees(self):
        a = self.__angle.radian
        zA = self.__sommet_principal.z
        zB = self.__point2.z
        if contexte['exact'] and issympy(a, zA, zB):
            zC = (zB - zA)*sexp(1j*a) + zA
            return zC.expand(complex=True).as_real_imag()
        else:
            zC = (zB - zA)*cexp(1j*a) + zA
            return zC.real, zC.imag

    def _set_coordonnees(self, x, y):
        with contexte(unite_angle='r'):
            zA = self.__sommet_principal.z
            zB = self.__point2.z
            z = x + 1j*y
            try:
                if issympy(zA, zB):
                    self.__angle = sarg((z - zA)/(zB - zA))
                else:
                    self.__angle = clog((z - zA)/(zB - zA)).imag
            except (OverflowError, ZeroDivisionError):
                if param.debug:
                    print_error()



class Triangle_isocele(Triangle):
    """Un triangle isocèle.

    Un triangle isocèle défini par son sommet principal, un autre sommet, et son angle principal (sens direct)."""

    sommet_principal = __sommet_principal = Argument("Point_generique", defaut=Point)
    point2 = __point2 = Argument("Point_generique", defaut=Point)
    angle = __angle = Argument("Angle_generique", defaut = lambda:radian(uniform(pi/6, pi/4) + randint(0, 1)*pi/2))

    def __init__(self, sommet_principal = None, point2 = None, angle = None, **styles):
        self.__sommet_principal = sommet_principal = Ref(sommet_principal)
        self.__point2 = point2 = Ref(point2)
        self.__angle = angle = Ref(angle)
        Triangle.__init__(self, sommet_principal, point2, Sommet_triangle_isocele(sommet_principal, point2, angle), **styles)
        # Hack infâme, pour lier le 3e sommet à l'objet 'Sommet_triangle_isocele'
        self._Polygone_generique__sommets[-1]._lier_sommet(self._Triangle__point3)


class Sommet_triangle_rectangle(Point_generique):
    """Un sommet d'un triangle rectangle.

    Le sommet opposé à l'hypothénuse du triangle rectangle.
    (Usage interne)."""

    _style_defaut = param.points_deplacables

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    angle = __angle = Argument("Angle_generique", defaut = lambda:radian(uniform(pi/6, pi/3)))

    def __init__(self, point1, point2, angle, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__angle = angle = Ref(angle)
        Point_generique.__init__(self, **styles)

    def _get_coordonnees(self):
        a = self.__angle.radian
        zA = self.__point1.z
        zB = self.__point2.z
        zI = (zA + zB)/2
        if contexte['exact'] and issympy(a, zI):
            zC = (zB - zI)*sexp(I*2*a) + zI
            return zC.expand(complex=True).as_real_imag()
        else:
            zC = (zB - zI)*cexp(1j*2*a) + zI
            return zC.real, zC.imag

    def _set_coordonnees(self, x, y):
        with contexte(unite_angle='r'):
            zA = self.__point1.z
            zB = self.__point2.z
            zI = (zA + zB)/2
            z = x + 1j*y
            try:
                if issympy(zI):
                    self.__angle = sarg((z - zI)/(zB - zI))/2
                else:
                    self.__angle = clog((z - zI)/(zB - zI)).imag/2
            except (OverflowError, ZeroDivisionError):
                if param.debug:
                    print_error()



class Triangle_rectangle(Triangle):
    """Un triangle rectangle.

    Un triangle rectangle défini par les extrémités de son hypothénuse (sens direct), et un de ses angles aigus."""

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    angle = __angle = Argument("Angle_generique", defaut = lambda:radian(uniform(pi/7, pi/5)))

    def __init__(self, point1 = None, point2 = None, angle = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__angle = angle = Ref(angle)
        Triangle.__init__(self, point1, point2, Sommet_triangle_rectangle(point1, point2, angle), **styles)
        # Hack infâme, pour lier le 3e sommet à l'objet 'Sommet_triangle_rectangle'
        self._Polygone_generique__sommets[-1]._lier_sommet(self._Triangle__point3)





class Triangle_isocele_rectangle(Triangle):
    """Un triangle isocèle rectangle.

    Un triangle isocèle rectangle défini par les extrémités de son hypothénuse (sens direct)."""

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)

    def __init__(self, point1 = None, point2 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        Triangle.__init__(self, point1, point2, Sommet_triangle_rectangle(point1, point2, 'pi/4'), **styles)




class PrevisualisationPolygone(Polygone_generique):
    """Une forme de polygone utilisée uniquement pour la prévisualisation.

    Usage interne."""

    def _get_points(self):
        return self.__points

    def _set_points(self, points):
        for pt in self.__points:
            pt.enfants.remove(self)
        for pt in points:
            pt.enfants.add(self)
        # NOTE: self.__points doit être de type tuple et surtout pas liste
        # (une éventuelle modification de la liste ne gererait pas correctement les vassaux)
        self.__points = points
##        self.creer_figure()
        self.figure_perimee()

    # Exceptionnellement, on ne passe par un objet 'Arguments' ici (le but étant d'être le plus rapide possible).
    points = property(_get_points, _set_points)

    # De même, inutile de passer par un descripteur de type 'DescripteurFeuille' pour l'attribut '__feuille__'
    feuille = None

    def __init__(self, *points):
        Objet.__init__(self)
        self.__points = ()
        self.points = points

    def style(self, nom):
        return param.polygones.get(nom, None)


    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.polygone(), self.rendu.ligne(zorder = 1)]

        fill = self._representation[0]
        plot = self._representation[1]
        niveau = self.style("niveau")
        points = self.__points
        xy = [pt.coordonnees for pt in points]
        x, y = zip(*xy)
        xy.append(self.__points[0].coordonnees)
        fill.xy = xy
        plot.set_data(x, y)
        fill._alpha = self.style("alpha")
        # Following line fails with matplotlib 1.3.1.
        #fill._edgecolor = fill._facecolor = plot._color = self.style("couleur")
        fill.zorder = niveau - 0.01
        plot._linestyle = self.style("style")
        fill._linestyle = FILL_STYLES.get(self.style("style"), "solid")
        plot._linewidth = fill._linewidth = self.style("epaisseur")
        plot.zorder = niveau

    def __repr__(self):
        return "PrevisualisationPolygone(%s)" %repr(self.__points)
