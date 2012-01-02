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
from .points import (Glisseur_arc_cercle, Glisseur_segment, Glisseur_droite,
                     Glisseur_vecteur, Glisseur_cercle, Glisseur_demidroite,)
import param


class Label_generique(Texte_generique):
    u"""Un label (�tiquette accol�e � l'objet)

    Le label est cr�e automatiquement lors de la cr�ation de l'objet.
    Le label n'est pas un 'vrai' objet, il n'est pas enregistr� sur la feuille."""

    _style_defaut = param.labels
    # Les coordonn�es exactes n'ont aucun int�r�t pour une �tiquette.
    _utiliser_coordonnees_approchees = True
    _initialisation_minimale = True

    @property
    def __feuille__(self):
        return self.parent.__feuille__

    def __init__(self, parent):
        Texte_generique.__init__(self)
        self._parent = ref(parent)
        # self._parent est une fonction qui renvoit parent si il existe encore.
        # Cela �vite de le maintenir en vie artificiellement par une r�f�rence circulaire !
        self._initialiser_coordonnees()

    def _initialiser_coordonnees(self):
        pass

    @property
    def parent(self):
        return self._parent()

    def _epix2coo(self, x, y):
        u"Conversion des �carts de pixels en �carts de coordonn�es."
        return self.__canvas__.coeff(0)*x, self.__canvas__.coeff(1)*y

    def _ecoo2pix(self, x, y):
        u"Conversion des �carts de coordonn�es en �carts de pixels."
        return x/self.__canvas__.coeff(0), y/self.__canvas__.coeff(1)

    def _get_coordonnees(self):
        raise NotImplementedError    # sera implemente differemment pour chaque type de label

    def label(self):
        return self.parent.label()

    @property
    def label_temporaire(self):
        return self.parent.label_temporaire

    def _creer_trace(self):
        u"Pas de trace pour les �tiquettes."
        pass


    def figure_perimee(self):
        # IMPORTANT:
        # il faut effacer manuellement le cache, car les coordonn�es ne sont pas fonction
        # des arguments de l'�tiquette.
        # (Pour les autres objets, les arguments sont encapsul�s dans des objets Ref
        # qui vident eux-m�me le cache en cas de modification).
        self._cache.clear()
        Objet.figure_perimee(self)


    @property
    def existe(self):
        # C'est l'existence de l'objet qui d�termine celle de son �tiquette.
        return self.parent.existe

    def _set_rayon(self, rayon, x, y):
        xmin, xmax, ymin, ymax = self._boite()
        rayon_max = param.distance_max_etiquette + hypot(xmin - xmax, ymin - ymax)/2
        self.style(_rayon_ = min(rayon, rayon_max))
        # TODO: nouvel algorithme:
        # 1. Chercher le point le plus proche parmi les 4 coins du texte.
        # 2. Adapter les coordonn�es de ce point pour que la distance ne d�passe pas le maximum autoris�.
        # 3. En d�duire les nouvelles coordonn�es du point d'ancrage
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
    u"L'�tiquette d'un point."

    def _initialiser_coordonnees(self):
        self.style(_angle_ = pi/4) # les noms de style sont entre "_" pour �viter des conflits avec les styles de Texte.
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
# Les classes suivantes sont bas�es sur les classes Glisseur de geolib.


class Label_glisseur(Label_generique):
    u"""Classe m�re de tous les labels utilisant un objet glisseur.

    `classe` doit contenir le type de glisseur utilis�.
    """
    defaut = 0.5
    classe = NotImplemented

    def _initialiser_coordonnees(self):
        self.style(_angle_ = pi/4) # les noms de style sont entre "_" pour �viter des conflits avec les styles de Texte.
        self.style(_rayon_ = 7) # distance au point en pixels
        self.style(_k_ = self.defaut) # Sur le segment [AB], l'�tiquette sera relative au point fictif M = k*A + (1-k)*B
        self._M = None # il serait assez d�licat d'initialiser _M d'office (risque de r�cursion infinie)...


    def _get_coordonnees(self):
        if self._M is None:
#            import objets
            self._M = self.classe(self.parent, k = self.style("_k_"))
        #~ print self._M.coordonnees
        x0, y0 =  self._M.coordonnees
        r = self.style("_rayon_"); a = self.style("_angle_")
        rx, ry = self._epix2coo(r*cos(a), r*sin(a));
        return  x0 + rx, y0 + ry

    def _set_coordonnees(self, x = None, y = None):
        if self._M is None:
#            import objets
            self._M = self.classe(self.parent, k = self.style("_k_"))
        if x is not None:
            self._M.coordonnees = (x, y)
            x0, y0 = self._M.coordonnees # comme _M est un glisseur, ce n'est pas x0 et y0 en g�n�ral
            self.style(_k_ = self._M.parametre)
            rx, ry = self._ecoo2pix(x - x0, y - y0)
            rayon = hypot(rx, ry)
            if rayon:
                self.style(_angle_ = acos(rx/rayon)*(cmp(ry, 0) or 1))
            self.style(_rayon_ = min(rayon, 50)) # distance maximale entre le point et son etiquette : 25 pixels



class Label_segment(Label_glisseur):
    u"""L'�tiquette d'un segment."""

    classe = Glisseur_segment



class Label_vecteur(Label_glisseur):
    u"""L'�tiquette d'un vecteur."""

    classe = Glisseur_vecteur


class Label_droite(Label_glisseur):
    u"""L'�tiquette d'une droite."""

    classe = Glisseur_droite


class Label_demidroite(Label_glisseur):
    """L'�tiquette d'une demi-droite."""

    classe = Glisseur_demidroite


class Label_cercle(Label_glisseur):
    """L'�tiquette d'un cercle."""

    defaut = 0
    classe = Glisseur_cercle


class Label_arc_cercle(Label_glisseur):
    """L'�tiquette d'un arc de cercle."""

    classe = Glisseur_arc_cercle


#   Autres classes
#
###########################



class Label_polygone(Label_generique):
    u"L'�tiquette d'un polygone."

    def _initialiser_coordonnees(self):
        self.style(_angle_ = pi/4) # les noms de style sont entre "_" pour �viter des conflits avec les styles de Texte.
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
            self.style(_rayon_ = rayon) # distance maximale entre le point et son �tiquette : 25 pixels


    def _get_coordonnees(self):
        parent = self.parent
        r = self.style("_rayon_"); a = self.style("_angle_")
        rx, ry = self._epix2coo(r*cos(a), r*sin(a))
        return  parent.centre.abscisse + rx, parent.centre.ordonnee + ry






class Label_angle(Label_generique):
    u"L'�tiquette d'un angle."

    def _initialiser_coordonnees(self):
        self.style(_k_ = 0.5) # les noms de style sont entre "_" pour �viter des conflits avec les styles de Texte.
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
        if parent.sens == u"non d�fini" and parent._sens() < 0:
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
                if parent.sens == u"non d�fini" and parent._sens() < 0:
                    a, b = b, a
                c = angle_vectoriel(i, (rx, ry))
                if a <> b:
                    if b < a:
                        b += 2*pi
                    if c < a:
                        c += 2*pi
                    self.style(_k_ = (c-a)/(b-a))
            self.style(_rayon_ = min(rayon, param.codage["rayon"] + 25))
