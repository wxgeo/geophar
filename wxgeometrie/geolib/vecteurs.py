# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                   Vecteurs                    #
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



from lignes import *
##from points import *






# Vecteurs





class Vecteur_generique(Objet_avec_coordonnees):
    u"""Un vecteur générique.

    Usage interne : la classe mère pour les différents vecteurs"""

    _prefixe_nom = "v"

    def __init__(self, **styles):
        #        self.__args = GestionnaireArguments()
        Objet.__init__(self,  **styles)
        # pas besoin de gérer les styles (objet non affiché), mais il vaut mieux que le code soit standardisé...


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


    def _longueur(self):
        return norme(self.x, self.y)

    norme = property(_longueur)

    def __add__(self, y):
        if isinstance(y, Vecteur_generique):
            return Somme_vecteurs([self, y])
        raise TypeError, "vecteur attendu"

    def __sub__(self, y):
        return self + (-y)

    def __mul__(self, y):
        if isinstance(y, Vecteur_generique):
            return Produit_scalaire(self, y)
        else:
            return NotImplemented

    def __rmul__(self, y):
        return Somme_vecteurs([self], [y])

    def __neg__(self, *args):
        return (-1)*self

    def __div__(self, y):
        return (1./y)*self

    def __truediv__(self, y):
        return self.__div__(y)

    def __eq__(self, y):
        if self.existe:
            if  isinstance(y, Vecteur_generique) and y.existe:
                return abs(self.x - y.x) < contexte['tolerance'] and abs(self.y - y.y) < contexte['tolerance']
            elif isinstance(y, (list, tuple, numpy.ndarray)) and len(y) == 2:
                return abs(self.x - y[0]) < contexte['tolerance'] and abs(self.y - y[1]) < contexte['tolerance']
        return False

    def __nonzero__(self):
        return tuple(self.coordonnees) != (0, 0)

    def __ne__(self, y):
        return not (self == y)


    @staticmethod
    def _convertir(objet):
        if hasattr(objet,  "__iter__"):
            a, b = objet
            if isinstance(a, Point_generique):
                return Vecteur(a, b)
            else:
                return Vecteur_libre(a, b)
        raise TypeError, "'" + str(type(objet)) + "' object is not iterable"






class Vecteur(Vecteur_generique):
    u"""Un vecteur.

    Un vecteur défini par deux points."""

    _style_defaut = param.vecteurs
    _affichage_depend_de_la_fenetre = True

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)

    def __new__(cls, *args, **kw):
        if len(args) == 2 and isinstance(args[0], ALL.TYPES_REELS + (ALL.Variable_generique, basestring, )) \
                                   and isinstance(args[1], ALL.TYPES_REELS + (ALL.Variable_generique, basestring, )):
            vecteur_libre = Vecteur_libre.__new__(Vecteur_libre, *args, **kw)
            vecteur_libre.__init__(*args, **kw)
            return vecteur_libre
        return object.__new__(cls)

    def __init__(self, point1 = None, point2 = None, **styles):
