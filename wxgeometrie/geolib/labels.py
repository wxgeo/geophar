# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

##--------------------------------------#######
#                   Labels                    #
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

from weakref import ref
from math import cos, sin, hypot, pi, acos

from .objet import Objet
from .textes import Texte_generique
from .routines import angle_vectoriel
from .. import param


class Label_generique(Texte_generique):
    u"""Un label (étiquette accolée à l'objet)

    Le label est crée automatiquement lors de la création de l'objet.
    Le label n'est pas un 'vrai' objet, il n'est pas enregistré sur la feuille."""

    _style_defaut = param.labels
    # Les coordonnées exactes n'ont aucun intérêt pour une étiquette.
    _utiliser_coordonnees_approchees = True
    _initialisation_minimale = True

    @property
    def __feuille__(self):
        return self.parent.__feuille__

    def __init__(self, parent):
        Texte_generique.__init__(self)
        self._parent = ref(parent)
        # self._parent est une fonction qui renvoit parent si il existe encore.
        # Cela évite de le maintenir en vie artificiellement par une référence circulaire !
        self.suffixe = self.__class__.__name__.split("_", 1)[1]
        self._initialiser_coordonnees()

    def _initialiser_coordonnees(self):
        pass

    @property
    def parent(self):
        return self._parent()

    def _epix2coo(self, x, y):
        u"Conversion des écarts de pixels en écarts de coordonnées."
        return self.__canvas__.coeff(0)*x, self.__canvas__.coeff(1)*y

    def _ecoo2pix(self, x, y):
        u"Conversion des écarts de coordonnées en écarts de pixels."
        return x/self.__canvas__.coeff(0), y/self.__canvas__.coeff(1)

    def _get_coordonnees(self):
        raise NotImplementedError    # sera implemente differemment pour chaque type de label

    def label(self):
        return self.parent.label()

    @property
    def label_temporaire(self):
        return self.parent.label_temporaire

    def _creer_trace(self):
        u"Pas de trace pour les étiquettes."
        pass


    def figure_perimee(self):
        # IMPORTANT:
        # il faut effacer manuellement le cache, car les coordonnées ne sont pas fonction
        # des arguments de l'étiquette.
        # (Pour les autres objets, les arguments sont encapsulés dans des objets Ref
        # qui vident eux-même le cache en cas de modification).
        self._cache.clear()
        Objet.figure_perimee(self)


    @property
    def existe(self):
        # C'est l'existence de l'objet qui détermine celle de son étiquette.
        return self.parent.existe

    def _set_rayon(self, rayon, x, y):
        xmin, xmax, ymin, ymax = self._boite()
        rayon_max = param.distance_max_etiquette + hypot(xmin - xmax, ymin - ymax)/2
        self.style(_rayon_ = min(rayon, rayon_max))
        # TODO: nouvel algorithme:
        # 1. Chercher le point le plus proche parmi les 4 coins du texte.
        # 2. Adapter les coordonnées de ce point pour que la distance ne dépasse pas le maximum autorisé.
        # 3. En déduire les nouvelles coordonnées du point d'ancrage
        # 4. Conclure avec les nouvelles valeur de _rayon_ et _angle_

##    def _distance_boite(self, x, y):
##        xmin, xmax, ymin, ymax = self._boite()
##        d1 = hypot((x-xmin), (y-ymin))
##        d2 = hypot((x-xmax), (y-ymax))
##        d3 = hypot((x-xmin), (y-ymax))
##        d4 = hypot((x-xmax), (y-ymin))
##        return min(d1, d2, d3, d4)

    @property
    def __x(self):
        return self.coordonnees[0]

    x = __x

    @property
    def __y(self):
        return self.coordonnees[1]

    y = __y







class Label_point(Label_generique):
    u"L'étiquette d'un point."

    def _initialiser_coordonnees(self):
        self.style(_angle_ = pi/4) # les noms de style sont entre "_" pour éviter des conflits avec les styles de Texte.
        self.style(_rayon_ = 7) # distance au point en pixels

    def _get_coordonnees(self):
        parent = self.parent
        r = self.style("_rayon_"); a = self.style("_angle_")
        rx, ry = self._epix2coo(r*cos(a), r*sin(a))
        return  parent.abscisse + rx, parent.ordonnee + ry

    def _set_coordonnees(self, x = None, y = None):
        if x is not None:
            parent = self.parent
            rx, ry = self._ecoo2pix(x - parent.abscisse, y - parent.ordonnee)
            rayon = hypot(rx, ry)
            if rayon:
                self.style(_angle_ = acos(rx/rayon)*(cmp(ry, 0) or 1))
            self.style(_rayon_ = min(rayon, 50)) # distance maximale entre le point et son etiquette : 25 pixels




###########################
# NOTE IMPORTANTE:
# Les classes suivantes sont basées sur les classes Glisseur de geolib.
# Si la classe utilise l'objet Glisseur_segment par exemple, elle DOIT s'appeler Label_segment.
# Si la classe utilise l'objet Glisseur_machin, elle DOIT s'appeler Label_machin. Etc.
# (La détection de l'objet à utiliser se fait automatiquement selon le nom de la classe).