#        if point2 is None:
#            point2 = point1
#            point1 = ALL.Point(0, 0)
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        Vecteur_generique.__init__(self, **styles)
        self.etiquette = ALL.Label_vecteur(self)

    @property
    def extremites(self):
        return self.__point1, self.__point2

    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.ligne(), self.rendu.ligne(), self.rendu.ligne()]
        plot1, plot2, plot3 = self._representation
        x1, y1 = self.__point1.coordonnees
        x2, y2 = self.__point2.coordonnees
        A = numpy.array(self.__canvas__.coo2pix(x1, y1))
        B = numpy.array(self.__canvas__.coo2pix(x2, y2))
        k = self.style("position")
        G = k*B + (1-k)*A   # par défaut, k = 1, et la flêche est positionnée à l'extrémité du vecteur (point B)

        #                                                 M
        #                                               C +--        # l'ideal est ici un dessin:   A +---------------+----+ G=B
        #                                                 +--/
        #                                                 N
        # On calcule les coordonnees de C, puis par rotation autour de G, celles de M et N.

        r = self.style("taille")*param.zoom_ligne
        a = self.style("angle")*math.pi/360
        C = G + r*(A - B)/math.hypot(*(A - B)) # prendre B et non G, au cas où G = A !
        M = (numpy.dot([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]], numpy.transpose([C - G])) + numpy.transpose([G]))[:,0]
        N = (numpy.dot([[math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]], numpy.transpose([C - G])) + numpy.transpose([G]))[:,0]
        x, y = self.__canvas__.pix2coo(*array_zip(M, G, N))
        plot1.set_data(numpy.array([x1, x2]), numpy.array([y1, y2]))
        plot2.set_data(numpy.array(x), numpy.array(y))

        if self.style("double_fleche"):
            plot3._visible = True
            G = k*A + (1-k)*B   # par défaut, k = 1, et la flêche est positionnée à l'extrémité du vecteur (point B)

            #                                                 M
            #                                               C +--            # l'ideal est ici un dessin:   B +---------------+----+ G=A
            #                                                 +--/
            #                                                 N
            # On calcule les coordonnees de C, puis par rotation autour de G, celles de M et N.

            r = self.style("taille")*param.zoom_ligne
            a = self.style("angle")*math.pi/360
            C = G + r*(B - A)/math.hypot(*(B - A)) # prendre B et non G, au cas où G = A !
            M = (numpy.dot([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]], numpy.transpose([C - G])) + numpy.transpose([G]))[:,0]
            N = (numpy.dot([[math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]], numpy.transpose([C - G])) + numpy.transpose([G]))[:,0]
            x, y = self.__canvas__.pix2coo(*array_zip(M, G, N))
            plot3.set_data(numpy.array(x), numpy.array(y))
        else:
            plot3._visible = False

        plot1._color = plot2._color = plot3._color = self.style("couleur")
        plot1._linestyle = plot2._linestyle = plot3._linestyle = self.style("style")
        plot1._linewidth = plot2._linewidth = plot3._linewidth = self.style("epaisseur")
        plot1.zorder = plot2.zorder = plot3.zorder = self.style("niveau")


    def _get_coordonnees(self):
        return (self.__point2.x - self.__point1.x,  self.__point2.y - self.__point1.y)



    def _espace_vital(self):
        x1, y1 = self.__point1.coordonnees
        x2, y2 = self.__point2.coordonnees
        return (min(x1, x2), max(x1, x2), min(y1, y2), max(y1, y2))

    def _distance_inf(self, x, y, d):
        # cf. "distance_point_segment.odt" dans "doc/developpeurs/maths/"
        xA, yA = self._pixel(self.__point1)
        xB, yB = self._pixel(self.__point2)
        x1 = min(xA, xB) - d; x2 = max(xA, xB) + d
        y1 = min(yA, yB) - d; y2 = max(yA, yB) + d
        if x1<x<x2 and y1<y<y2:
            norme2 = ((xB-xA)**2+(yB-yA)**2)
            if norme2 > contexte['tolerance']:
                return ((yA-yB)*(x-xA)+(xB-xA)*(y-yA))**2/norme2 < d**2
            else:   # les extrémités du segment sont confondues
                return (x - xA)**2 + (y - yA)**2 < d**2
        else:
            return False

    def _contains(self, M):
        #if not isinstance(M, Point_generique):
        #    return False
        A = self.__point1
        B = self.__point2
        xu, yu = vect(A, B)
        xv, yv = vect(A, M)
        if abs(xu*yv-xv*yu) > contexte['tolerance']:
            return False
        if xu:
            k = xv/xu
        elif yu:
            k = yv/yu
        else:  # A == B
            return M == A
        return 0 <= k <= 1

    @staticmethod
    def _convertir(objet):
        if hasattr(objet,  "__iter__"):
            return Vecteur(*objet)
        raise TypeError, "'" + str(type(objet)) + "' object is not iterable"

    def image_par(self, transformation):
        return Vecteur(self.__point1.image_par(transformation), self.__point2.image_par(transformation))


    def _creer_nom_latex(self):
        u"""Crée le nom formaté en LaTeX. Ex: M1 -> $M_1$."""
        Objet._creer_nom_latex(self)
        nom = "\\vec " + self.nom_latex[1:-1]
        self.nom_latex = "$" + nom + "$"



class Vecteur_libre(Objet_avec_coordonnees_modifiables, Vecteur_generique):
    u"""Un vecteur libre.

    Un vecteur défini par ses coordonnées."""

    abscisse = x = __x = Argument("Variable_generique", defaut = lambda:module_random.normalvariate(0,10))
    ordonnee = y = __y = Argument("Variable_generique", defaut = lambda:module_random.normalvariate(0,10))

    def __init__(self, x = None, y = None, **styles):
        x, y, styles = self._recuperer_x_y(x, y, styles)
        self.__x = x = Ref(x)
        self.__y = y = Ref(y)
        Objet_avec_coordonnees_modifiables.__init__(self, x, y, **styles)
        Vecteur_generique.__init__(self, **styles)


    def _set_feuille(self):
        xmin, xmax, ymin, ymax = self.__feuille__.fenetre
        if "_Vecteur_libre__x" in self._valeurs_par_defaut:
            self.__x.val = module_random.uniform(xmin, xmax)
#            self._valeurs_par_defaut.discard("_Vecteur_libre__x")
        if "_Vecteur_libre__y" in self._valeurs_par_defaut:
            self.__y.val = module_random.uniform(ymin, ymax)
#            self._valeurs_par_defaut.discard("_Vecteur_libre__y")
        Objet._set_feuille(self)



    def _update(self, objet):
        if not isinstance(objet, Vecteur_libre):
            objet = self._convertir(objet)
        if isinstance(objet, Vecteur_libre):
            self.coordonnees = objet.coordonnees
        else:
            raise TypeError, "l'objet n'est pas un vecteur libre."








class Vecteur_unitaire(Vecteur_generique):
    u"""Un vecteur unitaire.

    Un vecteur défini en normalisant un autre vecteur.
    Il aura donc même sens et même direction, mais sera de norme 1."""

    vecteur = __vecteur = Argument("Vecteur_generique", defaut = Vecteur_libre)

    def __init__(self, vecteur = None, **styles):
        self.__vecteur = vecteur = Ref(vecteur)
        Vecteur_generique.__init__(self, **styles)

    def _get_coordonnees(self):
        return (self.__vecteur.abscisse/self.__norme, self.__vecteur.ordonnee/self.__norme)

    def _conditions_existence(self):
        self.__norme = self.__vecteur.norme
        return self.__norme > contexte['tolerance']





class Somme_vecteurs(Vecteur_generique):
    u"""Une somme de vecteurs.

    Les arguments sont des couples coefficient, vecteur
    Exemple: Somme_vecteurs([u,v,A>B], [3,2,-5])."""

    vecteurs = __vecteurs = Arguments("Vecteur_generique")
    coeffs = coefficients = __coefficients = Arguments("Variable_generique")

    def __init__(self, vecteurs, coefficients = None, **styles):

        if coefficients == None:
            coefficients = tuple(1 for vecteur in vecteurs)

        # le code suivant evite de multiplier les sommes de vecteurs imbriquees :
        _coefficients_ = []
        _vecteurs_ = []
        for i in range(len(vecteurs)):
            if isinstance(vecteurs[i], Somme_vecteurs):
                _coefficients_.extend(list(coefficients[i]*k for k in vecteurs[i].coefficients))
                _vecteurs_.extend(vecteurs[i].vecteurs)
            else:
                _coefficients_.append(coefficients[i])
                _vecteurs_.append(vecteurs[i])
        coefficients, vecteurs = _coefficients_, _vecteurs_

        self.__vecteurs = vecteurs = tuple(Ref(obj) for obj in vecteurs)
        self.__coefficients = coefficients = tuple(Ref(obj) for obj in coefficients)
        Vecteur_generique.__init__(self, **styles)


    def _get_coordonnees(self):
        return sum(coeff*vecteur.x for coeff, vecteur in zip(self.__coefficients, self.__vecteurs)), \
                    sum(coeff*vecteur.y for coeff, vecteur in zip(self.__coefficients, self.__vecteurs))




# Le code suivant est erroné (la rotation s'appliquait à l'extrémité du vecteur seulement), et est inutile de toute façon.

#class Vecteur_rotation(Point_rotation, Vecteur_generique): # en pratique, c'est presque un alias de Point_rotation...
#    u"""Une image d'un vecteur par une rotation.
#
#    Vecteur construit à partir d'un autre via une rotation d'angle et de centre donné."""
#
#    def __init__(self, vecteur, rotation, **styles):
#        self.__args = GestionnaireArguments()
#        self.__vecteur = vecteur = Argument(vecteur)
#        self.__rotation = rotation = Argument(rotation)
#        self._initialiser(vecteur = Vecteur_generique, rotation = ALL.Rotation)
#        Point_rotation.__init__(self, point = vecteur, rotation = rotation)
#        #Vecteur_generique.__init__(self, **styles)
#
#
#    def _espace_vital(self):
#        pass
#
#    def _creer_figure(self):  # pour que le vecteur ne soit pas affiché comme point
#        pass





class Extremite(Point_generique):
    u"""L'extrémité d'un représentant de vecteur.abscisse

    L'objet est créé automatiquement lors de la création du représentant."""

    representant = __representant = Argument("Representant")

    def __init__(self, representant, **styles):
        self.__representant = representant = Ref(representant)
        Point_generique.__init__(self, **styles)

    def _get_coordonnees(self):
        return self.__representant._Vecteur__point2.coordonnees

    def _modifier_hierarchie(self, valeur = None):
        # Voir commentaires pour Sommet._modifier_hierarchie dans polygones.py
        Objet._modifier_hierarchie(self, self.__representant._hierarchie + .5)

    def _update(self, objet):
        u"""Pseudo mise à jour: seul un objet identique est accepté.

        Cela sert pour les objets créés automatiquement, qui peuvent être enregistrés deux fois dans la feuille."""
        if isinstance(objet, Extremite) and self.__representant is objet._Extremite__representant:
            self.style(**objet.style())
        else:
            raise RuntimeError


class Representant(Vecteur):
    u"""Un représentant d'un vecteur.

    Un représentant d'un vecteur, ayant pour origine un point donné."""
    vecteur = __vecteur = Argument("Vecteur_generique")
    origine = __origine = Argument("Point_generique", defaut = Point)

    def __init__(self, vecteur, origine = None, **styles):
#        if origine is None:
#            origine = Point(0, 0)
        self.__vecteur = vecteur = Ref(vecteur)
        self.__origine = origine = Ref(origine)
        point2 = Point_final(origine, [vecteur])
        Vecteur.__init__(self, origine, point2, **styles)
        self.extremite = self.__extremite = Extremite(self)
#        self._autres_dependances.append(point2)


    def _set_feuille(self):
        nom = self._style.get("_noms_",  {"extremite": ""})["extremite"]
        self.__feuille__.objets[nom] = self.__extremite


    def __repr__(self, *args, **kwargs):
        self.style(_noms_ = {"extremite": self.__extremite.nom})
        return Objet.__repr__(self, *args, **kwargs)