class Label_segment(Label_generique):
    u"""L'étiquette d'un segment.

    Attention, la classe ne doit pas être renommée."""
    defaut = 0.5

    def _initialiser_coordonnees(self):
        self.style(_angle_ = pi/4) # les noms de style sont entre "_" pour éviter des conflits avec les styles de Texte.
        self.style(_rayon_ = 7) # distance au point en pixels
        self.style(_k_ = self.defaut) # Sur le segment [AB], l'étiquette sera relative au point fictif M = k*A + (1-k)*B
        self._M = None # il serait assez délicat d'initialiser _M d'office (risque de récursion infinie)...


    def _get_coordonnees(self):
        if self._M is None:
#            import objets
            self._M = locals()["Glisseur_" + self.suffixe](self.parent, k = self.style("_k_"))
        #~ print self._M.coordonnees
        x0, y0 =  self._M.coordonnees
        r = self.style("_rayon_"); a = self.style("_angle_")
        rx, ry = self._epix2coo(r*cos(a), r*sin(a));
        return  x0 + rx, y0 + ry

    def _set_coordonnees(self, x = None, y = None):
        if self._M is None:
#            import objets
            self._M = locals()["Glisseur_" + self.suffixe](self.parent, k = self.style("_k_"))
        if x is not None:
            self._M.coordonnees = (x, y)
            x0, y0 = self._M.coordonnees # comme _M est un glisseur, ce n'est pas x0 et y0 en général
            self.style(_k_ = self._M.parametre)
            rx, ry = self._ecoo2pix(x - x0, y - y0)
            rayon = hypot(rx, ry)
            if rayon:
                self.style(_angle_ = acos(rx/rayon)*(cmp(ry, 0) or 1))
            self.style(_rayon_ = min(rayon, 50)) # distance maximale entre le point et son etiquette : 25 pixels



class Label_vecteur(Label_segment):
    u"""L'étiquette d'un vecteur.

    Attention, la classe ne doit pas être renommée."""



class Label_droite(Label_segment):
    u"""L'étiquette d'une droite.

    Attention, la classe ne doit pas être renommée."""




class Label_demidroite(Label_segment):
    """L'étiquette d'une demi-droite.

    Attention, la classe ne doit pas être renommée."""





class Label_cercle(Label_segment):
    """L'étiquette d'un cercle.

    Attention, la classe ne doit pas être renommée."""
    defaut = 0




class Label_arc_cercle(Label_segment):
    """L'étiquette d'un arc de cercle.

    Attention, la classe ne doit pas être renommée."""


#   Autres classes
#
###########################



class Label_polygone(Label_generique):
    u"L'étiquette d'un polygone."

    def _initialiser_coordonnees(self):
        self.style(_angle_ = pi/4) # les noms de style sont entre "_" pour éviter des conflits avec les styles de Texte.
        self.style(_rayon_ = 7) # distance au point en pixels

    def _set_coordonnees(self, x = None, y = None):
        if x is not None:
            parent = self.parent
            x1, x2, y1, y2 = parent._espace_vital()
            x = max(min(x, x2), x1)
            y = max(min(y, y2), y1)
            rx, ry = self._ecoo2pix(x - parent.centre.abscisse, y - parent.centre.ordonnee)
            rayon = hypot(rx, ry)
            if rayon:
                self.style(_angle_ = acos(rx/rayon)*(cmp(ry, 0) or 1))
            self.style(_rayon_ = rayon) # distance maximale entre le point et son étiquette : 25 pixels


    def _get_coordonnees(self):
        parent = self.parent
        r = self.style("_rayon_"); a = self.style("_angle_")
        rx, ry = self._epix2coo(r*cos(a), r*sin(a))
        return  parent.centre.abscisse + rx, parent.centre.ordonnee + ry






class Label_angle(Label_generique):
    u"L'étiquette d'un angle."

    def _initialiser_coordonnees(self):
        self.style(_k_ = 0.5) # les noms de style sont entre "_" pour éviter des conflits avec les styles de Texte.
        self.style(_rayon_ = param.codage["rayon"] + 10) # distance au point en pixels

    def _get_coordonnees(self):
        parent = self.parent
        r = self.style("_rayon_"); k = self.style("_k_")
        #xx, yy = self.parent.point.position()
        u = self._epix2coo(*parent._Secteur_angulaire__vecteur1)
        v = self._epix2coo(*parent._Secteur_angulaire__vecteur2)
        i = (1, 0)
        a = angle_vectoriel(i, u)
        b = angle_vectoriel(i, v)
        if parent.sens == u"non défini" and parent._sens() < 0:
            a, b = b, a
        if b < a:
            b += 2*pi
        c = k*b + (1 - k)*a
        rx, ry = self._epix2coo(r*cos(c), r*sin(c))
        return  parent._Secteur_angulaire__point.abscisse + rx, parent._Secteur_angulaire__point.ordonnee + ry


    def _set_coordonnees(self, x = None, y = None):
        if x is not None:
            parent = self.parent
            rx, ry = self._ecoo2pix(x - parent.point.abscisse, y - parent.point.ordonnee)
            rayon = hypot(rx, ry)
            if rayon:
                u = self._epix2coo(*parent._Secteur_angulaire__vecteur1)
                v = self._epix2coo(*parent._Secteur_angulaire__vecteur2)
                i = (1, 0)
                a = angle_vectoriel(i, u)
                b = angle_vectoriel(i, v)
                if parent.sens == u"non défini" and parent._sens() < 0:
                    a, b = b, a
                c = angle_vectoriel(i, (rx, ry))
                if a <> b:
                    if b < a:
                        b += 2*pi
                    if c < a:
                        c += 2*pi
                    self.style(_k_ = (c-a)/(b-a))
            self.style(_rayon_ = min(rayon, param.codage["rayon"] + 25))
